import numpy as np
import pandas as pd
import sys
import os
# Thêm thư mục gốc của dự án vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from sklearn.linear_model import LinearRegression

# Đọc dữ liệu
path_csv_data = 'data/processed/batdongsancomvn/chungcu/processed_merged_chungcu.csv'

try:
    print("Start reading file...")
    df = pd.read_csv(path_csv_data)
    df = df.astype(np.float32)
except FileNotFoundError:
    print(f"Error: File '{path_csv_data}' không tồn tại.")
except pd.errors.EmptyDataError:
    print(f"Error: File '{path_csv_data}' không chứa dữ liệu.")
except pd.errors.ParserError:
    print(f"Error: File '{path_csv_data}' không đúng định dạng CSV.")
except Exception as e:
    print(f"Đã xảy ra lỗi: {e}")

# Xử lý ngoại lai cho cột `price_square` bằng Z-score
df['z_score'] = np.abs(stats.zscore(df['price_square']))
df = df[df['z_score'] <= 3]  # Loại bỏ các điểm có Z-score lớn hơn 3
df = df.drop(columns=['z_score'])
print("Số lượng mẫu sau khi lọc ngoại lai:", len(df))

# # Lọc bỏ các dòng có giá trị `area` lớn hơn 200
# df = df[df['area'] <= 200]
# print("Số lượng mẫu sau khi lọc:", len(df))

# Biến đổi logarit cho cột diện tích để làm giảm độ phân tán
epsilon = 1e-10
df['log_area'] = np.log(df['area'] + epsilon)

# Tách cột đầu vào (X) và đầu ra (y)
X = df.drop(columns=['price_square', 'price', 'furniture', 'area']).values
y = df['price_square'].values

# Chia dữ liệu thành tập huấn luyện và tập kiểm tra
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Khởi tạo mô hình Multiple Linear Regression
model = LinearRegression()

# Huấn luyện mô hình
print("Training Multiple Linear Regression model...")
model.fit(X_train, y_train)

# Dự đoán trên tập kiểm tra
y_pred = model.predict(X_test)

# Đánh giá mô hình
def call_eval(y_true, y_pred):
    mse = mean_squared_error(y_true, y_pred)
    print("Mean Squared Error (MSE):", mse)
    rmse = np.sqrt(mse)
    print("Root Mean Squared Error (RMSE):", rmse)
    mean_actual = np.mean(y_true)
    percentage_error = (rmse / mean_actual) * 100
    print("Percentage Error của RMSE:", percentage_error, "%")
    mape = mean_absolute_percentage_error(y_true, y_pred) * 100
    print("Mean Absolute Percentage Error (MAPE):", mape, "%")

call_eval(y_test, y_pred)

# In kết quả dự đoán mẫu
print("Dự đoán mẫu:")
print(y_pred[:5], y_test[:5])