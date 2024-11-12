
import sys
import os
# Thêm thư mục gốc của dự án vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import pandas as pd
import lightgbm as lgb
import numpy as np
from sklearn.metrics import mean_absolute_percentage_error
# Import các hàm xử lý dữ liệu
from ml.preprocess.batdongsancomvn.chungcu_attribute_handler import normalize_interim_item, normalize_process_item
from ml.preprocess.utils.json_handler import read_json


input_data_path = 'data/input/input.json'

input_data = read_json(input_data_path)

input_data = normalize_interim_item(input_data)
input_data = normalize_process_item(input_data)

epsilon = 1e-10

input_data = pd.DataFrame([input_data])
# print("Columns in input_data:", input_data.columns)
# input_data['log_price'] = np.log(input_data['price'] + epsilon)
input_data['log_area'] = np.log(input_data['area'] + epsilon)
# print("Columns in input_data:", input_data.columns)

# test_data = input_data.drop(columns=['price_square', 'price','furniture','area'])
# print("Input data:",test_data.columns)

input_data = input_data.drop(columns=['price_square', 'price','furniture','area']).values

# Tải lại mô hình đã lưu
loaded_model = lgb.Booster(model_file='lightgbm_model_complex.txt')

y_pred_loaded = loaded_model.predict(input_data, num_iteration=loaded_model.best_iteration)
y_pred_loaded = np.exp(y_pred_loaded)-epsilon
print("Predicted values using the loaded model:")
print(y_pred_loaded)
# print(y_pred_loaded*157)


# kiểm tra dữ liệu test
# Đường dẫn tới file test.json
test_data_path = 'data/input/test.json'

# Đọc dữ liệu từ file JSON
test_data = read_json(test_data_path)

# Nếu `read_json` trả về một dictionary, chuyển nó thành DataFrame
if isinstance(test_data, dict):
    test_data = pd.DataFrame([test_data])
elif isinstance(test_data, list):
    test_data = pd.DataFrame(test_data)

print("Test data columns before dropping duplicates:", test_data.columns)

# Loại bỏ các giá trị trùng lặp dựa trên toàn bộ các cột
test_data = test_data.drop_duplicates()
print("Test data shape after dropping duplicates:", test_data.shape)

# Kiểm tra nếu cột 'area' và 'price' tồn tại trong test_data trước khi thực hiện log transformation
if 'area' in test_data.columns and 'price' in test_data.columns:
    test_data['log_area'] = np.log(test_data['area'] + epsilon)
    test_data['log_price'] = np.log(test_data['price'] + epsilon)
else:
    print("Column 'area' or 'price' not found in test_data. Please check the data source.")
    # Có thể thực hiện xử lý phù hợp ở đây, ví dụ: thêm giá trị mặc định hoặc thoát
    exit()

# Chuẩn bị dữ liệu đầu vào cho mô hình
x_test_data = test_data.drop(columns=['price_square', 'price', 'furniture', 'area', 'log_price']).values
y_test_data = test_data['price'].values  # Giá trị thực tế của cột giá
y_log_price = test_data['log_price'].values  # Giá trị logarit của cột giá

# Dự đoán trên tập test_data với mô hình đã load
y_pred_test = loaded_model.predict(x_test_data, num_iteration=loaded_model.best_iteration)
y_pred_log_price = y_pred_test
y_pred_test = np.exp(y_pred_test) - epsilon  # Chuyển đổi ngược lại từ log(price) về giá trị gốc

print("Predicted values using the loaded model:")
print(y_pred_test)

# Tính toán MAPE dựa trên y_test_data (giá trị thực tế) và y_pred_test (giá trị dự đoán)
mape = mean_absolute_percentage_error(y_test_data, y_pred_test) * 100
mape1 = mean_absolute_percentage_error(y_log_price, y_pred_log_price) * 100
print("Final Mean Absolute Percentage Error (MAPE):", mape, "%")
print("Final Mean Absolute Percentage Error (MAPE) of log price:", mape1, "%")