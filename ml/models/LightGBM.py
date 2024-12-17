import sys
import os
import numpy as np
import logging
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error, r2_score
import lightgbm as lgb
import optuna
from ml.models.BaseModel import BaseModel
from ml.utils import prepare_data_chungcu, prepare_data_dat, prepare_data_nharieng

logging.basicConfig(level=logging.INFO)

class LightGBM(BaseModel):
    EVALUATION_INTERVAL = 100
    NUM_ROUND = 10000
    EPSILON = 1e-10

    def __init__(self, model_name, type):
        """
        Initialize the LightGBM model with predefined parameters.
        """
        super().__init__(model_name)
        self.params = {
            'objective': 'regression',
            'metric': 'mse',
            'boosting_type': 'gbdt',
            'learning_rate': 0.001566833145925131,
            'num_leaves': 123,
            'max_depth': 14,
            'feature_fraction': 0.7547624321593347,
            'bagging_fraction': 0.7738857612338457,
            'bagging_freq': 1,
            'lambda_l1': 0.00017969895951366332,
            'lambda_l2': 6.7905143152959075,
            'verbose': -1
        }
        self.model = None
        self.type = type
        
        # Lưu sẵn y_test ở dạng exp(y) - epsilon để không phải tính lại trong callback
        self.y_test_exp = None
        self.X_test = None

    def custom_eval_callback(self, env):
        """
        Custom evaluation callback để giảm chi phí tính toán.
        Chỉ tính toán khi env.iteration % EVALUATION_INTERVAL == 0
        """
        if env.iteration % self.EVALUATION_INTERVAL == 0:
            # Dự đoán ở iteration hiện tại
            y_pred_log = env.model.predict(self.X_test, num_iteration=env.iteration)
            y_pred = np.exp(y_pred_log) - self.EPSILON

            mse = mean_squared_error(self.y_test_exp, y_pred)
            rmse = np.sqrt(mse)
            mape = np.mean(np.abs((self.y_test_exp - y_pred) / (self.y_test_exp + self.EPSILON))) * 100
            r2 = r2_score(self.y_test_exp, y_pred)

            logging.info(f"Iteration {env.iteration}: MSE: {mse}, RMSE: {rmse}, MAPE: {mape}%, R²: {r2}")

    def calculate_metrics(self, y_actual, y_pred, is_log=True):
        """
        Tính toán MSE, RMSE, MAPE, R².
        Nếu is_log=True, y_actual và y_pred được coi là log(price),
        nên ta exp() để quay về giá thực.
        """
        epsilon = self.EPSILON
        if is_log:
            y_actual = np.exp(y_actual - epsilon)
            y_pred = np.exp(y_pred - epsilon)
        mse = mean_squared_error(y_actual, y_pred)
        rmse = np.sqrt(mse)
        mape = np.mean(np.abs((y_actual - y_pred) / (y_actual + epsilon))) * 100
        r2 = r2_score(y_actual, y_pred)
        return mse, rmse, mape, r2

    def process_data(self, df):
        """
        Prepares the dataset for LightGBM training.
        """
        if self.type =='apartment':
            X, y = prepare_data_chungcu(df)
        elif self.type == 'land':
            X, y = prepare_data_dat(df)
        elif self.type == 'house':
            X, y = prepare_data_nharieng(df)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Lưu sẵn dữ liệu test ở dạng exp(y_test) - epsilon để dùng lại trong callback
        self.X_test = X_test
        self.y_test_exp = np.exp(y_test) - self.EPSILON

        train_data = lgb.Dataset(X_train, label=y_train)
        valid_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
        return train_data, valid_data, X_test, y_test

    def lightgbm_optuna_tuning(self, X_train, X_test, y_train, y_test):
        """
        Optimize LightGBM using Optuna.
        """
        logging.info("Performing LightGBM + Optuna Hyperparameter Tuning...")

        def objective(trial):
            epsilon = self.EPSILON
            param = {
                'objective': 'regression',
                'metric': 'mse',
                'boosting_type': 'gbdt',
                'learning_rate': trial.suggest_float('learning_rate', 0.001, 0.1, log=True),
                'num_leaves': trial.suggest_int('num_leaves', 20, 150),
                'max_depth': trial.suggest_int('max_depth', 5, 15),
                'feature_fraction': trial.suggest_float('feature_fraction', 0.6, 1.0),
                'bagging_fraction': trial.suggest_float('bagging_fraction', 0.6, 1.0),
                'bagging_freq': trial.suggest_int('bagging_freq', 1, 5),
                'lambda_l1': trial.suggest_float('lambda_l1', 1e-4, 10.0, log=True),
                'lambda_l2': trial.suggest_float('lambda_l2', 1e-4, 10.0, log=True),
                'min_data_in_leaf': trial.suggest_int('min_data_in_leaf', 10, 100),
                'verbosity': -1
            }

            train_data = lgb.Dataset(X_train, label=y_train)
            valid_data = lgb.Dataset(X_test, label=y_test, reference=train_data)

            model = lgb.train(
                param,
                train_data,
                valid_sets=[train_data, valid_data],
                valid_names=['train', 'valid'],
                num_boost_round=10000,
                callbacks=[
                    lgb.early_stopping(stopping_rounds=100),
                    lgb.log_evaluation(-1)
                ]
            )

            y_pred_log = model.predict(X_test, num_iteration=model.best_iteration)
            y_pred = np.exp(y_pred_log - epsilon)
            y_test_exp = np.exp(y_test) - epsilon
            rmse = np.sqrt(mean_squared_error(y_test_exp, y_pred))
            return rmse

        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=100)
        logging.info(f"Best RMSE: {study.best_value}")
        logging.info(f"Best parameters: {study.best_params}")

        # Update self.params with the best parameters
        self.params.update(study.best_params)
        self.params['objective'] = 'regression'
        self.params['metric'] = 'mse'
        self.params['boosting_type'] = 'gbdt'
        self.params['verbose'] = -1

        logging.info("Parameters updated with Optuna best parameters.")

    def train(self, train_data, valid_data, X_test, y_test, tuning=True):
        # Nếu cần tuning có thể bật lại phần gọi optuna
        # if tuning:
        #     X_train = train_data.data
        #     y_train = train_data.label
        #     X_val = valid_data.data
        #     y_val = valid_data.label
        #     self.lightgbm_optuna_tuning(X_train, X_val, y_train, y_val)

        logging.info("Training LightGBM model with current parameters...")

        # Sử dụng callback dạng lambda để gọi custom_eval_callback, 
        # qua đó tận dụng precomputed X_test, y_test_exp
        self.model = lgb.train(
            params=self.params,
            train_set=train_data,
            num_boost_round=self.NUM_ROUND,
            valid_sets=[train_data, valid_data],
            callbacks=[
                lgb.early_stopping(10000),
                lambda env: self.custom_eval_callback(env)
            ],
        )
        logging.info("Training complete!")

    def evaluate(self, y_actual, y_pred):
        """
        Calculate evaluation metrics.
        """
        epsilon = self.EPSILON
        y_actual = np.exp(y_actual - epsilon)
        y_pred = np.exp(y_pred - epsilon)
        mse = mean_squared_error(y_actual, y_pred)
        rmse = np.sqrt(mse)
        mape = np.mean(np.abs((y_actual - y_pred) / (y_actual + epsilon))) * 100
        r2 = r2_score(y_actual, y_pred)
        return mse, rmse, mape, r2

    def save_model(self):
        """
        Save the trained LightGBM model.
        """
        import joblib
        path = f"ml/saved_models/{self.type}/{self.model_name}.txt"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.model, path)
        logging.info(f"Model saved to {path}")

    def load_model(self):
        """
        Load a pre-trained LightGBM model.
        """
        import joblib
        path = f"ml/saved_models/{self.type}/{self.model_name}.txt"
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found at: {path}")

        self.model = joblib.load(path)
        logging.info(f"Model loaded from {path}")