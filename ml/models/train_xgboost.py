import numpy as np
import pandas as pd
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
import xgboost as xgb

# Đọc dữ liệu
# df = pd.read_csv('your_file.csv')  # Giả sử bạn đã tải dữ liệu vào DataFrame df

path_csv_data = 'data/processed/batdongsancomvn/chungcu/processed_merged_chungcu.csv'

try:
    print("Start reading file...")
    # Đọc file CSV vào DataFrame
    df = pd.read_csv(path_csv_data)
    df = df.astype(np.float32)  # Đảm bảo dữ liệu có định dạng float32 phù hợp với PyTorch

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

# Lọc bỏ các dòng có giá trị `area` lớn hơn 200
df = df[df['area'] <= 200]
print("Số lượng mẫu sau khi lọc:", len(df))

# Biến đổi logarit cho cột diện tích để làm giảm độ phân tán
epsilon = 1e-10
df['log_price'] = np.log(df['price'] + epsilon)
df['log_area'] = np.log(df['area'] + epsilon)

# Tách cột đầu vào (X) và đầu ra (y)
X = df.drop(columns=['price_square', 'price','furniture','area','log_price']).values
y = df['log_price'].values

# Chia dữ liệu thành tập huấn luyện và tập kiểm tra
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Chuyển đổi dữ liệu thành DMatrix
dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test, label=y_test)

# Thiết lập các tham số cho XGBoost
params = {
    'objective': 'reg:squarederror',
    'learning_rate': 0.06397098893169026,
    'max_depth': 12,
    'min_child_weight': 1,
    'subsample': 0.8592442627575188,
    'colsample_bytree': 0.9634909953761346,
    'lambda': 0.023579248032190175,
    'alpha': 0.00129044401202566,
    'eval_metric': 'rmse'
}

# số vòng lặp huấn luyện
num_boost_round = 1000
evaluation_interval = 100

# Huấn luyện mô hình với early stopping và verbose_eval để hiển thị đánh giá sau mỗi 100 vòng lặp
evals = [(dtrain, 'train'), (dtest, 'eval')]

# Huấn luyện mô hình XGBoost với early stopping
model = xgb.train(
    params=params,
    dtrain=dtrain,
    num_boost_round=num_boost_round,
    evals=evals,
    early_stopping_rounds=1000,
    verbose_eval=evaluation_interval
)

# Dự đoán trên tập kiểm tra với số vòng lặp tốt nhất
y_pred = model.predict(dtest)
# Tính toán và in các chỉ số đánh giá
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
print(f"Final Mean Squared Error (MSE): {mse}")
print(f"Final Root Mean Squared Error (RMSE): {rmse}")

# Tính Percentage Error của RMSE so với giá trị trung bình thực tế
mean_actual = np.mean(y_test)
percentage_error = (rmse / mean_actual) * 100
print("Final Percentage Error của RMSE:", percentage_error, "%")

# Tính MAPE
mape = mean_absolute_percentage_error(y_test, y_pred) * 100
print("Final Mean Absolute Percentage Error (MAPE):", mape, "%")

# In kết quả dự đoán mẫu
print("Dự đoán mẫu:")
print(y_pred[:5], y_test[:5])