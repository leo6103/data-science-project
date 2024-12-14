import xgboost as xgb
import lightgbm as lgb
import pandas as pd
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import StackingRegressor
from sklearn.linear_model import LinearRegression
import numpy as np

# Đường dẫn tới file CSV
path_csv_data = 'data/processed/batdongsancomvn/chungcu/processed_merged_chungcu.csv'

# Đọc dữ liệu và xử lý ngoại lệ
try:
    print("Start reading file...")
    df = pd.read_csv(path_csv_data).astype(np.float32)
except FileNotFoundError:
    print(f"Error: File '{path_csv_data}' không tồn tại.")
    exit()
except (pd.errors.EmptyDataError, pd.errors.ParserError) as e:
    print(f"Error with file '{path_csv_data}': {e}")
    exit()

# Loại bỏ ngoại lệ theo Z-score
df = df[(np.abs(stats.zscore(df['price'])) <= 3)]
print("Số lượng mẫu sau khi lọc ngoại lai:", len(df))

# Thêm epsilon nhỏ và lấy log cho cột giá và diện tích
epsilon = 1e-10
df['log_price'] = np.log(df['price'] + 1)
df['log_area'] = np.log(df['area'] + 1)

# Chuẩn hóa các cột liên tục
scaler = StandardScaler()
df[['log_area', 'log_price', 'latitude', 'longitude']] = scaler.fit_transform(df[['log_area', 'log_price', 'latitude', 'longitude']])

# One-hot Encoding cho các cột phân loại
df = pd.get_dummies(df, columns=['legal_status', 'furniture'], drop_first=True)

# Chuẩn bị dữ liệu
X = df.drop(columns=['price', 'area', 'log_price']).values
y = df['log_price'].values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Khởi tạo và thiết lập tham số cho XGBoost và LightGBM
params_xgb = {
    'objective': 'reg:squarederror',
    'learning_rate': 0.01,
    'max_depth': 13,
    'n_estimators': 1000,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'random_state': 42
}

params_lgb = {
    'objective': 'regression',
    'metric': 'rmse',
    'learning_rate': 0.01,
    'max_depth': 13,
    'n_estimators': 1000,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'random_state': 42
}

# Khởi tạo mô hình XGBoost và LightGBM
xgboost_model = xgb.XGBRegressor(**params_xgb)
lightgbm_model = lgb.LGBMRegressor(**params_lgb)

# Tạo mô hình Stacking
stacking_model = StackingRegressor(
    estimators=[('xgb', xgboost_model), ('lgb', lightgbm_model)],
    final_estimator=LinearRegression()
)

# Huấn luyện mô hình Stacking
print("Training Stacking model with XGBoost and LightGBM...")
stacking_model.fit(X_train, y_train)

# Đánh giá mô hình trên tập kiểm tra
y_pred_log = stacking_model.predict(X_test)
y_pred = np.exp(y_pred_log)  # Chuyển từ log_price về giá gốc
y_test_actual = np.exp(y_test)  # Chuyển từ log_price về giá gốc

# Tính toán RMSE và MAPE
rmse = np.sqrt(mean_squared_error(y_test_actual, y_pred))
mape = mean_absolute_percentage_error(y_test_actual, y_pred) * 100
print(f"Final RMSE on test: {rmse}, MAPE on test: {mape}%")

# In dự đoán mẫu so với giá trị thực tế
comparison_df = pd.DataFrame({
    'Predicted': y_pred[:5],
    'Actual': y_test_actual[:5]
})
print("Sample predictions vs actual values:")
print(comparison_df)