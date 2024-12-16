# import sys
# import os
# import numpy as np
# import logging
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
# import xgboost as xgb
# from ml.models.BaseModel import BaseModel
# from ml.utils import prepare_data

# logging.basicConfig(level=logging.INFO)

# class XGBoostModel(BaseModel):
#     EVALUATION_INTERVAL = 100
#     NUM_ROUND = 10000
#     EPSILON = 1e-10

#     def __init__(self, model_name):
#         """
#         Initialize the XGBoost model with predefined parameters.
#         """
#         super().__init__(model_name)
#         self.params = {
#         'objective': 'reg:squarederror',  # Hồi quy với sai số bình phương trung bình
#         'eval_metric': 'rmse',
#         'learning_rate': 0.0025,
#         'max_depth': 14,
#         'subsample': 0.944,
#         'colsample_bytree': 0.914,
#         'lambda': 0.918,  # L2 regularization
#         'alpha': 0.072,   # L1 regularization
#         'min_child_weight': 30,
#         'verbosity': 1
#     }
#         self.model = None

#     def custom_eval_callback(self, env, X_test, y_test, epsilon):
#         """
#         Custom evaluation callback to compute additional metrics during training.
#         """
#         if env.iteration % self.EVALUATION_INTERVAL == 0:
#             y_pred_log = self.model.predict(xgb.DMatrix(X_test), ntree_limit=env.iteration)
#             y_pred = np.exp(y_pred_log) - epsilon
#             y_actual = np.exp(y_test) - epsilon

#             mse, rmse, mape = self.calculate_metrics(y_actual, y_pred)
#             logging.info(f"Iteration {env.iteration}: MSE: {mse}, RMSE: {rmse}, MAPE: {mape}%")

#     def calculate_metrics(self, y_actual, y_pred):
#         """
#         Calculate evaluation metrics.
#         """
#         mse = mean_squared_error(y_actual, y_pred)
#         rmse = np.sqrt(mse)
#         mape = mean_absolute_percentage_error(y_actual, y_pred) * 100
#         return mse, rmse, mape

#     def process_data(self, df):
#         """
#         Prepares the dataset for XGBoost training.
#         """
#         X, y = prepare_data(df)
#         X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
#         train_data = xgb.DMatrix(X_train, label=y_train)
#         valid_data = xgb.DMatrix(X_test, label=y_test)
#         return train_data, valid_data, X_test, y_test

#     def train(self, train_data, valid_data, X_test, y_test, epsilon=EPSILON):
#         """
#         Train the XGBoost model with early stopping and custom evaluation.
#         """
#         logging.info("Training XGBoost model...")
#         eval_list = [(train_data, 'train'), (valid_data, 'eval')]
#         self.model = xgb.train(
#             params=self.params,
#             dtrain=train_data,
#             num_boost_round=self.NUM_ROUND,
#             evals=eval_list,
#             early_stopping_rounds=100,
#             verbose_eval=self.EVALUATION_INTERVAL
#         )
            
#         logging.info("Training complete!")

#     def predict(self, X):
#         """
#         Predict using the trained model.
#         """
#         if not self.model:
#             raise ValueError("Model is not loaded or trained yet.")

#         # Sử dụng iteration_range thay vì ntree_limit
#         best_iteration = getattr(self.model, 'best_iteration', None)
#         if best_iteration is not None:
#             y_pred_log = self.model.predict(xgb.DMatrix(X), iteration_range=(0, best_iteration))
#         else:
#             y_pred_log = self.model.predict(xgb.DMatrix(X))
        
#         return np.exp(y_pred_log) - self.EPSILON

#     def load_model(self):
#         """
#         Load a pre-trained XGBoost model.
#         """
#         path = f"ml/saved_models/{self.model_name}.json"
#         if not os.path.exists(path):
#             raise FileNotFoundError(f"Model file not found at: {path}")

#         self.model = xgb.Booster()
#         self.model.load_model(path)
#         logging.info(f"Model loaded from {path}")

#     def save_model(self):
#         """
#         Save the trained XGBoost model.
#         """
#         if not self.model:
#             raise ValueError("Model is not trained yet.")
#         path = f"ml/saved_models/{self.model_name}.pkl"
#         os.makedirs(os.path.dirname(path), exist_ok=True)
#         self.model.save_model(path)
#         logging.info(f"Model saved to {path}")

#     def evaluate(self, X_test, y_test):
#         """
#         Evaluate the trained model on test data.
#         """
#         if not self.model:
#             raise ValueError("Model is not loaded or trained yet.")

#         # Kiểm tra nếu best_iteration tồn tại
#         best_iteration = getattr(self.model, 'best_iteration', None)
#         if best_iteration is not None:
#             y_pred_log = self.model.predict(xgb.DMatrix(X_test), iteration_range=(0, best_iteration))
#         else:
#             y_pred_log = self.model.predict(xgb.DMatrix(X_test))
        
#         # Chuyển đổi log thành giá trị thực
#         y_pred = np.exp(y_pred_log) - self.EPSILON
#         y_actual = np.exp(y_test) - self.EPSILON

#         mse, rmse, mape = self.calculate_metrics(y_actual, y_pred)
#         logging.info(f"Final MSE on test: {mse:.4f}, RMSE on test: {rmse:.4f}, MAPE on test: {mape:.2f}%")
#         return mse, rmse, mape
import sys
import os
import logging
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from ml.models.BaseModel import BaseModel
from ml.utils import prepare_data_chungcu,prepare_data_dat,prepare_data_nharieng
from xgboost import XGBRegressor
from skopt import BayesSearchCV
from skopt.space import Integer, Real, Categorical

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
logging.basicConfig(level=logging.INFO)


