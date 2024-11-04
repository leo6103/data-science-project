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

# truoc khi update
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
        
        self.proxies =proxies
#         self.proxies=[
#     "127.0.0.1:30000",
#     "127.0.0.1:30001",
#     "127.0.0.1:30002",
#     "127.0.0.1:30003",
#     "127.0.0.1:30004",
#     "127.0.0.1:30005",
#     "127.0.0.1:30006",
#     "127.0.0.1:30007",
#     "127.0.0.1:30008",
#     "127.0.0.1:30009",
#     "127.0.0.1:30010",
#     "127.0.0.1:30011",
#     "127.0.0.1:30012",
#     "127.0.0.1:30013",
#     "127.0.0.1:30014",
#     "127.0.0.1:30015",
#     "127.0.0.1:30016",
#     "127.0.0.1:30017",
#     "127.0.0.1:30018",
#     "127.0.0.1:30019"

   
# ]
        self.user_agents=user_agents
#         self.user_agents =[ # Chrome trên Windows
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.127 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.49 Safari/537.36",
    
#     # Firefox trên Windows
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:114.0) Gecko/20100101 Firefox/114.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:113.0) Gecko/20100101 Firefox/113.0",

#     # Safari trên macOS
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",

#     # Chrome trên macOS
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.49 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.5563.111 Safari/537.36",

#     # Firefox trên macOS
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:106.0) Gecko/20100101 Firefox/106.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:105.0) Gecko/20100101 Firefox/105.0",
    
#     # Chrome trên Linux
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.74 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.124 Safari/537.36",

#     # Firefox trên Linux
#     "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
#     "Mozilla/5.0 (X11; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0",
    
#     # Edge trên Windows
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.1661.44 Safari/537.36 Edg/111.0.1661.44",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.1587.57 Safari/537.36 Edg/110.0.1587.57",

    
#     # Cốc Cốc trên Windows
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) coc_coc_browser/95.0.150 Chrome/89.0.4389.150 Safari/537.36",
# ]
        self.target_url = target_url
        self.start_page = start_page
        self.end_page = end_page
        self.save_path = save_path
        self.request_type = request_type
        self.multi_threading = multi_threading
  

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
            # proxy = random.choice(self.proxies)
            user_agent = random.choice(self.user_agents)
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
                "User-Agent": random.choice(self.user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7",
                "Cache-Control": "no-cache",
            }
            # proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
            
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
            user_agent = random.choice(self.user_agents)
            # proxy = random.choice(self.proxies)
            try:
                with sync_playwright() as p:
                    # Tạo một context với User-Agent
                    browser = p.chromium.launch(headless=True)
                    context = browser.new_context(
                        user_agent=user_agent
                    )
                    page = context.new_page()
                    page.goto(url)
                    page.wait_for_load_state("domcontentloaded")
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
       # Thêm khoảng nghỉ ngẫu nhiên giữa các lần truy cập URL
        time.sleep(random.uniform(1, 2))
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
