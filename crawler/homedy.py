from crawler.base_crawler import BaseCrawler
from bs4 import BeautifulSoup
from collections import deque
from crawler.utils import REQUESTS, SELENIUM, PLAYWRIGHT
import time


class Homedy(BaseCrawler):
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
        self.base_url = 'https://homedy.com/'

    def extract_house_items(self, soup: BeautifulSoup) -> list:
        print('Extracting items')
        elements = soup.find_all(class_='product-item')
        print(elements)
        return elements
    
    def extract_item_url(self, item_html: BeautifulSoup) -> str:
        item_url = self.base_url + item_html.find('a').get('href')

        return item_url
    
    def extract_general_info(self, item_html: BeautifulSoup) -> dict:
        item_general_info = {}

        # Extract title
        try:
            title_element = item_html.find('h3').find('a', class_='title')
            title = title_element.get('title')
            item_general_info['title'] = title
        except Exception as e:
            item_general_info['title'] = None
            print(f"Error extracting title: {e}")

        # Extract URL
        try:
            url_element = item_html.find('h3').find('a', class_='title')
            url = url_element.get('href')
            # Add base URL if necessary
            base_url = "https://homedy.com"
            full_url = f"{base_url}{url}" if url.startswith('/') else url
            item_general_info['url'] = full_url
        except Exception as e:
            item_general_info['url'] = None
            print(f"Error extracting URL: {e}")

        # Extract location
        try:
            location_element = item_html.find('li', class_='address')
            location = location_element.get_text(strip=True)
            item_general_info['location'] = location
        except Exception as e:
            item_general_info['location'] = None
            print(f"Error extracting location: {e}")

        print(f'Extracted general info: {item_general_info}')
        return item_general_info

    def extract_detail_info(self, item_url: str) -> dict:
        print(f'Extracting detail info with url {item_url}')
        html = self.send_request(item_url)

        if html is None:
            return {}

        detail_info = {}
        soup = BeautifulSoup(html, 'html.parser')

        # Extract price and area
        try:
            product_info = soup.find('div', class_='product-short-info')
            if product_info:
                # Find all short-item elements
                short_items = product_info.find_all('div', class_='short-item')
                
                if len(short_items) >= 2:
                    # Extract price from the first short-item
                    price_element = short_items[0].find('strong')
                    if price_element:
                        price = price_element.get_text(strip=True).replace("\n", " ")
                        detail_info['price'] = price
                    
                    # Extract area from the second short-item
                    area_element = short_items[1].find('strong')
                    if area_element:
                        area = area_element.get_text(strip=True).replace("\n", " ")
                        detail_info['area'] = area
        except Exception as e:
            print(f"Error extracting price and area: {e}")

        # Extract additional attributes
        try:
            attributes = {}
            attributes_section = soup.find('div', class_='product-attributes')
            if attributes_section:
                attribute_items = attributes_section.find_all('div', class_='product-attributes--item')
                for item in attribute_items:
                    key = item.find('span').get_text(strip=True)
                    value = item.find_all('span')[-1].get_text(strip=True)
                    attributes[key] = value
            detail_info.update(attributes)
        except Exception as e:
            print(f"Error extracting additional attributes: {e}")

        # Extract latitude and longitude
        try:
            location_reviews = soup.find('div', class_='location_reviews')
            if location_reviews:
                view_detail_link = location_reviews.find('a', class_='view-detail')
                if view_detail_link and 'latitude' in view_detail_link['href'] and 'longitude' in view_detail_link['href']:
                    href = view_detail_link['href']
                    latitude = href.split('latitude=')[1].split('&')[0].replace(',', '.')
                    longitude = href.split('longitude=')[1].split('&')[0].replace(',', '.')
                    detail_info['latitude'] = latitude
                    detail_info['longitude'] = longitude
        except Exception as e:
            print(f"Error extracting latitude and longitude: {e}")

        print(f'Detail info: {detail_info}')
        return detail_info


if __name__ == '__main__':
    proxies = []
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
    target_url = 'https://homedy.com/ban-nha-rieng-ha-noi/p{page}'
    start_page = 1
    end_page = 200
    save_path = f'data/raw/homedy/nharieng/{start_page}-{end_page}.json'
    request_type = PLAYWRIGHT
    multithreading = True

    crawler = Homedy(proxies, user_agents, target_url, start_page, end_page, save_path, request_type, multithreading)
    crawler.run()

    end_time = time.time()

    total_time = end_time - start_time
    print(f"Running time: {total_time:.2f} seconds")