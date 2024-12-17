import sys
import os
import logging
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from ml.models.BaseModel import BaseModel
from ml.utils import prepare_data_chungcu, prepare_data_dat, prepare_data_nharieng

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
logging.basicConfig(level=logging.INFO)

class LinearRegressionModel(BaseModel):
    def __init__(self, model_name, type):
        """
        Khởi tạo mô hình Linear Regression với Pipeline bao gồm bước chuẩn hóa.
        """
        super().__init__(model_name)
        self.pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('model', LinearRegression())
        ])
        self.type = type

    def process_data(self, df):
        """
        Chuẩn bị dữ liệu cho mô hình Linear Regression.
        """
        if self.type == 'apartment':
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
        Tính toán MSE, RMSE, MAPE, R².
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
        r2 = r2_score(y_actual, y_pred)
        return mse, rmse, mape, r2

    def train(self, X_train, y_train, X_test, y_test, is_log=False):
        """
        Huấn luyện mô hình Linear Regression và đánh giá trên tập Train, Test.
        """
        logging.info("Training Linear Regression model...")

        # Đánh giá bằng Cross-Validation (10-fold)
        logging.info("Performing 10-Fold Cross-Validation...")
        cv_scores = cross_val_score(self.pipeline, X_train, y_train, cv=10, scoring='neg_mean_squared_error', n_jobs=-1)
        cv_rmse = np.sqrt(-cv_scores.mean())
        logging.info(f"10-Fold Cross-Validation RMSE: {cv_rmse:.4f}")

        # Huấn luyện mô hình trên toàn bộ tập train
        self.pipeline.fit(X_train, y_train)

        # Dự báo trên tập Train và Test
        y_train_pred = self.pipeline.predict(X_train)
        y_test_pred = self.pipeline.predict(X_test)

        # Calculate metrics for train set
        train_mse, train_rmse, train_mape, r2= self.calculate_metrics(y_train, y_train_pred, is_log=is_log)
        logging.info(f" Train MSE: {train_mse:.4f}, Train RMSE: {train_rmse:.4f}, Train MAPE: {train_mape:.2f}%, Train R²: {r2:.4f}")

        # Calculate metrics for test set
        test_mse, test_rmse, test_mape, r2 = self.calculate_metrics(y_test, y_test_pred, is_log=is_log)
        logging.info(f"Test MSE: {test_mse:.4f}, Test RMSE: {test_rmse:.4f}, Test MAPE: {test_mape:.2f}%, Test R²: {r2:.4f}")

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
        mse, rmse, mape,r2 = self.calculate_metrics(y_test, y_pred, is_log=is_log)
        logging.info(f"Final MSE on test:{mse}, RMSE on test:{rmse:.4f}, MAPE on test: {mape:.2f}%", f"R² on test: {r2:.4f}")
        return rmse, mape