import sys
import os
import numpy as np
import logging
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
import lightgbm as lgb
import optuna
from ml.models.BaseModel import BaseModel
from ml.utils import prepare_data

logging.basicConfig(level=logging.INFO)

class LightGBM(BaseModel):
    EVALUATION_INTERVAL = 100
    NUM_ROUND = 5000
    EPSILON = 1e-10

    def __init__(self, model_name):
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

    def custom_eval_callback(self, env, X_test, y_test, epsilon):
        """
        Custom evaluation callback to compute additional metrics during training.
        """
        if env.iteration % self.EVALUATION_INTERVAL == 0:
            y_pred_log = env.model.predict(X_test, num_iteration=env.iteration)
            y_pred = np.exp(y_pred_log) - epsilon
            y_actual = np.exp(y_test) - epsilon

            mse, rmse, mape = self.calculate_metrics(y_actual, y_pred)
            logging.info(f"Iteration {env.iteration}: MSE: {mse}, RMSE: {rmse}, MAPE: {mape}%")

    def calculate_metrics(self, y_actual, y_pred):
        """
        Calculate evaluation metrics.
        """
        epsilon = 1e-10
        mse = mean_squared_error(y_actual, y_pred)
        rmse = np.sqrt(mse)
        mape = np.mean(np.abs((y_actual - y_pred) / (y_actual + epsilon))) * 100
        return mse, rmse, mape

    def process_data(self, df):
        """
        Prepares the dataset for LightGBM training.
        """
        X, y = prepare_data(df)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        train_data = lgb.Dataset(X_train, label=y_train)
        valid_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
        return train_data, valid_data, X_test, y_test

    def lightgbm_optuna_tuning(self, X_train, X_test, y_train, y_test):
        """
        Optimize LightGBM using Optuna and print results.
        After tuning, update self.params with the best found parameters.
        """
        logging.info("Performing LightGBM + Optuna Hyperparameter Tuning...")

        def objective(trial):
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

            y_pred = model.predict(X_test, num_iteration=model.best_iteration)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            return rmse

        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=50)
        logging.info(f"Best RMSE: {study.best_value}")
        logging.info(f"Best parameters: {study.best_params}")

        # Update self.params with the best parameters
        self.params.update(study.best_params)
        # Ensure essential params are still set correctly
        self.params['objective'] = 'regression'
        self.params['metric'] = 'mse'
        self.params['boosting_type'] = 'gbdt'
        self.params['verbose'] = -1

        logging.info("Parameters updated with Optuna best parameters.")

    def train(self, train_data, valid_data, X_test, y_test,tuning = True):


        # Nếu cần tuning, gọi lightgbm_optuna_tuning trước
        if tuning:
            # Lấy dữ liệu từ train_data và valid_data
            # Vì train_data, valid_data là Dataset của LightGBM, ta cần trích xuất ra cho tuning
            X_train = train_data.data
            y_train = train_data.label
            X_val = valid_data.data
            y_val = valid_data.label

            # Tối ưu tham số bằng Optuna
            self.lightgbm_optuna_tuning(X_train, X_val, y_train, y_val)

        # Sau khi có params tốt nhất (nếu tuning=True), tiến hành train mô hình
        logging.info("Training LightGBM model with current parameters...")
        self.model = lgb.train(
            params=self.params,
            train_set=train_data,
            num_boost_round=self.NUM_ROUND,
            valid_sets=[train_data, valid_data],
            callbacks=[
                lgb.early_stopping(10000),
                lambda env: self.custom_eval_callback(env, X_test, y_test, epsilon=1e-10),
            ],
        )
        logging.info("Training complete!")