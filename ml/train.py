
import sys
import os
print("Path sys ")
print(sys.path)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ml.models.LightGBM import LightGBM
from ml.models.SVM import SVM
from ml.models.XGBoost import XGBoostModel
from ml.models.RandomForest import RandomForest
from ml.models.LinearRegression import LinearRegressionModel


path = "data/processed/batdongsancomvn/chungcu/preprocess_merged_chungcu.csv"
# path = "data/processed/batdongsancomvn/dat/preprocess_merged_dat.csv"



# linear_regression = LinearRegressionModel("linear_regression", "apartment")
# data = linear_regression.load_data(path)
# X_train, X_test, y_train, y_test = linear_regression.process_data(data)
# linear_regression.train(X_train, y_train, X_test, y_test)
# linear_regression.save_model()
# y_pred = linear_regression.predict(X_test)    
# linear_regression.evaluate(X_test, y_test)

# y_pred = light_gbm.predict(X_test)
# light_gbm.evaluate(X_test, y_test, epsilon=1e-10)

# Train SVM
# svm_model = SVM("svm_model", kernel="rbf", C=1.0, epsilon=0.1)
# svm_model = SVM("svm_model", "apartment")
# data = svm_model.load_data(path)
# X_train, X_test, y_train, y_test = svm_model.process_data(data)
# svm_model.train(X_train, y_train, X_test, y_test)
# svm_model.save_model()
# y_pred = svm_model.predict(X_test)
# svm_model.evaluate(X_test, y_test)

# Train XGBoost
# xgb_model = XGBoostModel("xgb_model")
# data = xgb_model.load_data(path)
# X_train, X_test, y_train, y_test = xgb_model.process_data(data)
# xgb_model.train(X_train, y_train, X_test, y_test)
# xgb_model.save_model()
# y_pred_xgb = xgb_model.predict(X_test)
# xgb_model.evaluate(X_test, y_test)

# Train Random Forest
# rf_model = RandomForest("rf_model","apartment")
# data = rf_model.load_data(path)
# X_train, X_test, y_train, y_test = rf_model.process_data(data)
# rf_model.train(X_train, y_train, X_test, y_test)
# rf_model.save_model()


# y_pred_rf = rf_model.predict(X_test)
# rf_model.evaluate(X_test, y_test) 

light_gbm = LightGBM("light_gbm","apartment")
data  = light_gbm.load_data(path)
train_data, valid_data, X_test, y_test = light_gbm.process_data(data)
light_gbm.train(train_data, valid_data, X_test, y_test)
light_gbm.save_model()