import json
import matplotlib.pyplot as plt
import seaborn as sns

# Hàm đọc data từ file JSON
def read_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# Hàm visualize dữ liệu bất động sản (diện tích và số tầng)
def visualize_estate_data(data):
    # Trích xuất diện tích và số tầng từ data
    dien_tich = []
    so_tang = []
    labels = []
    
    for i, estate in enumerate(data):
        # Xử lý chuỗi diện tích và số tầng để lấy giá trị số
        try:
            dt = float(estate['Diện tích'].replace('m²', '').replace(',', '.').strip())
            st = int(estate['Số tầng'].split()[0])  # Chỉ lấy số đầu tiên
            dien_tich.append(dt)
            so_tang.append(st)
            labels.append(f"Nhà {i+1}")
        except Exception as e:
            print(f"Lỗi khi trích xuất dữ liệu: {e}")

    # Vẽ biểu đồ cột so sánh diện tích các căn nhà
    plt.figure(figsize=(10, 5))
    plt.bar(labels, dien_tich, color='skyblue')
    plt.title('So sánh diện tích các căn nhà')
    plt.xlabel('Căn nhà')
    plt.ylabel('Diện tích (m²)')
    plt.show()

    # Vẽ biểu đồ Seaborn so sánh số tầng và diện tích
    plt.figure(figsize=(10, 5))
    sns.scatterplot(x=dien_tich, y=so_tang, hue=labels, s=100, palette="viridis")
    plt.title('Mối quan hệ giữa diện tích và số tầng')
    plt.xlabel('Diện tích (m²)')
    plt.ylabel('Số tầng')
    plt.show()

# Đọc dữ liệu từ file general_data.json
data = read_data('general_data.json')

# Thực hiện visualize dữ liệu bất động sản
visualize_estate_data(data)
