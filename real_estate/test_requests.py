import requests
import json
import logging
import time
from selenium import webdriver
from bs4 import BeautifulSoup


# Set up logging
logging.basicConfig(filename='debug.log', 
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

headers = {
    "User-Agent": '''Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36''',
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7",
    "Connection": "keep-alive",
    "Referer": "https://batdongsan.com.vn/",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "no-cache"
    "Upgrade-Insecure-Requests:" "1",
}
page_limit = 5

base_url = 'https://batdongsan.com.vn/nha-dat-ban-ha-noi'

estate_list = []

for i in range(1, page_limit + 1):
    url = f'https://batdongsan.com.vn/nha-dat-ban-ha-noi/p{i}'
    logger.info(f'Fetching page {i} from URL: {url}')

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Đặt encoding dựa trên header Content-Type hoặc tự chỉ định
        response.encoding = response.apparent_encoding

        soup = BeautifulSoup(response.content, 'html.parser')

        elements = soup.find_all(class_='js__product-link-for-product-id')

        for element in elements:
                    # Chỉ giữ lại title và url
                    title = estate_url = None

                    try:
                        title = element.find(class_="re__card-title").get_text(separator=' ', strip=True)
                    except Exception as e:
                        logger.error(f'Error fetching title: {e}')

                    try:
                        estate_url = base_url + element['href']
                    except Exception as e:
                        logger.error(f'Error fetching url: {e}')

                    # Fetch detailed information from the estate_url
                    if estate_url:
                        logger.info(f'Fetching details from: {estate_url}')
                        try:
                            detail_response = requests.get(estate_url, headers=headers)
                            detail_response.raise_for_status()
                            soup_detail = BeautifulSoup(detail_response.content, 'html.parser')
                            features = {}

                            # Lấy tất cả các mục thông tin thuộc class 're__pr-specs-content-item'
                            info_items = soup_detail.find_all(class_='re__pr-specs-content-item')

                            # Duyệt qua các item để lấy tiêu đề và giá trị tương ứng
                            for item in info_items:
                                try:
                                    # Lấy tiêu đề của thông tin (Diện tích, Mức giá, Mặt tiền, Số tầng)
                                    feature_title = item.find(class_='re__pr-specs-content-item-title').get_text(strip=True)
                                    # Lấy giá trị tương ứng của thông tin
                                    feature_value = item.find(class_='re__pr-specs-content-item-value').get_text(strip=True)
                                    # Lưu lại vào từ điển features
                                    features[feature_title] = feature_value
                                except Exception as e:
                                    logger.error(f"Lỗi khi trích xuất thông tin chi tiết: {e}")

                            # Cập nhật các thông tin cơ bản với các thông tin chi tiết
                            estate_info = {
                                'Title': title,
                                'Url': estate_url
                            }

                            # Cập nhật các thông tin chi tiết vào estate_info
                            estate_info.update(features)

                            # Thêm estate_info vào danh sách estate_list
                            estate_list.append(estate_info)

                        except requests.RequestException as e:
                            logger.error(f'Error fetching details from {estate_url}: {e}')

    except requests.RequestException as e:
        logger.error(f'Error fetching page {i}: {e}')

# Log the final estate_list
if estate_list:
    logger.info('List length: ' + str(len(estate_list)))
    logger.info('Final list of estates:')
    logger.info(json.dumps(estate_list, indent=4, ensure_ascii=False))

# Output estate_list
for estate in estate_list:
    print(json.dumps(estate, indent=4, ensure_ascii=False))
