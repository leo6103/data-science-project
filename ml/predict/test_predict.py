import sys
import os
# Thêm thư mục gốc của dự án vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Import các hàm xử lý dữ liệu
from ml.preprocess.batdongsancomvn.attribute_handler.chungcu_attribute_handler import normalize_interim_item, normalize_process_item
from ml.preprocess.utils.json_handler import read_json
from ml.models.RandomForest import RandomForest
from ml.models.LightGBM import LightGBM
from ml.models.SVM import SVM
from ml.utils import prepare_data_predict
from ml.utils import prepare_data

input_data_path = 'data/input/input.json'

# Đọc và xử lý dữ liệu input
input_data = read_json(input_data_path)
input_data = normalize_interim_item(input_data)
input_data = normalize_process_item(input_data)

epsilon = 1e-10



input_data = pd.DataFrame([input_data])

# Chuẩn bị dữ liệu dự đoán từ input
df = input_data
print(input_data)

X, y = prepare_data_predict(df)
print("X ")
print(X)

# Khởi tạo mô hình Random Forest
model = RandomForest("rf_model")
# model = LightGBM("light_gbm")
# model = SVM("svm_model_scaler")

# Load mô hình đã huấn luyện
model.load_model()

# Dự đoán giá trị từ input
y_pred_log = model.predict(X)
print(y_pred_log)
y_pred = np.exp(y_pred_log - epsilon)

print("Giá trị dự đoán (input):", y_pred)
print("Giá trị thực tế (input):", y)

# Chuẩn bị dữ liệu test
test_data_path = 'data/input/test.json'
test_data = read_json(test_data_path)
for i in range(len(test_data)):
    test_data[i] = normalize_interim_item(test_data[i])
    test_data[i] = normalize_process_item(test_data[i])
test_data = [item for item in test_data if item is not None]
test_data = pd.DataFrame(test_data)
# Chuẩn bị dữ liệu
X, y = prepare_data_predict(test_data)
for i in range(len(y)):
    y[i] = np.exp(y[i] - epsilon)

# Dự đoán giá trị trên tập test
y_pred_log = model.predict(X)
y_pred = np.exp(y_pred_log - epsilon)

# In giá trị dự đoán và thực tế
sum_abs_percentage_error = 0
for i in range(len(y_pred)):
    print(f"Giá trị dự đoán: {y_pred[i]:.4f}, Thực tế: {y[i]:.4f}")
    sum_abs_percentage_error += abs((y[i] - y_pred[i]) / y[i])

# Tính MAE
mae = mean_absolute_error(y, y_pred)
print(f"MAE: {mae:.4f}")

# Tính MSE
mse = mean_squared_error(y, y_pred)
print(f"MSE: {mse:.4f}")

# Tính MAPE
mape = (sum_abs_percentage_error / len(y)) * 100
print(f"MAPE: {mape:.2f}%")

