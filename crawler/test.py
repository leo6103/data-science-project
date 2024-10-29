import requests
from bs4 import BeautifulSoup

# URL bạn muốn kiểm tra
url = 'https://batdongsan.com.vn/ban-can-ho-chung-cu/p1/p1'

# Gửi yêu cầu GET để lấy HTML của trang
response = requests.get(url)

# Kiểm tra xem yêu cầu có thành công không
if response.status_code == 200:
    # Phân tích HTML bằng BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # In ra cấu trúc HTML đầy đủ của trang
    print(soup.prettify())
    
    # Hoặc in ra một phần (500 ký tự đầu tiên) nếu HTML quá dài
    print(soup.prettify()[:500])
else:
    print(f"Failed to retrieve page. Status code: {response.status_code}")
