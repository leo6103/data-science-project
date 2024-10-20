from base_crawler import BaseCrawler
import requests
from bs4 import BeautifulSoup
import logging
import re
import json
import time
import random
from utils import REQUESTS, SELENIUM

class BatDongSanComVn(BaseCrawler):
    def __init__(
            self, 
            proxies, 
            user_agents, 
            target_url, 
            start_page, 
            end_page, 
            save_path, 
            request_type, 
            multi_threading
        ):
        super().__init__(proxies, user_agents, target_url, start_page, end_page, save_path, request_type, multi_threading)
        self.base_url = 'https://batdongsan.com.vn'

    def extract_house_items(self, soup: BeautifulSoup) -> list:
        elements = soup.find_all(class_='js__card js__card-full-web pr-container re__card-full re__vip-diamond')
        
        print(elements)
        valid_elements = [element for element in elements if element.get('prid') and element.get('prid') != '0']

        return elements

    
    def extract_item_url(self, item_html: BeautifulSoup) -> str:
        item_url = self.base_url + item_html.find('a', class_='js__product-link-for-product-id').get('href')
        
        return item_url
    
    def extract_general_info(self, item_html: BeautifulSoup) -> dict:
        item_general_info = {}
        
        try:
            title_element = item_html.find('span', class_='pr-title js__card-title')
            title = title_element.get_text(separator=' ', strip=True) if title_element else None
            item_general_info['title'] = title
        except Exception as e:
            item_general_info['title'] = None
            print(f"Error extracting title: {e}")

        try:
            item_general_info['url'] = self.extract_item_url(item_html)
        except Exception as e:
            item_general_info['url'] = None
            print(f"Error extracting URL: {e}")

        try:
            location_element = item_html.find('div', class_='re__card-location')
            location = location_element.find_all('span')[-1].get_text(separator=' ', strip=True) if location_element else None
            item_general_info['location'] = location
        except Exception as e:
            item_general_info['location'] = None
            print(f"Error extracting location: {e}")

        return item_general_info

    def extract_detail_info(self, item_url: str) -> dict:
        print(f'Extracting detail info with url {item_url}')
        html = self.send_request(item_url)

        if html is None:
            return {}

        detail_info = {}

        soup = BeautifulSoup(html, 'html.parser')
        table_features = {}
        table_items = soup.find_all(class_='re__pr-specs-content-item')
        for item in table_items:
            try:
                feature_title = item.find(class_='re__pr-specs-content-item-title').get_text(strip=True)
                feature_value = item.find(class_='re__pr-specs-content-item-value').get_text(strip=True)
                table_features[feature_title] = feature_value
            except Exception as e:
                logging.error(f"Error when extracting information: {e}")
        
        detail_info.update(table_features)
        # Special cases for area
        # Extract latitude and longitude from iframe data-src
        try:
            iframe = soup.find('iframe', class_='lazyload')
            data_src = iframe.get('data-src')

            # Use regex to find the coordinates after '?q='
            match = re.search(r'q=([\d.]+),([\d.]+)', data_src)
            if match:
                latitude = match.group(1)
                longitude = match.group(2)
                detail_info['latitude'] = latitude
                detail_info['longitude'] = longitude
        except Exception as e:
            logging.error(f"Error when extracting latitude and longitude: {e}")
        
        return detail_info

import time

if __name__ == '__main__':
    proxies = []
    user_agents = [
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0'
    ]

    start_time = time.time()

    target_url = 'https://batdongsan.com.vn/ban-can-ho-chung-cu-ha-noi/p1/p{page}'
    start_page = 1
    end_page = 15
    save_path = 'data/raw/batdongsancomvn.json'
    request_type = SELENIUM
    multithreading = True

    crawler = BatDongSanComVn(proxies, user_agents, target_url, start_page, end_page, save_path, request_type, multithreading)
    crawler.run()

    end_time = time.time()

    total_time = end_time - start_time
    print(f"Running time: {total_time:.2f} seconds")
