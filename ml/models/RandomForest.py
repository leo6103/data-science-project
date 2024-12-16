# import sys
# import os
# import logging
# import numpy as np
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
# from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
# from ml.models.BaseModel import BaseModel
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# logging.basicConfig(level=logging.INFO)
# from ml.utils import prepare_data_chungcu,prepare_data_dat,prepare_data_nharieng


# class RandomForest(BaseModel):
#     def __init__(self, model_name, type, n_estimators=100, max_depth=None, min_samples_split=2, min_samples_leaf=1):
#         """
#         Initialize the Random Forest model with predefined parameters.
#         """
#         super().__init__(model_name)
#         self.n_estimators = n_estimators
#         self.max_depth = max_depth
#         self.min_samples_split = min_samples_split
#         self.min_samples_leaf = min_samples_leaf
#         self.model = RandomForestRegressor(
#             n_estimators=self.n_estimators,
#             max_depth=self.max_depth,
#             min_samples_split=self.min_samples_split,
#             min_samples_leaf=self.min_samples_leaf,
#             random_state=42
#         )
#         self.type = type

#     def process_data(self, df):
#         """
#         Prepares the dataset for LightGBM training.
#         """
#         if self.type =='apartment':
#             X, y = prepare_data_chungcu(df)
#         elif self.type == 'land':
#             X, y = prepare_data_dat(df)
#         elif self.type == 'house':
#             X, y = prepare_data_nharieng(df)
        
#         # Chia dữ liệu thành train và test
#         X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
#         return X_train, X_test, y_train, y_test

#     def calculate_metrics(self, y_actual, y_pred, is_log=False):
#         """
#         Calculate evaluation metrics.
#         """
#         epsilon = 1e-10
#         if is_log:
#             y_actual = np.exp(y_actual - epsilon)
#             y_pred = np.exp(y_pred - epsilon)

#         mse = mean_squared_error(y_actual, y_pred)
#         rmse = np.sqrt(mse)
#         mape = mean_absolute_percentage_error(y_actual, y_pred) * 100
#         return mse, rmse, mape

#     def train(self, X_train, y_train, X_test, y_test, is_log=False):
#         """
#         Train the Random Forest model and tune hyperparameters.
#         """
#         logging.info("Training Random Forest model...")

#         # Cross-Validation
#         logging.info("Performing Cross-Validation...")
#         cv_scores = cross_val_score(self.model, X_train, y_train, cv=5, scoring='neg_mean_squared_error')
#         cv_rmse = np.sqrt(-cv_scores.mean())
#         logging.info(f"Cross-Validation RMSE: {cv_rmse:.4f}")

#         # Grid Search for Hyperparameter Tuning
#         logging.info("Performing Grid Search for hyperparameter tuning...")
#         param_grid = {
#             'n_estimators': [50, 100, 200],
#             'max_depth': [10, 20, None],
#             'min_samples_split': [2, 5, 10],
#             'min_samples_leaf': [1, 2, 4]
#         }
#         grid_search = GridSearchCV(
#             RandomForestRegressor(random_state=42),
#             param_grid,
#             scoring='neg_mean_squared_error',
#             cv=5,
#             verbose=3
#         )
#         grid_search.fit(X_train, y_train)

#         # Set best model
#         best_params = grid_search.best_params_
#         logging.info(f"Best parameters from Grid Search: {best_params}")
#         self.model = grid_search.best_estimator_

#         # Predictions on train and test sets
#         y_train_pred = self.model.predict(X_train)
#         y_test_pred = self.model.predict(X_test)

#         # Calculate metrics for train set
#         train_mse, train_rmse, train_mape = self.calculate_metrics(y_train, y_train_pred, is_log=is_log)
#         logging.info(f" Train MSE: {train_mse:.4f}, Train RMSE: {train_rmse:.4f}, Train MAPE: {train_mape:.2f}%")

#         # Calculate metrics for test set
#         test_mse, test_rmse, test_mape = self.calculate_metrics(y_test, y_test_pred, is_log=is_log)
#         logging.info(f"Test MSE: {test_mse:.4f}, Test RMSE: {test_rmse:.4f}, Test MAPE: {test_mape:.2f}%")

