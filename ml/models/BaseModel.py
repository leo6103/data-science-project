import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_percentage_error

from ml.utils import read_csv
class BaseModel:
    def __init__(self,model_name):
        self.model = None
        self.model_name  = model_name

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)
        pass

    def load_data(self,path):
        return read_csv(path)
    
    def predict(self):
        pass

    def evaluate(self, X_test, y_test, epsilon=1e-10):
        y_pred_log = self.model.predict(X_test, num_iteration=self.model.best_iteration)
        y_pred = np.exp(y_pred_log) - epsilon
        y_actual = np.exp(y_test) - epsilon

        rmse = np.sqrt(mean_squared_error(y_actual, y_pred))
        mape = mean_absolute_percentage_error(y_actual, y_pred) * 100

        print(f"Final RMSE on test: {rmse}, MAPE on test: {mape}%")

        return rmse, mape

    

    def save_model(self):
        path =  f"ml/saved_models/{self.model_name}.txt"
        self.model.save_model(path)
        print(f"Model saved to {path}")
        pass

    def load_model(self,path):
        pass

