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

page_limit = 200
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
        with open('dothi.json', 'w', encoding='utf-8') as f:
            json.dump(estate_list, f, indent=4, ensure_ascii=False)
        
        print(f'Data has been successfully saved to dothi.json')
        print('Total:', len(estate_list))

# Example of running crawler with multithreading
run_crawler(multi_threading=True)
