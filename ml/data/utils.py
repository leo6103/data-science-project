


import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from crawler.batdongsancomvn import BatDongSanComVn
import json


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def get_missing_data(url):

    user_agents = [
        'Mozilla/5.0 (Macintosh; ARM64; macOS 11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64',
        'Mozilla/5.0 (Macintosh; ARM64; rv:91.0) Gecko/20100101 Firefox/91.0'
    ]
    proxies = []

    target_url = 'https://batdongsan.com.vn/ban-can-ho-chung-cu-ha-noi/p1/p{page}'
    start_page = 1
    end_page = 1
    save_path = f'data/raw/batdongsancomvn/chungcu/{start_page}-{end_page}.json'
    request_type = "playwright"
    multithreading = True

    crawler = BatDongSanComVn(proxies, user_agents, target_url, start_page, end_page, save_path, request_type,
                              multithreading)
    item_data = crawler.extract_general_info(url)

    item_data.update(crawler.extract_detail_info(url))
    print("Item data")
    print(item_data)
    return  item_data

def read_json_file(url_missing_data):
    url_data = None
    try:
        print("Start reading file...")

        # Mở và đọc file JSON
        with open(url_missing_data, 'r', encoding='utf-8') as file:
            url_data = json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{url_missing_data}' không tồn tại.")
    except json.JSONDecodeError:
        print(f"Error: File '{url_missing_data}' không đúng định dạng JSON.")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
    print("Done")
    return url_data


def remove_duplicates_by_url(data):
    seen_urls = set()  # Tạo một tập hợp để lưu trữ các URL đã gặp
    unique_data = []  # Danh sách chứa các phần tử có URL duy nhất

    for item in data:
        url = item.get('url')  # Lấy giá trị URL từ từng phần tử

        # Nếu URL chưa tồn tại trong tập hợp, thêm phần tử vào danh sách kết quả
        if url not in seen_urls:
            unique_data.append(item)
            seen_urls.add(url)  # Đánh dấu URL đã xuất hiện

    return unique_data

if __name__ == '__main__':
    urls_path = 'processed/url_missing_data.json'
    path_raw_data = 'data/raw/batdongsancomvn/chungcu/merged/1-10.json'
    print(f"Đang mở file từ đường dẫn 1: {urls_path}")
    print(f"Đang mở file từ đường dẫn 2: {path_raw_data}")
    urls = read_json_file(urls_path)
    raw_data = read_json_file(path_raw_data)
    raw_data = remove_duplicates_by_url(raw_data)
    add_data = []

    for url in urls:
        detail_missing_data = get_missing_data(url)
        print("Detail missing data")
        print(detail_missing_data)
        add_data.append(detail_missing_data)

    with open("processed/preprocess_data1.json", 'w', encoding='utf-8') as file:
        json.dump(add_data, file, ensure_ascii=False, indent=4)
    print("Done")

