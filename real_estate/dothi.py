import requests
import json
import time
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

headers = {
    "User-Agent": '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36''',
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://batdongsan.com.vn/",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0"
}

page_limit = 180
base_url = 'https://dothi.net'
estate_list = []

def crawl_page(i):
    url = f'https://dothi.net/ban-can-ho-chung-cu-ha-noi/p{i}.htm'
    print(f'Fetching page {i} from URL: {url}')
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        elements = soup.find_all(class_='vip-5-highlight')
        print('Found', len(elements), 'elements')

        for element in elements:
            title = estate_url = None
            estate_info = {}

            try:
                title = element.find(class_="vip5")['title']
                estate_url = base_url + element.find(class_="vip5")['href']
                estate_info = {
                    'Tên': title,
                    'Url': estate_url
                }
                estate_list.append(estate_info)
                print(estate_url)
            except Exception as e:
                print(f'Error processing element: {e}')

            # Send request to url to figure out more attributes
            if estate_url:
                print(f'Fetching details from: {estate_url}')
                try:
                    detail_response = requests.get(estate_url, headers=headers, timeout=10)
                    detail_response.raise_for_status()
                    soup_detail = BeautifulSoup(detail_response.content, 'html.parser')

                    try:
                        location_element = soup_detail.find('div', class_="pd-location")
                        location_text = location_element.get_text(separator=' ', strip=True)
                        district_name = location_text.split('-')[1].strip()
                        estate_info['Quận'] = district_name  # Store district name
                    except Exception as e:
                        print("Error fetching district name:", e)

                    # Fetching price and area
                    try:
                        # Lấy thông tin giá
                        price_div = soup_detail.find('div', class_='pd-price')
                        price = price_div.find('span', class_='spanprice').get_text(strip=True)
                        estate_info['Giá'] = price + ' Tỷ'

                        # Lấy thông tin diện tích
                        area_text = price_div.text  # Lấy toàn bộ văn bản bên trong div
                        area_start = area_text.find('Diện tích:') + len('Diện tích:')  # Tìm vị trí bắt đầu của diện tích
                        area_end = area_text.find('m²', area_start)  # Tìm vị trí kết thúc của diện tích
                        if area_end != -1:  # Kiểm tra xem có tìm thấy 'm²' không
                            area = area_text[area_start:area_end].strip()  # Cắt chuỗi để lấy giá trị diện tích
                            estate_info['Diện tích'] = area + ' m²'
                        else:
                            print("Diện tích không có đơn vị 'm²' hoặc không tìm thấy trong phần mô tả.")
                    except Exception as e:
                        print("Error fetching price or area:", e)

                    try:
                        # Trích xuất nội dung mô tả từ div
                        description_div = soup_detail.find('div', class_='pd-desc-content')
                        description_text = description_div.get_text(separator=' ', strip=True)  # Dùng separator để giữ khoảng trắng giữa các dòng
                        estate_info['Mô tả'] = description_text
                    except Exception as e:
                        print("Error fetching description:", e)



                    # Fetching code
                    try:
                        code_row = soup_detail.find('td', text=lambda x: x and 'Mã số' in x)
                        code = code_row.find_next('td').get_text(strip=True)
                        estate_info['Mã số'] = code
                    except Exception as e:
                        print("Error fetching code:", e)

                    # Fetching type of advertisement
                    try:
                        type_row = soup_detail.find('td', text=lambda x: x and 'Loại tin rao' in x)
                        type_of_ad = type_row.find_next('td').get_text(strip=True)
                        estate_info['Loại tin rao'] = type_of_ad
                    except Exception as e:
                        print("Error fetching type of ad:", e)

                    # Fetching posting and expiration dates
                    try:
                        posted_date_row = soup_detail.find('td', text=lambda x: x and 'Ngày đăng tin' in x)
                        posted_date = posted_date_row.find_next('td').get_text(strip=True)
                        estate_info['Ngày đăng tin'] = posted_date

                        expiration_date_row = soup_detail.find('td', text=lambda x: x and 'Ngày hết hạn' in x)
                        expiration_date = expiration_date_row.find_next('td').get_text(strip=True)
                        estate_info['Ngày hết hạn'] = expiration_date
                    except Exception as e:
                        print("Error fetching posting or expiration dates:", e)

                    # Fetching direction and number of rooms
                    try:
                        direction_row = soup_detail.find('td', text=lambda x: x and 'Hướng' in x)
                        direction = direction_row.find_next('td').get_text(strip=True)
                        estate_info['Hướng nhà'] = direction

                        room_count_row = soup_detail.find('td', text=lambda x: x and 'Số phòng' in x)
                        room_count = room_count_row.find_next('td').get_text(strip=True)
                        estate_info['Số phòng'] = room_count
                    except Exception as e:
                        print("Error fetching direction or room count:", e)

                    print(estate_info)  # Finally, print all collected estate information

                        
                except Exception as e:
                    print(f'Error fetching details: {e}')

    except requests.exceptions.RequestException as e:
        print(f'Error fetching page {i}: {e}')

# Hàm chính để quản lý đa luồng
def run_crawler(multi_threading):
    if multi_threading:
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(crawl_page, i) for i in range(1, page_limit + 1)]
            for future in as_completed(futures):
                future.result()
    else:
        for i in range(1, page_limit + 1):
            crawl_page(i)

    # Save data to JSON file
    if estate_list:
        with open('dothi2.json', 'w', encoding='utf-8') as f:
            json.dump(estate_list, f, indent=4, ensure_ascii=False)
        
        print(f'Data has been successfully saved to dothi.json')
        print('Total:', len(estate_list))

# Example of running crawler with multithreading
run_crawler(multi_threading=True)
