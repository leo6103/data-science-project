import requests
from bs4 import BeautifulSoup
import random
import time
import csv
import json
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import concurrent.futures
from utils import SELENIUM, REQUESTS, PLAYWRIGHT
from playwright.sync_api import sync_playwright

class BaseCrawler:
    def __init__(
            self, 
            proxies, 
            user_agents, 
            target_url,
            start_page,
            end_page,
            save_path,
            request_type=REQUESTS,
            multi_threading=False
        ):
        self.proxies = proxies
        self.user_agents = user_agents
        self.target_url = target_url
        self.start_page = start_page
        self.end_page = end_page
        self.save_path = save_path
        self.request_type = request_type
        self.multi_threading = multi_threading

    def send_request(self, url):
        if self.request_type == SELENIUM:
            chrome_options = Options()
            chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
            
            driver = webdriver.Chrome(options=chrome_options)

            try:
                driver.get(url)
                
                driver.implicitly_wait(10)
                
                page_source = driver.page_source
                
                print(f"Successfully fetched page: {url}")
                return page_source

            except TimeoutException:
                print(f"Timeout while trying to fetch page: {url}")
                return None

            finally:
                driver.quit()
        elif self.request_type == REQUESTS:
            headers = {
                "Pragma": "no-cache",
                "Priority": "u=0, i",
                "Sec-Ch-Ua": '"Chromium";v="129", "Not;A=Brand";v="25", "Google Chrome";v="129"',  # Version numbers changed
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": "Linux",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",  # Updated the Chrome version here
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7",
                "Cache-Control": "no-cache",
            }
            
            try:
                response = requests.get(url, headers=headers)
                print(response.status_code)
                print(response.text)

                if response.status_code == 200:
                    return response.text
                
            except requests.exceptions.RequestException as e:
                print(e)
            return None
        elif self.request_type == PLAYWRIGHT:
            try:
                with sync_playwright() as p:
                    # Tạo một context với User-Agent
                    browser = p.chromium.launch(headless=False)
                    context = browser.new_context(
                        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
                    )
                    page = context.new_page()
                    page.goto(url)
                    page_source = page.content()

                    print(f"Successfully fetched page using Playwright: {url}")
                    return page_source

            except Exception as e:
                print(f"Error occurred while fetching page with Playwright: {e}")
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

        data = []

        if self.multi_threading:
            # Sử dụng đa luồng nếu self.multi_threading = True
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(self.process_item, item) for item in house_items]

                for future in concurrent.futures.as_completed(futures):
                    item_data = future.result()
                    data.append(item_data)
        else:
            # Chạy tuần tự nếu self.multi_threading = False
            for item in house_items:
                item_data = self.process_item(item)
                data.append(item_data)

        return data

    def process_item(self, item):
        item_data = self.extract_general_info(item)
        item_url = self.extract_item_url(item)

        print(f"======== Extracting detail info from {item_url}")
        print('General data extracted:', item_data)

        detail_info = self.extract_detail_info(item_url)
        print('Detail data extracted:', detail_info)
        
        # Cập nhật thông tin chi tiết vào item_data
        item_data.update(detail_info)

        return item_data

    def save_data(self, data):
        with open(self.save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {self.save_path}")

    def run(self):
        all_data = []
        # Crawl data from start_page to end_page
        for i in range(self.start_page, self.end_page + 1):
            page_data = self.crawl_page(i)
            all_data.extend(page_data)

        self.save_data(all_data)
        print(f'Saved {len(all_data)} items to {self.save_path}')
