import requests
import json
import re
import time
from bs4 import BeautifulSoup

headers = {
    "User-Agent": '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36''',
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://batdongsan.com.vn/",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0"
}

page_limit = 20
base_url = 'https://alonhadat.com.vn'
estate_list = []

# Hàm để crawl một trang và xử lý dữ liệu
def crawl_page(i):
    url = f'https://alonhadat.com.vn/nha-dat/can-ban/can-ho-chung-cu/1/ha-noi/trang--{i}.html'
    print(f'Fetching page {i} from URL: {url}')
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        elements = soup.find_all(class_='content-item item')
        print('Found', len(elements), 'elements')

        for element in elements:
            title = estate_url = None
            estate_info = {}

            try:
                title = element.find(class_="ct_title").get_text(separator=' ', strip=True)
            except Exception as e:
                print(f'Error fetching title: {e}')

            try:
                estate_url = base_url + element.find(class_="ct_title").find('a')['href']
                print(estate_url)
            except Exception as e:
                print(f'Error fetching url: {e}')
            
            estate_info = {
                'Tên': title,
                'Url': estate_url
            }
            if estate_info:
                estate_list.append(estate_info)

    except requests.exceptions.RequestException as e:
        print(f'Error fetching page {i}: {e}')

    time.sleep(0.5)  # Chèn độ trễ 0.5 giây giữa mỗi yêu cầu

# Vòng lặp để crawl từng trang
for i in range(1, page_limit + 1):
    crawl_page(i)

# Lưu dữ liệu vào file alonhadat.json
if estate_list:
    with open('alonhadat.json', 'w', encoding='utf-8') as f:
        json.dump(estate_list, f, indent=4, ensure_ascii=False)
    
    print(f'Data has been successfully saved to alonhadat.json')
    print('Total:', len(estate_list))