class XGBoostModel(BaseModel):
    def __init__(self, model_name, type):
        """
        Khởi tạo mô hình XGBoost với Pipeline bao gồm bước chuẩn hóa.
        """
        super().__init__(model_name)
        self.pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('model', XGBRegressor(
                n_estimators=100, 
                max_depth=6, 
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1,
                tree_method="auto"
            ))
        ])
        self.type = type

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
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        return X_train, X_test, y_train, y_test

    def calculate_metrics(self, y_actual, y_pred, is_log=True):
        """
        Tính toán metric: MSE, RMSE, và MAPE tự tính.
        Nếu giá đã được log-transform, chuyển ngược lại bằng exp().
        """
        epsilon = 1e-10
        if is_log:
            y_actual = np.exp(y_actual - epsilon)
            y_pred = np.exp(y_pred - epsilon)

        mse = mean_squared_error(y_actual, y_pred)
        rmse = np.sqrt(mse)
        # Tự tính MAPE
        mape = np.mean(np.abs((y_actual - y_pred) / (y_actual + epsilon))) * 100

        return mse, rmse, mape

    def bayesian_optimization_tuning(self, X_train, y_train):
        """
        Sử dụng Bayesian Optimization để tối ưu tham số cho XGBoost.
        """
        logging.info("Performing Bayesian Optimization for hyperparameter tuning...")

        search_spaces = {
            'model__n_estimators': Integer(50, 500),
            'model__max_depth': Integer(3, 15),
            'model__learning_rate': Real(1e-3, 0.3, prior='log-uniform'),
            'model__subsample': Real(0.5, 1.0),
            'model__colsample_bytree': Real(0.5, 1.0),
            'model__reg_alpha': Real(1e-5, 10.0, prior='log-uniform'),
            'model__reg_lambda': Real(1e-5, 10.0, prior='log-uniform')
        }

        bayes_search = BayesSearchCV(
            estimator=self.pipeline,
            search_spaces=search_spaces,
            n_iter=30,
            cv=10, 
            scoring='neg_mean_squared_error',
            random_state=42,
            verbose=3,
            n_jobs=-1
        )
        bayes_search.fit(X_train, y_train)
        logging.info(f"Best parameters from Bayesian Optimization: {bayes_search.best_params_}")
        self.pipeline = bayes_search.best_estimator_

    def train(self, X_train, y_train, X_test, y_test, is_log=False, tuning_method="bayesian"):
        """
        Huấn luyện mô hình XGBoost với hyperparameter tuning.
        """
        logging.info("Training XGBoost model...")

        # Đánh giá bằng Cross-Validation (10-fold)
        logging.info("Performing 10-Fold Cross-Validation...")
        cv_scores = cross_val_score(self.pipeline, X_train, y_train, cv=10, scoring='neg_mean_squared_error', n_jobs=-1)
        cv_rmse = np.sqrt(-cv_scores.mean())
        logging.info(f"10-Fold Cross-Validation RMSE: {cv_rmse:.4f}")

        # Tối ưu tham số
        if tuning_method == "bayesian":
            self.bayesian_optimization_tuning(X_train, y_train)
        else:
            logging.info("No hyperparameter tuning selected.")

        # Dự báo trên tập Train và Test sau khi tối ưu
        y_train_pred = self.pipeline.predict(X_train)
        y_test_pred = self.pipeline.predict(X_test)

        # Tính toán metric cho tập Train
        train_mse, train_rmse, train_mape = self.calculate_metrics(y_train, y_train_pred, is_log=is_log)
        logging.info(f" Train MSE: {train_mse:.4f}, Train RMSE: {train_rmse:.4f}, Train MAPE: {train_mape:.2f}%")

        # Tính toán metric cho tập Test
        test_mse, test_rmse, test_mape = self.calculate_metrics(y_test, y_test_pred, is_log=is_log)
        logging.info(f" Test MSE: {test_mse:.4f}, Test RMSE: {test_rmse:.4f}, Test MAPE: {test_mape:.2f}%")

        logging.info("Training complete!")

    def predict(self, X):
        """
        Dự báo với mô hình đã huấn luyện.
        """
        if not self.pipeline:
            raise ValueError("Model is not trained yet.")
        return self.pipeline.predict(X)

    def save_model(self):
        """
        Lưu mô hình đã huấn luyện.
        """
        import joblib
        path = f"ml/saved_models/{self.type}/{self.model_name}.txt"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.pipeline, path)
        logging.info(f"Model saved to {path}")

    def load_model(self):
        """
        Tải mô hình đã lưu.
        """
        import joblib
        path = f"ml/saved_models/{self.type}/{self.model_name}.txt"
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found at: {path}")

        self.pipeline = joblib.load(path)
        logging.info(f"Model loaded from {path}")

    def evaluate(self, X_test, y_test, is_log=False):
        """
        Đánh giá mô hình trên dữ liệu test.
        """
        if not self.pipeline:
            raise ValueError("Model is not trained yet.")
        y_pred = self.predict(X_test)
        _, rmse, mape = self.calculate_metrics(y_test, y_pred, is_log=is_log)
        logging.info(f"Final RMSE on test: {rmse:.4f}, MAPE on test: {mape:.2f}%")
        return rmse, mape