import torch
import torch.nn as nn
import torch.optim as optim
import sys
import os
# Thêm thư mục gốc của dự án vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# Import các hàm xử lý dữ liệu
import os
from torch.utils.data import DataLoader, TensorDataset
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np
from scipy import stats
from ml.models.wide_deep_learning import WideAndDeepModel  # Đảm bảo rằng bạn có mô hình này

path_csv_data = 'data/processed/batdongsancomvn/chungcu/processed_merged_chungcu.csv'

# Đọc dữ liệu
try:
    print("Start reading file...")
    df = pd.read_csv(path_csv_data)
    df = df.astype(np.float32)
except FileNotFoundError:
    print(f"Error: File '{path_csv_data}' không tồn tại.")
    sys.exit(1)
except Exception as e:
    print(f"Đã xảy ra lỗi: {e}")
    sys.exit(1)

# Xử lý ngoại lai và biến đổi logarit
df['z_score'] = np.abs(stats.zscore(df['price_square']))
df = df[df['z_score'] <= 3].drop(columns=['z_score'])
# df = df[df['area'] <= 200]
df['log_price'] = np.log(df['price'] + 1e-10)
df['log_area'] = np.log(df['area'] + 1e-10)

# Chia dữ liệu
X = df.drop(columns=['price_square', 'price','furniture','area','log_price']).values
y = df['log_price'].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Chuyển đổi dữ liệu thành Tensor
X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train, dtype=torch.float32).view(-1, 1)
y_test_tensor = torch.tensor(y_test, dtype=torch.float32).view(-1, 1)

# Tạo DataLoader
dataset = TensorDataset(X_train_tensor, y_train_tensor)
dataloader = DataLoader(dataset, batch_size=8, shuffle=True)

# Khởi tạo mô hình, hàm loss và optimizer
input_dim = X_train.shape[1]
model = WideAndDeepModel(input_dim)
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

# Hàm đánh giá
def call_eval(y_true, y_pred):
    mse = mean_squared_error(y_true, y_pred)
    print("Mean Squared Error trên tập kiểm tra:", mse)
    rmse = np.sqrt(mse)
    print("Root Mean Squared Error (RMSE):", rmse)
    mean_actual = np.mean(y_true)
    percentage_error = (rmse / mean_actual) * 100
    print("Percentage Error của RMSE:", percentage_error, "%")
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    print("Mean Absolute Percentage Error (MAPE):", mape, "%")

# Huấn luyện mô hình
num_epochs = 1000
for epoch in range(num_epochs):
    model.train()
    for batch_X, batch_y in dataloader:
        optimizer.zero_grad()
        outputs = model(batch_X)
        loss = criterion(outputs, batch_y)
        loss.backward()
        optimizer.step()

    # Đánh giá mô hình mỗi 10 epoch
    if (epoch + 1) % 10 == 0:
        print(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {loss.item():.4f}')
        model.eval()
        with torch.no_grad():
            y_pred = model(X_test_tensor).numpy()
        call_eval(y_test, y_pred)

# Đánh giá cuối cùng trên tập kiểm tra
print("Final Evaluation on Test Set:")
model.eval()
with torch.no_grad():
    y_pred = model(X_test_tensor).numpy()
call_eval(y_test, y_pred)

# In kết quả dự đoán mẫu
print("Dự đoán mẫu:")
print(y_pred[:5], y_test[:5])