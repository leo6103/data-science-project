from crawler.base_crawler import BaseCrawler
import requests
from bs4 import BeautifulSoup
import logging
import re
import json
import time
import random
from crawler.utils import REQUESTS, SELENIUM, PLAYWRIGHT
from collections import deque
import signal


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
    
        elements = soup.find_all(
            "div", 
            class_=re.compile(r"js__card.*pr-container.*re__card-full")
        )

        # print(elements)
        valid_elements = [element for element in elements if element.get('prid') and element.get('prid') != '0']

        return elements

    
    def extract_item_url(self, item_html: BeautifulSoup) -> str:
        link_tag = item_html.find('a', class_='js__product-link-for-product-id')
        if link_tag and link_tag.get('href'):
            href = link_tag.get('href')
            if href.startswith("http://") or href.startswith("https://"):
                item_url = href 
            else:
                item_url = self.base_url + href
        return item_url
    
    
    def extract_general_info(self, item_html: BeautifulSoup) -> dict:
        item_general_info = {}

        try:
            title_element = item_html.find('span', class_='pr-title js__card-title')
            title = title_element.get_text(separator=' ', strip=True) if title_element else None
            item_general_info['title'] = title
        except Exception as e:
            item_general_info['title'] = None
            # print(f"Error extracting title: {e}")

        try:
            item_general_info['url'] = self.extract_item_url(item_html)
        except Exception as e:
            item_general_info['url'] = None
            # print(f"Error extracting URL: {e}")

        try:
            location_element = item_html.find('div', class_='re__card-location')
            location = location_element.find_all(['span', 'i'])[-1].get_text(separator=' ', strip=True) if location_element else None
            item_general_info['location'] = location
        except Exception as e:
            item_general_info['location'] = None
            print(f"Error extracting location: {e}")

        return item_general_info

    def extract_detail_info(self, item_url: str) -> dict:
        # print(f'Extracting detail info with url {item_url}')
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
    proxies =[]
    # ["127.0.0.1:30000",
    # "127.0.0.1:30001",
    # "127.0.0.1:30002",
    # "127.0.0.1:30003",
    # "127.0.0.1:30004",
    # "127.0.0.1:30005",
    # "127.0.0.1:30006",
    # "127.0.0.1:30007",
    # "127.0.0.1:30008",
    # "127.0.0.1:30009",
    # "127.0.0.1:30010",
    # "127.0.0.1:30011",
    # "127.0.0.1:30012",
    # "127.0.0.1:30013",
    # "127.0.0.1:30014",
    # "127.0.0.1:30015",
    # "127.0.0.1:30016",
    # "127.0.0.1:30017",
    # "127.0.0.1:30018",
    # "127.0.0.1:30019"]
    user_agents = deque([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.127 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.49 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:114.0) Gecko/20100101 Firefox/114.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:113.0) Gecko/20100101 Firefox/113.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.49 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.5563.111 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:106.0) Gecko/20100101 Firefox/106.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:105.0) Gecko/20100101 Firefox/105.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.74 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.1661.44 Safari/537.36 Edg/111.0.1661.44",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.1587.57 Safari/537.36 Edg/110.0.1587.57",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) coc_coc_browser/95.0.150 Chrome/89.0.4389.150 Safari/537.36"
    ])

    start_time = time.time()
    # target_url = 'https://batdongsan.com.vn/ban-can-ho-chung-cu-ha-noi/p{page}'
    target_url = 'https://batdongsan.com.vn/ban-dat-dat-nen-ha-noi/p{page}'
    # target_url = 'https://batdongsan.com.vn/ban-nha-rieng-ha-noi/p{page}'

    start_page = 101
    end_page = 150


    # save_path = f'data/raw/batdongsancomvn/chungcu/{start_page}-{end_page}.json'
    save_path = f'data/raw/batdongsancomvn/dat/new{start_page}-{end_page}.json'
    # save_path = f'data/raw/batdongsancomvn/nharieng/new{start_page}-{end_page}.json'


    request_type = PLAYWRIGHT
    multithreading = True

    crawler = BatDongSanComVn(proxies, user_agents, target_url, start_page, end_page, save_path, request_type, multithreading)
    crawler.run()

    end_time = time.time()

    total_time = end_time - start_time
    print(f"Running time: {total_time:.2f} seconds")
