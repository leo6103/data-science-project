import requests
from bs4 import BeautifulSoup
import random
import time
import csv
import json

class BaseCrawler:
    def __init__(self, proxies, user_agents, target_url, page_limit, save_path):
        self.proxies = proxies
        self.user_agents = user_agents
        self.target_url = target_url
        self.page_limit = page_limit
        self.save_path = save_path

    def send_request(self, url):
        headers = {
            "Pragma": "no-cache",
            "Priority": "u=0, i",
            "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "Linux",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7",
            "Cache-Control": "no-cache",
        }
        # TODO : Set proxies, user-agent for request
        # Send request to url
        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                return response.text
            
        except requests.exceptions.RequestException as e:
            print(e)
        return None

    def extract_house_items(self, html: BeautifulSoup) -> list:
        pass

    def extract_general_info(self, item_html: BeautifulSoup) -> str:
        pass

    def extract_item_url(self, item_html: BeautifulSoup) -> str:
        pass

    def extract_detail_info(self, item_url: str) -> dict:
        pass

    def crawl_page(self, page_num):
        url = self.target_url.format(page=page_num)
        print(f"Start crawling url: {url}")
        html = self.send_request(url)
        if html is None:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        house_items = self.extract_house_items(soup)
        print('List item')
        print(house_items)

        data = []
        for item in house_items:
            item_data = self.extract_general_info(item)

            item_url = self.extract_item_url(item)
            print(f"Extracting detail info from {item_url}")
            print('General data extracted:', item_data)
            detail_info = self.extract_detail_info(item_url)
            print('Detail data extracted:', detail_info)
            
            item_data.update(detail_info)
            
            data.append(item_data)

        return data

    def save_data(self, data):
        with open(self.save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {self.save_path}")

    def run(self):
        all_data = []
        for i in range(1, self.page_limit + 1):
            page_data = self.crawl_page(i)
            all_data.extend(page_data)

        self.save_data(all_data)
        print(f'Saved {len(all_data)} items to {self.save_path}')

    
