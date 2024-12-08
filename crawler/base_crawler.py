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
from crawler.utils import SELENIUM, REQUESTS, PLAYWRIGHT
from playwright.sync_api import sync_playwright, TimeoutError
from collections import deque

# truoc khi update
class BaseCrawler:
    def __init__(
            self, 
            proxies,
            user_agents: deque, 
            target_url,
            start_page,
            end_page,
            save_path,
            request_type=REQUESTS,
            multi_threading=False
        ):
        
        self.proxies =proxies
        self.user_agents=user_agents
        self.target_url = target_url
        self.start_page = start_page
        self.end_page = end_page
        self.save_path = save_path
        self.request_type = request_type
        self.multi_threading = multi_threading

        self.item_num = 0
  

    def send_request(self, url):
       
        if self.request_type == SELENIUM:
            user_agent = random.choice(self.user_agents)
            # proxy = random.choice(self.proxies)
            chrome_options = Options()
            chrome_options.add_argument(f"user-agent={user_agent}")
            # chrome_options.add_argument(f"--proxy-server=http://{proxy}")
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
            while True:
                # Rotate user-agent for each retry
                user_agent = self.user_agents[0]
                self.user_agents.append(self.user_agents[0])
                self.user_agents.popleft()  # Rotate the user-agent

                headers = {
                    "Pragma": "no-cache",
                    "Priority": "u=0, i",
                    "Sec-Ch-Ua": '"Chromium";v="129", "Not;A=Brand";v="25", "Google Chrome";v="129"',  # Adjusted version numbers
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": "Linux",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": user_agent,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Accept-Language": "en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7",
                    "Cache-Control": "no-cache",
                }
                
                try:
                    # Send the request
                    response = requests.get(url, headers=headers, timeout=5)  # Set timeout for 5 seconds
                    print(response.status_code)
                    
                    # Check for a successful response
                    if response.status_code == 200:
                        print("Request successful")
                        return response.text
                    else:
                        print(f"Non-200 status code received: {response.status_code}. Retrying with a new User-Agent...")

                except requests.exceptions.Timeout:
                    print(f"Timeout occurred for URL: {url} with User-Agent: {user_agent}. Retrying with a new User-Agent...")
                
                except requests.exceptions.RequestException as e:
                    print(f"Request error occurred: {e}")
                    return None
                
                # Pause briefly before retrying
                time.sleep(1)
        elif self.request_type == PLAYWRIGHT:
            while True:
                # Xoay vòng user-agent
                self.user_agents.append(self.user_agents[0])
                self.user_agents.popleft()  # Xoay vòng user-agent

                try:
                    with sync_playwright() as p:
                        browser = p.chromium.launch(headless=True)
                        user_agent = self.user_agents[0]
                        context = browser.new_context(user_agent=user_agent)
                        page = context.new_page()

                        # Cố gắng truy cập trang với thời gian chờ tối đa là 5 giây
                        page.goto(url, wait_until="domcontentloaded")  # 5000 ms = 5 giây
                        page.wait_for_load_state("domcontentloaded", timeout=5000)

                        page_source = page.content()
                        print(f"Successfully fetched page using Playwright: {url}")
                        
                        # Đóng context và browser sau khi hoàn thành
                        page.close()
                        context.close()
                        browser.close()

                        return page_source

                except TimeoutError:
                    print(f"Timeout occurred for URL: {url} with User-Agent: {user_agent}. Retrying with a new User-Agent...")
                    # Tiếp tục vòng lặp với user-agent mới nếu hết thời gian chờ
                    time.sleep(1)  # Đặt khoảng nghỉ ngắn trước khi thử lại

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
        data = []
        
        while True:
            # Pop phần tử đầu tiên và append vào cuối trong self.user_agents
            self.user_agents.append(self.user_agents[0])
            self.user_agents.popleft()
            
            url = self.target_url.format(page=page_num)
            print(f"Start crawling url: {url}")

            html = self.send_request(url)
            
            # Thêm khoảng nghỉ ngẫu nhiên giữa các lần truy cập URL
            time.sleep(random.uniform(1, 2))

            # Kiểm tra nếu không nhận được HTML, thì thử lại
            if html is None:
                print("Failed to retrieve HTML. Retrying...")
                continue  # Bắt đầu lại vòng lặp nếu HTML là None

            soup = BeautifulSoup(html, 'html.parser')
            house_items = self.extract_house_items(soup)
            
            # Nếu không có house_items, tiếp tục lặp
            if not house_items:
                print("No items found on page. Retrying...")
                continue  # Bắt đầu lại vòng lặp nếu house_items rỗng

            # Nếu nhận được dữ liệu hợp lệ, thoát khỏi vòng lặp
            break

        # Xử lý dữ liệu sau khi lấy được house_items
        if self.multi_threading:
            # Sử dụng đa luồng nếu self.multi_threading = True
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(self.process_item, item) for item in house_items]
                
                for future in concurrent.futures.as_completed(futures):
                    item_data = future.result()
                    if item_data['location'] is not None and 'Hà Nội' in item_data['location']:
                        data.append(item_data)
        else:
            # Chạy tuần tự nếu self.multi_threading = False
            for item in house_items:
                item_data = self.process_item(item)
                if item_data['location'] is not None and 'Hà Nội' in item_data['location']:
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
