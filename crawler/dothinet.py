from base_crawler import BaseCrawler
import requests
from bs4 import BeautifulSoup
import logging
import re
import json
import time
import random

class DoThiNet(BaseCrawler):
    def __init__(self, proxies, user_agents):
        target_url = 'https://dothi.net/ban-can-ho-chung-cu-ha-noi/p{page}.htm'
        page_limit = 1
        save_path = 'data/raw/dothinet.json'
        super().__init__(proxies, user_agents, target_url, page_limit, save_path)
        
        self.base_url = 'https://dothi.net/'

    def extract_house_items(self, soup: BeautifulSoup) -> list:
        elements = soup.find_all(class_='vip-5-highlight')
        
        return elements
    
    def extract_item_url(self, item_html: BeautifulSoup) -> str:
        # find first a tag
        item_url = self.base_url + item_html.find('a').get('href')

        return item_url
    
    def extract_general_info(self, item_html: BeautifulSoup) -> dict:
        item_general_info = {}

        # Extract title (giả sử bạn đã có đoạn code để extract title)
        try:
            title = item_html.find('img').get('title')
            item_general_info['title'] = title
        except Exception as e:
            item_general_info['title'] = None
            print(f"Error extracting title: {e}")

        # Extract url
        try:
            item_general_info['url'] = self.extract_item_url(item_html)
        except Exception as e:
            item_general_info['url'] = None
            print(f"Error extracting URL: {e}")

        # Extract price (bỏ qua phần label)
        try:
            price_element = item_html.find('div', class_='price')
            price_value = price_element.find(text=True, recursive=False).strip()  # Chỉ lấy phần text không nằm trong thẻ con
            item_general_info['price'] = price_value
        except Exception as e:
            item_general_info['price'] = None
            print(f"Error extracting price: {e}")

        # Extract area (bỏ qua phần label)
        try:
            area_element = item_html.find('div', class_='area')
            area_value = area_element.find(text=True, recursive=False).strip()  # Chỉ lấy phần text không nằm trong thẻ con
            item_general_info['area'] = area_value
        except Exception as e:
            item_general_info['area'] = None
            print(f"Error extracting area: {e}")

        # Extract location (bỏ qua phần label)
        try:
            location_element = item_html.find('div', class_='location')
            location_value = location_element.find('strong').get_text(strip=True)  # Chỉ lấy phần trong thẻ <strong>
            item_general_info['location'] = location_value
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

        # Extract features from table with id 'tbl1'
        table_features = {}
        try:
            table = soup.find('table')
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)  # Key is the first <td>
                    value = cells[1].get_text(strip=True)  # Value is the second <td>
                    table_features[key] = value
        except Exception as e:
            print(f"Error when extracting table features: {e}")

        detail_info.update(table_features)

        return detail_info

if __name__ == '__main__':
    proxies = []
    user_agents = [
    ]
    crawler = DoThiNet(proxies, user_agents)
    crawler.run()
