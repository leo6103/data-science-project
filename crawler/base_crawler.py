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
import sys, signal
import unicodedata


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


        self.item_num = 0

        self.headless = True
  

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
                    "Cookie" : "__uidac=0166e10b24e9c33f51e204c31d3dedbd; _tt_enable_cookie=1; __RC=4; __R=1; __iid=6461; __iid=6461; __su=0; __su=0; _fbp=fb.2.1726024496003.446215731339796127; __tb=0; _hjSessionUser_1708983=eyJpZCI6Ijg0YWVkYzZjLWJkMjItNWQ3NS05MDI1LTVmYzc3MmQ0MDk1ZCIsImNyZWF0ZWQiOjE3MjYwMjQ0ODUxMDEsImV4aXN0aW5nIjp0cnVlfQ==; __zi=3000.SSZzejyD6jy_Zl2jp1eKttQU_gxC3nMGTChWuC8NLincmF_oW0L0s26VkVQ1JmJJ89gu_SXC2j5bchZvmKKEqpKq.1; _ga=GA1.1.900106895.1726024484; cf_clearance=8a4oUdhlSLpXc9aj216bpigYNrFfZ1dkxuSpbxvSTUg-1730792985-1.2.1.1-lUeQLO7SvfTdqDzh4ohhpKF8EEimtYyA4ldn05aXr2zau9xqQsQCkhOo6gp3vZbLiacIZw3oi0XDESi_ImxqdEQU.WmVQV9tCdZKTR3AG3IEWWDjDVgxRN.UBExgP63va.ojBbXtr2c2eEco8kQmjQOGpBWBEXQrpHyadx5gRqClQsrCEWT4_IqKzP_YCF1fhGTj6nh8cCVkz2FgF1pFyz0Q0ekh_TU2Md9XL7WxGE4WyEIJyO8Mt48fYvcRzSz.00tu7Fi5ZF3AVsWzaCQ_AAUKuhWgbuuVvr0r8RQ1DF8FmD5PAsbibyKQHEoRZuy.BShC5JPPMVQD_dBe1DcZ17zwkiQaAW2tFKa6jVrZCibn.GT6fQHO2lh0d3bC79GhK1AJrNNXykfEk9.F8skkGrV2by.g287Etimb_Z.6ONl2CnEAUagfPolaW53FAxAF; __admUTMtime=1731313343; _ttp=BbfBk5Dudk2tnOvY4mvlTGEXanV.tt.2; __uif=__uid%3A5696027391907961199; userinfo=khoinguyen6103@gmail.com; BDS.UMS.Cookie=CfDJ8JnPa_lzET9CkeNrvw8JOGr3gd7PvqLYt5cpjTLGAWwFt0d_uCrMdzGNrOrGq52IVMjnz51m9b2DD1lRU-dVxG_EqnKMwkx8SkVahXICzZYH4DtPjNfhZR3NMyI1baOq0tWlEMrnbAj1LgbXr8cIf6BPZyMAVrKR9XX8qKw3N9BC9qyjM6RL1Q-C1Q7w_9cTuz38GWHHeRKUL9q7ikxQ9x-F_lh19sQR6u-MWO1A7JrqfRzMOA_yI2-002fX4_WOfVSMWMHLP5WiT4wRYKIptcpvG0BO8zRABVe35d03DZB-X4x5zKIoE1RVvAA6GtjTnoLIHgMLqgtIeATorv7ih_FPir899-u8ArJzjrAK68jNCw1C3FC41281v4kfz6G88JsvKwWYry3_FVr6KJgrlpMud5d6-G2s1n0OX7eYTNOQmA08D5DKvEn7wyyfFIu1vHFzeMKKlGC2dEHcMIFfXqdqdPkPgY61c6X3yp5i4q0JgFjrAO6F1WYKiWZE2w6nQxyVAWbve-tlfu7Y0sUH_rKWKVxSUnMvu9x2Z1hwY-LN85etB5yw5FuojnDjPkq5VvldWA7X3ri9Ljsqo1FRV-5oDQVUCGSsnYusGaIs64Q3nBYLlAvKgLBAV9kpH7mSojtdwVMMUrHkAfBveGZqw8n1rAcQKYMF4sDMtGyl8qSr3BuREF9LEcA15P4xuamoxQ; c_u_id=3962265; ajs_anonymous_id=ab0d096b-55d9-4010-9978-69bc341da4cb; con.unl.lat=1733763600; con.unl.sc=23; .AspNetCore.Antiforgery.VyLW6ORzMgk=CfDJ8LEKtJ3EThVGr0F0l0smRaa2hPAeMUCo4FhdrB1gKWorSF-w8MxN8TCyFg0_S59kD4ipaHfz1lyxkzJgiEkj7CiusKMzm0BtjwxSfWM9TuKjTXprBKVfSC6AtQ6LqlHuM0Iy7sbsL6jzgQI80VH2hvo; PH_ONBOARDING_SESSION=0; _hjHasCachedUserAttributes=true; dtdz=_PID.1.3bc12cee0b251a7; onboarding-session-later=2; __UF=2%252C4; _clck=epcddk%7C2%7Cfrl%7C0%7C1715; _dtdcTime=1733814669; _gcl_au=1.1.1586975716.1733814673; _cfuvid=mfzC_dLNKAvlnwRgBpkaCgrpS69GspQ374JwuF00eQ4-1733794026968-0.0.1.1-604800000; refreshToken=lCpdy9Oj3MORQ7Z1a83CAHpW3yqyTNQkkrofhxm7x18; accessToken=eyJhbGciOiJSUzI1NiIsImtpZCI6Ijg5Mzg0OTU1MkNDRTExMUFDMjc5RjUyNDI3RUEwMUY5QzdDMzAxNTQiLCJ0eXAiOiJhdCtqd3QiLCJ4NXQiOiJpVGhKVlN6T0VSckNlZlVrSi1vQi1jZkRBVlEifQ.eyJuYmYiOjE3MzM3OTQwMjgsImV4cCI6MTczMzc5NzYyOCwiaXNzIjoiaHR0cDovL2F1dGhlbnRpY2F0aW9uLmJkcy5sYyIsImF1ZCI6IkFwaUdhdGV3YXkiLCJjbGllbnRfaWQiOiIwM2QwZjkwNS0xMGM5LTRkMjEtOTBmNS0xMGI3OGUwYTk4OWMiLCJzdWIiOiIzOTYyMjY1IiwiYXV0aF90aW1lIjoxNzMzMjY4OTM1LCJpZHAiOiJsb2NhbCIsInByZWZlcnJlZF91c2VybmFtZSI6Imtob2luZ3V5ZW42MTAzQGdtYWlsLmNvbSIsImVtYWlsIjoia2hvaW5ndXllbjYxMDNAZ21haWwuY29tIiwic2NvcGUiOlsib3BlbmlkIiwicHJvZmlsZSIsIkFwaUdhdGV3YXkiLCJvZmZsaW5lX2FjY2VzcyJdLCJhbXIiOlsicHdkIl19.Gyt-CdNm5F_vErJYgBD5oph4rvOJJS2amOpCGJ7WK_LSLQ8_ldJr6kqtkFJiEw3E0lii2vYn0yZf16BHlO73neIw0guRYIGDfTBCxU0jNXALxChBU0bjFUTIZ4Bl4EqRUkdPneaUoPJR-0cF6nWyr5DC-cDjKn-BKsoo8m8-EOy2OxDBbEc2tADU4JJPwmbjxOHrpfJn-jVQEKem8PNx_unnCSDGp9yGTcAIkMTVZH9PRJ7VQvCmU5Iw3rWqXPKXwCE65RfeXcEVL0HHogXqFCP71-gfiffp3Bw3Sn_KRrm0OsrYqEq25yljbajTV4pT9g7zCyYXRhd_sE5q_kTJ8g; ab.storage.deviceId.892f88ed-1831-42b9-becb-90a189ce90ad=%7B%22g%22%3A%2258be5d5f-ff16-fc7a-e984-949cca84dbb8%22%2C%22c%22%3A1726024488271%2C%22l%22%3A1733818824949%7D; ab.storage.userId.892f88ed-1831-42b9-becb-90a189ce90ad=%7B%22g%22%3A%223962265%22%2C%22c%22%3A1733243746952%2C%22l%22%3A1733818824951%7D; _ga_HTS298453C=deleted; __IP=999943754; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22VsqR6f0KTganJfzzaLPD%22%2C%22expiryDate%22%3A%222025-12-10T08%3A31%3A41.064Z%22%7D; __adm_upl=eyJ0aW1lIjoxNzMzNzk2NTcyLCJfdXBsIjoiMC01Njk2MDI3MzkxOTA3OTYxMTk5In0=; ab.storage.sessionId.892f88ed-1831-42b9-becb-90a189ce90ad=%7B%22g%22%3A%222f03344d-c545-4a3b-5727-777aec5c50fc%22%2C%22e%22%3A1733821305880%2C%22c%22%3A1733818824947%2C%22l%22%3A1733819505880%7D; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22expiryDate%22%3A%222025-12-10T08%3A31%3A46.129Z%22%7D; con.unl.usr.id=%7B%22key%22%3A%22userId%22%2C%22value%22%3A%22ab0d096b-55d9-4010-9978-69bc341da4cb%22%2C%22expireDate%22%3A%222025-12-10T08%3A39%3A37.1671841Z%22%7D; con.unl.cli.id=%7B%22key%22%3A%22clientId%22%2C%22value%22%3A%223b82a014-dddd-4310-95a1-e15d8650a154%22%2C%22expireDate%22%3A%222025-12-10T08%3A39%3A37.1672188Z%22%7D; _ga_HTS298453C=GS1.1.1733822693.46.0.1733822693.60.0.0; __gads=ID=6c36510227266d80:T=1726024484:RT=1733800050:S=ALNI_MYpMCLXJkAk4BFZ_Te_dyV4Xg7SWw; __gpi=UID=00000ef886aa4b55:T=1726024484:RT=1733800050:S=ALNI_MbgaJ8sQTI5YdGqDlJVE3OxyGd8Sw; __eoi=ID=0c3e74a94769ca07:T=1726024484:RT=1733800050:S=AA-Afjaeigrg2xUU2_8pOVHQ3zLK"
                }
                
                try:
                    # Send the request
                    response = requests.get(url, headers=headers, timeout=5)
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
                
        elif self.request_type == PLAYWRIGHT:
            while True:
                # Xoay vòng user-agent
                self.user_agents.append(self.user_agents[0])
                self.user_agents.popleft()  # Xoay vòng user-agent

                try:
                    with sync_playwright() as p:
                        browser = p.chromium.launch(headless=self.headless)
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

            if self.multi_threading:
                # Sử dụng đa luồng nếu self.multi_threading = True
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = [executor.submit(self.process_item, item) for item in house_items]
                    
                    for future in concurrent.futures.as_completed(futures):
                        item_data = future.result()
                        data.append(item_data)

            else:

                self.headless = True

            # Nếu nhận được dữ liệu hợp lệ, thoát khỏi vòng lặp
            break

        # Xử lý dữ liệu sau khi lấy được house_items
        if self.multi_threading:
            # Sử dụng đa luồng nếu self.multi_threading = True
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(self.process_item, item) for item in house_items]
                
                for future in concurrent.futures.as_completed(futures):
                    item_data = future.result()
                    print(f'Item data {item_data}')
                    if item_data['location'] is not None and 'Hà Nội' in unicodedata.normalize('NFKC', item_data['location']):
                        data.append(item_data)
                    else:
                        print('$$$$$$$$$$$$$$Data not saved')
        else:
            # Chạy tuần tự nếu self.multi_threading = False
            for item in house_items:
                item_data = self.process_item(item)
                if item_data['location'] is not None and 'Hà Nội' in unicodedata.normalize('NFKC', item_data['location']):
                    data.append(item_data)

        return data

    def process_item(self, item):
        while True:
            item_data = self.extract_general_info(item)
            item_url = self.extract_item_url(item)

            # print(f"======== Extracting detail info from {item_url}")
            # print('General data extracted:', item_data)

            detail_info = self.extract_detail_info(item_url)
            # print('Detail data extracted:', detail_info)

            if item_data['location'] == None:
                self.headless = False
            
                # Cập nhật thông tin chi tiết vào item_data
                item_data.update(detail_info)

                return item_data
            elif (detail_info == {} or item_data == {}) and self.headless == True:
                self.headless = False
                continue
            elif (detail_info == {} or item_data == {}):
                continue
            

            else:
                self.headless = True
            
                # Cập nhật thông tin chi tiết vào item_data
                item_data.update(detail_info)

                return item_data

    def save_data(self, data=None):
        """Hàm lưu dữ liệu ra tệp JSON"""
        if data is None:
            data = self.collected_data  # Nếu không truyền data, lưu dữ liệu trong `self.collected_data`
        try:
            with open(self.save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Data saved to {self.save_path}")
        except Exception as e:
            print(f"Error saving data: {e}")

    def signal_handler(self, signal_received, frame):
        """Hàm xử lý tín hiệu Ctrl+C"""
        print("\nSignal received: Saving data before exiting...")
        self.save_data()  # Lưu dữ liệu hiện tại
        sys.exit(0)  # Thoát chương trình một cách an toàn

    def run(self):
        """Phương thức chạy chính"""
        signal.signal(signal.SIGINT, self.signal_handler)  # Đăng ký signal handler
        self.collected_data = []  # Khởi tạo danh sách chứa dữ liệu đã thu thập

        print(f"Starting crawler for pages {self.start_page} to {self.end_page}...")
        for i in range(self.start_page, self.end_page + 1):
            try:
                print(f"Processing page {i}...")
                page_data = self.crawl_page(i)  # Thu thập dữ liệu từ trang
                print(f'Page data {page_data}')
                self.collected_data.extend(page_data)  # Thêm dữ liệu vào danh sách tổng
            except Exception as e:
                print(f"Error processing page {i}: {e}")
                continue

        # Sau khi hoàn thành, lưu tất cả dữ liệu
        self.save_data(self.collected_data)
        print(f"Saved {len(self.collected_data)} items to {self.save_path}")