#         logging.info("Training complete!")

#     def predict(self, X):
#         """
#         Predict using the trained model.
#         """
#         if not self.model:
#             raise ValueError("Model is not trained yet.")
#         return self.model.predict(X)

#     def save_model(self):
#         """
#         Save the trained Random Forest model.
#         """
#         import joblib
#         path = f"ml/saved_models/{self.type}/{self.model_name}.txt"
#         os.makedirs(os.path.dirname(path), exist_ok=True)
#         joblib.dump(self.model, path)
#         logging.info(f"Model saved to {path}")

#     def load_model(self):
#         """
#         Load a pre-trained Random Forest model.
#         """
#         import joblib
#         path = f"ml/saved_models/{self.type}/{self.model_name}.txt"
#         if not os.path.exists(path):
#             raise FileNotFoundError(f"Model file not found at: {path}")

#         self.model = joblib.load(path)
#         logging.info(f"Model loaded from {path}")

#     def evaluate(self, X_test, y_test, is_log=False):
#         """
#         Evaluate the trained model on test data.
#         """
#         if not self.model:
#             raise ValueError("Model is not trained yet.")
#         y_pred = self.predict(X_test)
#         _, rmse, mape = self.calculate_metrics(y_test, y_pred, is_log=is_log)
#         logging.info(f"Final RMSE on test: {rmse:.4f}, MAPE on test: {mape:.2f}%")
#         return rmse, mape

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import logging
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.model_selection import RandomizedSearchCV
from skopt import BayesSearchCV  # Bayesian Optimization
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from ml.models.BaseModel import BaseModel
from ml.utils import prepare_data_chungcu,prepare_data_dat,prepare_data_nharieng,prepare_data_predict

logging.basicConfig(level=logging.INFO)


