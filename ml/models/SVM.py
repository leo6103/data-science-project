# import sys
# import os
# import logging
# import numpy as np
# from sklearn.svm import SVR
# from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
# from sklearn.preprocessing import StandardScaler
# from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
# from ml.models.BaseModel import BaseModel
# from ml.utils import prepare_data

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# logging.basicConfig(level=logging.INFO)


# class SVM(BaseModel):
#     def __init__(self, model_name, kernel='rbf', C=1.0, gamma='scale', epsilon=0.1):
#         """
#         Initialize the SVM model with predefined parameters.
#         """
#         super().__init__(model_name)
#         self.kernel = kernel
#         self.C = C
#         self.gamma = gamma
#         self.epsilon = epsilon
#         self.scaler = StandardScaler()  # Chuẩn hóa dữ liệu
#         self.model = SVR(kernel=self.kernel, C=self.C, gamma=self.gamma, epsilon=self.epsilon)

#     def process_data(self, df):
#         """
#         Prepares the dataset for SVM training.
#         """
#         X, y = prepare_data(df)
        
#         # Chia dữ liệu thành train và test
#         X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
#         # Chuẩn hóa dữ liệu
#         X_train = self.scaler.fit_transform(X_train)
#         X_test = self.scaler.transform(X_test)
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
#         Train the SVM model and tune hyperparameters.
#         """
#         logging.info("Training SVM model...")

#         # Cross-Validation
#         logging.info("Performing Cross-Validation...")
#         cv_scores = cross_val_score(self.model, X_train, y_train, cv=10, scoring='neg_mean_squared_error')
#         cv_rmse = np.sqrt(-cv_scores.mean())
#         logging.info(f"Cross-Validation RMSE: {cv_rmse:.4f}")

#         # Grid Search for Hyperparameter Tuning
#         logging.info("Performing Grid Search for hyperparameter tuning...")
#         param_grid = {
#             'C': [10, 100],
#             'gamma': [0.1, 0.01, 0.001],
#             'epsilon': [0.1, 0.01, 0.001]
#         }
#         grid_search = GridSearchCV(SVR(kernel='rbf'), param_grid, scoring='neg_mean_squared_error', cv=5, verbose=3)
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
#         X_scaled = self.scaler.transform(X)
#         return self.model.predict(X_scaled)

#     def save_model(self):
#         """
#         Save the trained SVM model and scaler.
#         """
#         import joblib
#         model_path = f"ml/saved_models/{self.model_name}.pkl"
#         scaler_path = f"ml/saved_models/{self.model_name}_scaler.pkl"
#         os.makedirs(os.path.dirname(model_path), exist_ok=True)
#         joblib.dump(self.model, model_path)
#         joblib.dump(self.scaler, scaler_path)
#         logging.info(f"Model and scaler saved to {model_path} and {scaler_path}")

#     def load_model(self):
#         """
#         Load a pre-trained SVM model and scaler.
#         """
#         import joblib
#         model_path = f"ml/saved_models/{self.model_name}.pkl"
#         scaler_path = f"ml/saved_models/{self.model_name}_scaler.pkl"
#         if not os.path.exists(model_path) or not os.path.exists(scaler_path):
#             raise FileNotFoundError(f"Model or scaler file not found at: {model_path} or {scaler_path}")

#         self.model = joblib.load(model_path)
#         self.scaler = joblib.load(scaler_path)
#         logging.info(f"Model and scaler loaded from {model_path} and {scaler_path}")

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
import logging
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.metrics import mean_squared_error
from sklearn.svm import SVR
from ml.models.BaseModel import BaseModel
from ml.utils import prepare_data
from skopt import BayesSearchCV
from skopt.space import Integer, Real, Categorical

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
logging.basicConfig(level=logging.INFO)


class OptionalPCA:
    """
    Một transformer cho phép bật/tắt PCA thông qua n_components.
    Nếu n_components=0: không PCA, dữ liệu giữ nguyên.
    Nếu n_components>0: áp dụng PCA.
    """
    def __init__(self, n_components=0):
        self.n_components = n_components
        self.pca = None

    def fit(self, X, y=None):
        if self.n_components > 0:
            from sklearn.decomposition import PCA
            self.pca = PCA(n_components=self.n_components, random_state=42)
            self.pca.fit(X)
        return self

    def transform(self, X):
        if self.n_components > 0:
            return self.pca.transform(X)
        return X

    def fit_transform(self, X, y=None):
        self.fit(X, y)
        return self.transform(X)
    
    def get_params(self, deep=True):
        return {'n_components': self.n_components}
    
    def set_params(self, **params):
        for key, value in params.items():
            setattr(self, key, value)
        return self


