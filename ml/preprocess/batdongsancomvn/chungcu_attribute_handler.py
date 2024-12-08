from typing import List, Dict
from crawler.batdongsancomvn import BatDongSanComVn
from crawler.utils import PLAYWRIGHT
import json
import numpy as np


directions = ['None', 'Đông', 'Tây', 'Nam', 'Bắc', 'Đông - Nam', 'Tây - Nam', 'Đông - Bắc', 'Tây - Bắc']
N = len(directions) - 1

translation_dict = translation_dict = {
    "title": "title",
    "url": "url",
    "location": "location",
    "Diện tích": "area",
    "Mức giá": "price",
    "Hướng nhà": "house_direction",
    "Hướng ban công": "balcony_direction",
    "Số phòng ngủ": "bedrooms",
    "Số toilet": "toilets",
    "Pháp lý": "legal_status",
    "Nội thất": "furniture",
    "latitude": "latitude",
    "longitude": "longitude"
}


def translate_key(entry: Dict) -> Dict:
    translated_entry = {}
    
    for key, value in entry.items():
        new_key = translation_dict.get(key, key)
        translated_entry[new_key] = value
    
    print(translated_entry)
    return translated_entry


def normalize_item(entry: Dict) -> Dict:
    entry = translate_key(entry)
    entry = process_bedrooms_toilets(entry)
    entry = process_coordinates(entry)
    entry = process_area_price(entry)
    entry = process_directions(entry)

    return entry


def process_coordinates(entry: Dict) -> Dict:
    latitude = entry.get("latitude", None)
    longitude = entry.get("longitude", None)
    if latitude is not None and longitude is not None:
        entry["latitude"] = float(latitude)
        entry["longitude"] = float(longitude)

    return entry


def process_area_price(entry: Dict) -> Dict:
    area = entry.get("area", None)
    price = entry.get("price", None)

    if price == "Thỏa thuận":
        entry["price"] = "deal"
        entry["price_square"] = "deal"

    elif isinstance(price, str) and "triệu/m²" in price:
        price_per_sqm = float(price.split()[0].replace(",", "."))  # Lấy số trước "triệu/m²" và chuyển thành float
        entry["price_square"] = price_per_sqm  # Lưu giá trị gốc vào "price_square"
        if area is not None:
            entry["price"] = price_per_sqm * area  # Tính giá tổng
    
    elif isinstance(price, str) and "tỷ" in price:
        total_price_billion = float(price.split()[0].replace(",", "."))  # Lấy số trước "tỷ" và chuyển thành float
        total_price = total_price_billion * 1e3  # Chuyển từ tỷ sang triệu
        entry["price_square"] = total_price / area if area else None  # Tính giá trên m² và lưu vào "price_square"
        entry["price"] = total_price  # Lưu giá tổng vào "price"
    
    return entry


def process_directions(entry: Dict) -> Dict:
    def circular_encoding(index, N):
        angle = 2 * np.pi * index / N
        x = np.cos(angle)
        y = np.sin(angle)
        return x, y
    
    house_direction = entry.get("house_direction", None)
    if house_direction is not None:
        if house_direction == 'None':
            x, y = 0, 0  # Gán giá trị đặc biệt cho 'None'
        else:
            index = directions.index(house_direction)
            x, y = circular_encoding(index - 1, N)  # Trừ 1 để bỏ qua 'None' trong tính toán
        entry["house_direction"] = x,y

    balcony_direction = entry.get("balcony_direction", None)
    if balcony_direction is not None:
        if balcony_direction == 'None':
            x, y = 0, 0  # Gán giá trị đặc biệt cho 'None'
        else:
            index = directions.index(balcony_direction)
            x, y = circular_encoding(index - 1, N)  # Trừ 1 để bỏ qua 'None' trong tính toán
        entry["balcony_direction"] = x,y

    return entry


def process_bedrooms_toilets(entry: Dict) -> Dict:
    if "area" in entry and isinstance(entry["area"], str):
        area_value = entry["area"].split()[0].replace(",", ".")  # Thay thế dấu phẩy bằng dấu chấm
        entry["area"] = float(area_value)  # Chuyển thành số thực
    if "bedrooms" in entry and isinstance(entry["bedrooms"], str):
        entry["bedrooms"] = int(entry["bedrooms"].split()[0])  # Lấy số đầu tiên và chuyển thành số nguyên

    if "toilets" in entry and isinstance(entry["toilets"], str):
        entry["toilets"] = int(entry["toilets"].split()[0])

    return entry


def is_missing_data(entry: Dict) -> bool:
    return 'latitude' not in entry


def resolve_missing_data(entry: Dict) -> Dict:
    # TODO : Refactor after refactoring crawler
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.127 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.49 Safari/537.36",
    ]
    proxies = []
    target_url = 'https://batdongsan.com.vn/ban-nha-rieng/p1/p{page}'

    start_page =101
    end_page =120
    # save_path = f'data/raw/batdongsancomvn/chungcu/{start_page}-{end_page}.json'
    # save_path = f'data/raw/batdongsancomvn/dat/{start_page}-{end_page}.json'
    save_path = f'data/raw/batdongsancomvn/nharieng/{start_page}-{end_page}.json'


    request_type = PLAYWRIGHT
    multithreading = True

    crawler = BatDongSanComVn(proxies, user_agents, target_url, start_page, end_page, save_path, request_type, multithreading)

    detail_data = crawler.extract_detail_info(entry['url'])
    detail_data = {translation_dict[key]: value for key, value in detail_data.items()}

    entry.update(detail_data)
    entry = process_bedrooms_toilets(entry)
    entry = process_coordinates(entry)
    entry = process_area_price(entry)
    entry = process_directions(entry)

    return entry
        


