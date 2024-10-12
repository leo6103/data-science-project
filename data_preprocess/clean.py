import pandas as pd

# Đường dẫn đến file JSON
file_path = 'dothi2.json'  # Thay đổi đường dẫn theo vị trí lưu file của bạn

# Đọc file JSON vào DataFrame
data = pd.read_json(file_path)

# Get data với các cột : "Giá", "Diện tích", "Số phòng", "Quận"

data = data[["Giá", "Diện tích", "Số phòng", "Quận"]]

# Xử lý cột giá, xóa ký tự ' Tỷ'
data['Giá'] = data['Giá'].str.replace(' Tỷ', '')
# Chuyển dạng float
data['Diện tích'] = data['Diện tích'].str.replace(' m²', '').astype(float)

# Có 1 số data giá có dạng Triệu/m², tìm và in ra
for index, row in data.iterrows():
    if 'Triệu/m²' in row['Giá']:
        # Xóa ký tự ' Triệu/m²' và chuyển sang kiểu float, nhân với diện tích
        price_per_m2 = float(row['Giá'].replace(' Triệu/m²', '')) * row['Diện tích']

# Lưu vào file CSV
data.to_csv('dothi2.csv', index=False)