class SVM(BaseModel):
    def __init__(self, model_name):
        """
        Khởi tạo mô hình SVR với Pipeline linh hoạt:
        - PolynomialFeatures
        - StandardScaler
        - OptionalPCA
        - SVR (SVM Regression)
        """
        super().__init__(model_name)
        self.pipeline = Pipeline([
            ('poly', PolynomialFeatures(include_bias=False)),
            ('scaler', StandardScaler()),
            ('pca', OptionalPCA(n_components=0)),
            ('model', SVR(kernel='rbf', C=1.0, epsilon=0.1, gamma='scale'))
        ])

    def process_data(self, df):
        """
        Tiền xử lý dữ liệu:
        Gọi prepare_data(df) lấy X, y.
        Người dùng có thể bổ sung bước feature engineering khác ở đây.
        """
        X, y = prepare_data(df)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        return X_train, X_test, y_train, y_test

    def calculate_metrics(self, y_actual, y_pred, is_log=True):
        """
        Tính toán MSE, RMSE, MAPE.
        Nếu is_log=True, y_actual và y_pred được coi là log(price),
        nên ta exp() để quay về giá thực.
        """
        epsilon = 1e-10
        if is_log:
            y_actual = np.exp(y_actual - epsilon)
            y_pred = np.exp(y_pred - epsilon)

        mse = mean_squared_error(y_actual, y_pred)
        rmse = np.sqrt(mse)
        mape = np.mean(np.abs((y_actual - y_pred) / (y_actual + epsilon))) * 100
        return mse, rmse, mape

    def bayesian_optimization_tuning(self, X_train, y_train):
        """
        Tối ưu tham số mô hình bằng Bayesian Optimization.
        Không gian tham số rộng, tối ưu cả bước mở rộng đa thức, PCA, và các tham số SVM.
        """
        logging.info("Performing Bayesian Optimization for hyperparameter tuning...")

        # Không gian tham số:
        # poly__degree: bậc đa thức (1 nghĩa là không mở rộng)
        # pca__n_components: 0 nghĩa là không PCA, >0 giảm chiều.
        # model__kernel: chọn kernel (linear, rbf, poly)
        # model__C, model__epsilon, model__gamma: tham số của SVR
        # model__degree: bậc cho kernel 'poly' (nếu kernel=poly)
        
        search_spaces = {
            'poly__degree': Integer(1, 3),
            'pca__n_components': Integer(0, 10),
            'model__kernel': Categorical(['linear', 'rbf', 'poly']),
            'model__C': Real(1e-3, 1e3, prior='log-uniform'),
            'model__epsilon': Real(1e-3, 1, prior='log-uniform'),
            'model__gamma': Real(1e-4, 1e-1, prior='log-uniform'),
            'model__degree': Integer(1, 3), # Chỉ ảnh hưởng nếu kernel='poly'
        }

        # Sử dụng 10-fold CV, scoring bằng neg_mean_squared_error
        bayes_search = BayesSearchCV(
            estimator=self.pipeline,
            search_spaces=search_spaces,
            n_iter=50,            # Số vòng lặp tuning, tăng lên nếu muốn tìm kiếm kỹ hơn
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
        Huấn luyện mô hình SVR với hyperparameter tuning.
        """
        logging.info("Training SVR model...")

        # Đánh giá mô hình ban đầu bằng 10-Fold CV
        logging.info("Performing 10-Fold Cross-Validation before tuning...")
        cv_scores = cross_val_score(self.pipeline, X_train, y_train, cv=10, scoring='neg_mean_squared_error', n_jobs=-1)
        cv_rmse = np.sqrt(-cv_scores.mean())
        logging.info(f"Initial 10-Fold Cross-Validation RMSE: {cv_rmse:.4f}")

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
        logging.info(f"Train MSE: {train_mse:.4f}, Train RMSE: {train_rmse:.4f}, Train MAPE: {train_mape:.2f}%")

        # Tính toán metric cho tập Test
        test_mse, test_rmse, test_mape = self.calculate_metrics(y_test, y_test_pred, is_log=is_log)
        logging.info(f"Test MSE: {test_mse:.4f}, Test RMSE: {test_rmse:.4f}, Test MAPE: {test_mape:.2f}%")

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
        path = f"ml/saved_models/{self.model_name}.pkl"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.pipeline, path)
        logging.info(f"Model saved to {path}")

    def load_model(self):
        """
        Tải mô hình đã lưu.
        """
        import joblib
        path = f"ml/saved_models/{self.model_name}.pkl"
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
        y_pred = self.pipeline.predict(X_test)
        _, rmse, mape = self.calculate_metrics(y_test, y_pred, is_log=is_log)
        logging.info(f"Final RMSE on test: {rmse:.4f}, MAPE on test: {mape:.2f}%")
        return rmse, mape