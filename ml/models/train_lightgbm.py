import lightgbm as lgb
import pandas as pd
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from lightgbm import early_stopping, log_evaluation
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import KFold
from sklearn.metrics import mean_absolute_percentage_error
from imblearn.over_sampling import SMOTE



import numpy as np

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
# Giả sử `df` là DataFrame chứa các cột `longitude`, `latitude`, `price_square`, và `price`
# Chuyển đổi latitude và longitude sang radian
# df['latitude_rad'] = np.radians(df['latitude'])
# df['longitude_rad'] = np.radians(df['longitude'])
#
# # Tính toán tọa độ vuông góc x, y, z
# df['x'] = np.cos(df['latitude_rad']) * np.cos(df['longitude_rad'])
# df['y'] = np.cos(df['latitude_rad']) * np.sin(df['longitude_rad'])
# df['z'] = np.sin(df['latitude_rad'])

# # Loại bỏ các cột gốc không cần thiết
# df = df.drop(columns=['latitude', 'longitude', 'latitude_rad', 'longitude_rad'])
#
# # Cập nhật lại `data` sau khi chuyển đổi
# data = df.to_dict(orient="records")

# print(data)

add_data_path = 'data/processed/batdongsancomvn/chungcu/additional_data.json'
add_data = pd.read_json(add_data_path)
add_data = add_data.astype(np.float32)

add_data = pd.DataFrame(add_data)
add_data = add_data.drop_duplicates()

print("Số lượng mẫu add data :", len(add_data))
print(len(add_data))

df = pd.concat([df, add_data], ignore_index=True)
# Giả sử 'column' là cột mà bạn muốn loại bỏ ngoại lai
print("Số lượng mẫu trước khi lọc:", len(df))

# Loại bỏ các điểm có Z-score lớn hơn 3 ( xử lí ngoại lai)
df['z_score'] = np.abs(stats.zscore(df['price_square']))
df = df[df['z_score'] <= 3]
df = df.drop(columns=['z_score'])
print("Số lượng mẫu sau khi lọc ngoại lai:", len(df))


# Lọc bỏ các dòng có giá trị area lớn hơn 200
# df = df[df['area'] <= 200]
# print("Số lượng mẫu sau khi lọc:", len(df))

# Biến đổi logarit cho cột giá và diẹn tích
epsilon = 1e-10
df['log_price'] = np.log(df['price'] + epsilon)
df['log_area'] = np.log(df['area'] + epsilon)


# Chia dữ liệu thành các cột đầu vào (X) và đầu ra (y)
X = df.drop(columns=['price_square', 'price','furniture','area','log_price']).values
y = df['log_price'].values

# Chia dữ liệu thành tập huấn luyện và tập kiểm tra
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

# Chuyển đổi dữ liệu thành định dạng Dataset của LightGBM
train_data = lgb.Dataset(X_train, label=y_train)
valid_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
# Thiết lập các tham số tăng độ phức tạp cho mô hình LightGBM
# params = {
#     'objective': 'regression',
#     'metric': 'mse',
#     'boosting_type': 'gbdt',
#     'learning_rate': 0.00005,            # Giảm learning rate
#     'num_leaves': 64,                 # Tăng số lượng lá
#     'max_depth': 10,                  # Tăng độ sâu của cây
#     'feature_fraction': 1.0,          # Sử dụng toàn bộ các đặc trưng
#     'bagging_fraction': 0.9,          # Tăng tỷ lệ lấy mẫu dữ liệu
#     'bagging_freq': 1,                # Sử dụng bagging thường xuyên hơn
#     'verbose': -1
# }
# params = {
#     'objective': 'regression',
#     'metric': 'mse',
#     'boosting_type': 'gbdt',
#     'learning_rate': 0.07344563864614025,
#     'num_leaves': 137,
#     'max_depth': 12,
#     'feature_fraction': 0.9619720932813092,
#     'bagging_fraction': 0.6886977902886937,
#     'bagging_freq': 4,
#     'lambda_l1': 0.004726611625011041,
#     'lambda_l2': 0.1296782309409407,
#     'verbose': -1
# }