class RandomForest(BaseModel):
    def __init__(self, model_name,type, n_estimators=100, max_depth=None, min_samples_split=2, min_samples_leaf=1):
        """
        Initialize the Random Forest model with predefined parameters.
        """
        super().__init__(model_name)
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.model = RandomForestRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            min_samples_leaf=self.min_samples_leaf,
            random_state=42
        )
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
        # Chia dữ liệu thành train và test
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        return X_train, X_test, y_train, y_test

    def calculate_metrics(self, y_actual, y_pred, is_log=True):
        """
        Calculate evaluation metrics.
        """
        epsilon = 1e-10

        y_actual = np.exp(y_actual - epsilon)
        y_pred = np.exp(y_pred - epsilon)
        sum_abs_percentage_error = 0
        for i in range(len(y_pred)):
            print(f"Giá trị dự đoán: {y_pred[i]:.4f}, Thực tế: {y_actual[i]:.4f}")
            sum_abs_percentage_error += abs((y_actual[i] - y_pred[i]) / y_actual[i])

        mse = mean_squared_error(y_actual, y_pred)
        rmse = np.sqrt(mse)
        mape = (sum_abs_percentage_error / len(y_actual)) * 100
        return mse, rmse, mape

    def random_search_tuning(self, X_train, y_train):
        """
        Perform Random Search for hyperparameter tuning.
        """
        logging.info("Performing Random Search for hyperparameter tuning...")
        param_distributions = {
            'n_estimators': [50, 100, 200, 300],
            'max_depth': [10, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2'],
            'bootstrap': [True, False]
        }
        random_search = RandomizedSearchCV(
            estimator=self.model,
            param_distributions=param_distributions,
            n_iter=50,  # Number of random configurations
            cv=10,  # 10-fold CV
            scoring='neg_mean_squared_error',
            random_state=42,
            verbose=3
        )
        random_search.fit(X_train, y_train)
        logging.info(f"Best parameters from Random Search: {random_search.best_params_}")
        self.model = random_search.best_estimator_

    def bayesian_optimization_tuning(self, X_train, y_train):
        """
        Perform Bayesian Optimization for hyperparameter tuning.
        """
        logging.info("Performing Bayesian Optimization for hyperparameter tuning...")
        search_spaces = {
            'n_estimators': (50, 300),
            'max_depth': (10, 50),
            'min_samples_split': (2, 10),
            'min_samples_leaf': (1, 4),
            'max_features': ['sqrt', 'log2'],
            'bootstrap': [True, False]
        }
        bayes_search = BayesSearchCV(
            estimator=self.model,
            search_spaces=search_spaces,
            n_iter=32,  # Number of iterations
            cv=20,  # 10-fold CV
            scoring='neg_mean_squared_error',
            random_state=42,
            verbose=3
        )
        bayes_search.fit(X_train, y_train)
        logging.info(f"Best parameters from Bayesian Optimization: {bayes_search.best_params_}")
        self.model = bayes_search.best_estimator_

    def train(self, X_train, y_train, X_test, y_test, is_log=False, tuning_method="bayesian"):
        """
        Train the Random Forest model with hyperparameter tuning.
        """
        logging.info("Training Random Forest model...")

        # Cross-Validation with 10 folds
        logging.info("Performing 10-Fold Cross-Validation...")
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=20, scoring='neg_mean_squared_error')
        cv_rmse = np.sqrt(-cv_scores.mean())
        logging.info(f"10-Fold Cross-Validation RMSE: {cv_rmse:.4f}")

        # Hyperparameter Tuning
        if tuning_method == "random_search":
            self.random_search_tuning(X_train, y_train)
        elif tuning_method == "bayesian":
            self.bayesian_optimization_tuning(X_train, y_train)
        else:
            logging.info("No hyperparameter tuning selected.")

        # Predictions on train and test sets
        y_train_pred = self.model.predict(X_train)
        y_test_pred = self.model.predict(X_test)

        # Calculate metrics for train set
        train_mse, train_rmse, train_mape = self.calculate_metrics(y_train, y_train_pred, is_log=is_log)
        logging.info(f" Train MSE: {train_mse:.4f}, Train RMSE: {train_rmse:.4f}, Train MAPE: {train_mape:.2f}%")

        # Calculate metrics for test set
        test_mse, test_rmse, test_mape = self.calculate_metrics(y_test, y_test_pred, is_log=is_log)
        logging.info(f"Test MSE: {test_mse:.4f}, Test RMSE: {test_rmse:.4f}, Test MAPE: {test_mape:.2f}%")

        logging.info("Training complete!")

    def predict(self, X):
        """
        Predict using the trained model.
        :param X: Input data (JSON, dict, or DataFrame)
        :return: Predicted values
        """
        # Kiểm tra xem model đã được load chưa
        if not self.model:
            raise ValueError("Model is not trained or loaded yet.")
        X = prepare_data_predict(X)  
        print(X)
        X = X.to_numpy()
        return self.model.predict(X)

    def save_model(self):
        """
        Save the trained Random Forest model.
        """
        import joblib
        path = f"ml/saved_models/{self.type}/{self.model_name}.txt"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.model, path)
        logging.info(f"Model saved to {path}")

    def load_model(self):
        """
        Load a pre-trained Random Forest model.
        """
        import joblib
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))  # Lấy thư mục hiện tại của file
        path = os.path.join(base_dir, f"ml/saved_models/{self.type}/{self.model_name}.txt")  # Đường dẫn tuyệt đối

        print(f"Trying to load model from path: {path}")  # Log đường dẫn để kiểm tra

        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found at: {path}")

        # Load model
        try:
            self.model = joblib.load(path)
            logging.info(f"Model loaded successfully from {path}")
        except Exception as e:
            logging.error(f"Failed to load model from {path}: {e}")
            raise RuntimeError(f"Failed to load model: {e}")
    def evaluate(self, X_test, y_test, is_log=False):
        """
        Evaluate the trained model on test data.
        """
        if not self.model:
            raise ValueError("Model is not trained yet.")
        y_pred = self.predict(X_test)
        _, rmse, mape = self.calculate_metrics(y_test, y_pred, is_log=is_log)
        logging.info(f"Final RMSE on test: {rmse:.4f}, MAPE on test: {mape:.2f}%")
        return rmse, mape