params = {
    'objective': 'regression',
    'metric': 'mse',
    'boosting_type': 'gbdt',
    'learning_rate': 0.01566833145925131,
    'num_leaves': 123,
    'max_depth': 14,
    'feature_fraction': 0.7547624321593347,
    'bagging_fraction': 0.7738857612338457,
    'bagging_freq': 1,
    'lambda_l1': 0.00017969895951366332,
    'lambda_l2': 6.7905143152959075,
    'verbose': -1
}

# số vòng lặp huấn luyện
num_boost_round = 10000
evaluation_interval = 100


# Callback tùy chỉnh để đánh giá mô hình sau mỗi 100 vòng lặp
def custom_eval_callback(env):
    if env.iteration % evaluation_interval == 0:
        # Dự đoán trên tập kiểm tra với số vòng lặp hiện tại
        y_pred_log = env.model.predict(X_test, num_iteration=env.iteration)

        # Chuyển đổi dự đoán log_price thành price
        y_pred = np.exp(y_pred_log) - epsilon
        y_actual = np.exp(y_test) - epsilon  # Chuyển đổi y_test từ log_price về price nếu y_test là log(price)

        # Đánh giá mô hình
        mse = mean_squared_error(y_actual, y_pred)
        rmse = np.sqrt(mse)
        mean_actual = np.mean(y_actual)
        percentage_error = (rmse / mean_actual) * 100
        mape = mean_absolute_percentage_error(y_actual, y_pred) * 100

        # In kết quả đánh giá
        print(f"Iteration {env.iteration}:")
        print(f"  Mean Squared Error (MSE): {mse}")
        print(f"  Root Mean Squared Error (RMSE): {rmse}")
        print(f"  Percentage Error của RMSE: {percentage_error} %")
        print(f"  Mean Absolute Percentage Error (MAPE): {mape} %")

print("Training LightGBM model...")

# Huấn luyện mô hình với callbacks
model = lgb.train(
    params=params,
    train_set=train_data,
    num_boost_round=num_boost_round,
    valid_sets=[train_data, valid_data],
    callbacks=[ custom_eval_callback, lgb.early_stopping(1000)]
)
# Dự đoán trên tập train
y_pred_train = model.predict(X_train, num_iteration=model.best_iteration)
y_pred_train = np.exp(y_pred_train) - epsilon  # Chuyển đổi ngược lại từ log(price) về giá trị gốc
# Đánh giá mô hình sau huấn luyện
mse_train = mean_squared_error(np.exp(y_train) - epsilon, y_pred_train)  # Tính trên giá trị price thật
rmse_train = np.sqrt(mse_train)
mape_train = mean_absolute_percentage_error(np.exp(y_train) - epsilon, y_pred_train) * 100
print(f"Final Mean Squared Error (MSE) on train: {mse_train}")
print(f"Final Root Mean Squared Error (RMSE) on train: {rmse_train}")
print(f"Final Mean Absolute Percentage Error (MAPE) on train: {mape_train} %")

# Dự đoán trên tập kiểm tra
y_pred = model.predict(X_test, num_iteration=model.best_iteration)

# Lưu mô hình vào file
model.save_model('lightgbm_model_complex.txt')
print("Model saved to 'lightgbm_model_complex.txt'")
y_pred = np.exp(y_pred) - epsilon  # Chuyển đổi ngược lại từ log(price) về giá trị gốc
# Đánh giá mô hình sau huấn luyện
mse = mean_squared_error(np.exp(y_test) - epsilon, y_pred)  # Tính trên giá trị price thật
rmse = np.sqrt(mse)
mape = mean_absolute_percentage_error(np.exp(y_test) - epsilon, y_pred) * 100

print(f"Final Mean Squared Error (MSE): {mse}")
print(f"Final Root Mean Squared Error (RMSE): {rmse}")
print(f"Final Mean Absolute Percentage Error (MAPE): {mape} %")

# Tạo DataFrame để so sánh giá trị dự đoán và giá trị thực tế
comparison_df = pd.DataFrame({
    'Predicted': y_pred[:5],
    'Actual': y_test[:5]
})

# In kết quả so sánh
print("Sample predictions vs actual values:")
print(comparison_df)

# Tính feature importance
feature_names = df.drop(columns=['price_square', 'price','furniture','area','log_price']).columns.tolist()
print(feature_names)
# Lấy feature importance từ mô hình và hiển thị
feature_importances = model.feature_importance(importance_type='split')
feature_importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': feature_importances})
feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)
print("Feature Importance:")
print(feature_importance_df)
#
# # Tính toán MAPE bằng k-fold cross-validation
# print("Đánh giá bằng k fold cross validation")
# K = 5
# kf = KFold(n_splits=K, shuffle=True, random_state=42)
# mape_scores = []
#
# # Thực hiện k-fold cross-validation
# # Dùng cross-validation
# for train_index, test_index in kf.split(X):
#     X_train, X_test = X[train_index], X[test_index]
#     y_train, y_test = y[train_index], y[test_index]
#
#     # Khởi tạo mô hình mới cho mỗi fold
#     model = lgb.LGBMRegressor(
#         objective='regression',
#         metric='mape',
#         boosting_type='gbdt',
#         learning_rate=0.07344563864614025,
#         num_leaves=137,
#         max_depth=12,
#         feature_fraction=0.9619720932813092,
#         bagging_fraction=0.6886977902886937,
#         bagging_freq=4,
#         lambda_l1=0.004726611625011041,
#         lambda_l2=0.1296782309409407,
#         verbose=-1,
#         n_estimators=1000
#     )
#
#     # Huấn luyện mô hình
#     model.fit(X_train, y_train, eval_set=[(X_test, y_test)])
#
#     # Dự đoán và chuyển đổi ngược lại từ log thành giá trị gốc
#     y_pred = model.predict(X_test)
#     y_pred = np.exp(y_pred) - epsilon
#     y_test_actual = np.exp(y_test) - epsilon
#
#     # Tính MAPE
#     mape = mean_absolute_percentage_error(y_test_actual, y_pred)
#     mape_scores.append(mape)
#
# # Tính MAPE trung bình trên các folds
# average_mape = np.mean(mape_scores)
# print(f"MAPE trung bình trên {K} folds:", average_mape)
#
# print("Sử dụng optina để tìm tham số tối ưu")
# import optuna
# from lightgbm import LGBMRegressor
# from sklearn.metrics import mean_absolute_percentage_error
#
#
# def objective(trial):
#     params = {
#         'objective': 'regression',
#         'metric': 'mape',
#         'boosting_type': 'gbdt',
#         'learning_rate': trial.suggest_loguniform('learning_rate', 1e-4, 0.1),
#         'num_leaves': trial.suggest_int('num_leaves', 20, 200),
#         'max_depth': trial.suggest_int('max_depth', 3, 15),
#         'feature_fraction': trial.suggest_uniform('feature_fraction', 0.6, 1.0),
#         'bagging_fraction': trial.suggest_uniform('bagging_fraction', 0.6, 1.0),
#         'bagging_freq': trial.suggest_int('bagging_freq', 1, 10),
#         'lambda_l1': trial.suggest_loguniform('lambda_l1', 1e-4, 10.0),
#         'lambda_l2': trial.suggest_loguniform('lambda_l2', 1e-4, 10.0),
#     }
#
#     model = LGBMRegressor(**params, n_estimators=1000)
#     model.fit(X_train, y_train, eval_set=[(X_test, y_test)],)
#     # Dự đoán và chuyển đổi ngược lại từ log thành giá trị gốc
#     y_pred = model.predict(X_test)
#     y_pred = np.exp(y_pred) - epsilon
#     y_test_actual = np.exp(y_test) - epsilon
#
#     # Tính MAPE
#     mape = mean_absolute_percentage_error(y_test_actual, y_pred)
#     mape_scores.append(mape)
#
#
# study = optuna.create_study(direction='minimize')
# study.optimize(objective, n_trials=50)
# print("Best parameters:", study.best_params)


