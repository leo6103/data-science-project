from typing import List, Dict

from crawler.batdongsancomvn import BatDongSanComVn
from crawler.utils import PLAYWRIGHT
import json
import numpy as np


directions = ['None', 'Đông', 'Tây', 'Nam', 'Bắc', 'Đông - Nam', 'Tây - Nam', 'Đông - Bắc', 'Tây - Bắc']

N = len(directions) - 1

translation_dict = {
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
legal_status_mapping = {
    'HDMB': 0,
    'Hợp đồng mua bán': 0,
    'Đang chờ sổ': 0,
    'Hợp đồng thuê': 0,
    'Sổ đỏ': 1,
    'Sổ hồng': 1,
    'Sổ đỏ chính chủ': 1,
    'Sổ đỏ/ Sổ hồng': 1,
    'Có sổ.': 1,
    'Sổ 50 năm': 1,
    'Sổ lâu dài + Quỹ căn HĐMB 50 năm': 1,
    'Pháp lý đầy đủ, đảm bảo an tâm cho các giao dịch bất động sản': 1,
    'Đầy đủ sẵn sàng giao dịch': 1
}



# Từ điển mã hóa các giá trị 'furniture'
furniture_mapping = {
    'Không nội thất': 0,
    'Cơ bản': 1,
    'Cơ bản - Nhà mới 100% bàn giao nguyên bản chủ đầu tư.': 1,
    'Nội thất cơ bản': 1,
    'Nội thất cơ bản CĐT hoàn thiện': 1,
    'Đầy đủ nội thất': 2,
    'Đã có đầy đủ nội thất để có thể vào ở được luôn.': 2,
    'Full nội thất': 2,
    'Nội thất cao cấp': 3,
    'Full nội thất cao cấp': 3,
    'Bàn giao full nội thất cao cấp liền tường nhập khẩu Châu Âu.': 3,
    'Full nội thất nhập khẩu Châu Âu cao cấp': 3,
    'Nội thất đầy đủ cao cấp từ Smegg, Villory&Boss.': 3
} 



def translate_key(entry: Dict) -> Dict:
    translated_entry = {}
    
    for key, value in entry.items():
        new_key = translation_dict.get(key, key)
        translated_entry[new_key] = value
    
    return translated_entry


def remove_duplicates_by_url(data):
    seen_urls = set()
    unique_data = []

    for item in data:
        url = item.get('url')
        if url not in seen_urls:
            unique_data.append(item)
            seen_urls.add(url)
    print("remove_duplicates_by_url success")

    return unique_data

def normalize_interim_item(entry: Dict) -> Dict:
    entry = translate_key(entry)
    entry = process_bedrooms_toilets(entry)
    entry = process_coordinates(entry)
    entry = process_area_price(entry)

    entry = process_directions(entry)
    entry = process_legal_status(entry)
    entry = process_furniture_data(entry)

    return entry

def normalize_process_item(entry: Dict) -> Dict:
    entry = remove_keys_from_data(entry)
    if entry is None:
        return None
    entry = remove_price_square_deal(entry)
    if entry is None:
        return None
    entry = remove_other_keys(entry)
    if entry is None:
        return None
    # entry = remove_objects_with_none(entry)
    return entry


def process_coordinates(entry: Dict) -> Dict:
    latitude = entry.get("latitude")
    longitude = entry.get("longitude")
    if latitude is not None and longitude is not None:
        entry["latitude"] = float(latitude)
        entry["longitude"] = float(longitude)
    return entry


def process_area_price(entry: Dict) -> Dict:
    area = entry.get("area", None)
    price = entry.get("price", None)

    if price == "Thỏa thuận":
        entry["price"] = "deal"

    # Nếu giá có dạng "X triệu/m²"
    elif isinstance(price, str) and "triệu/m²" in price:
        try:
            price_per_sqm = float(price.split()[0].replace(",", "."))
            if area is not None:
                entry["price"] = price_per_sqm * area
        except ValueError:
            entry["price"] = None  # Gán None nếu chuyển đổi thất bại

    # Nếu giá có dạng "X tỷ"
    elif isinstance(price, str) and "tỷ" in price:
        try:
            total_price_billion = float(price.split()[0].replace(",", "."))
            total_price = total_price_billion * 1e3
            entry["price"] = total_price
        except ValueError:
            entry["price"] = None

    # Nếu giá có dạng "X triệu"
    elif isinstance(price, str) and "triệu" in price:
        try:
            total_price_million = float(price.split()[0].replace(",", "."))
            entry["price"] = total_price_million
        except ValueError:
            entry["price"] = None

    # Chuyển price sang float và chia cho 1000 nếu cần
    if "price" in entry and isinstance(entry["price"], (int, float)):
        entry["price"] /= 1000

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
            x, y = 0, 0
        else:
            index = directions.index(house_direction)
            x, y = circular_encoding(index - 1, N)
        entry["house_direction_x"] = x
        entry["house_direction_y"] = y
        entry.pop("house_direction", None)

    balcony_direction = entry.get("balcony_direction", None)
    if balcony_direction is not None:
        if balcony_direction == 'None':
            x, y = 0, 0
        else:
            index = directions.index(balcony_direction)
            x, y = circular_encoding(index - 1, N)
        entry["balcony_direction_x"] = x
        entry["balcony_direction_y"] = y
        entry.pop("balcony_direction", None)


    return entry

def process_furniture_data(entry):
    """
    Hàm xử lý dữ liệu furniture từ một object, chấp nhận khớp một phần giá trị.
    Args:
        entry (dict): Một object chứa thông tin về nội thất.
    Returns:
        dict: Object với cột 'furniture' đã được mã hóa.
    """
    furniture = entry.get("furniture")
    if furniture is not None:
        # Tìm key trong từ điển có chứa một phần của furniture
        for key, value in furniture_mapping.items():
            if key in furniture:  # Kiểm tra chuỗi con
                entry["furniture"] = value
                return entry
        # Nếu không khớp phần nào thì gán None
        entry["furniture"] = None
    else:
        entry["furniture"] = None
    return entry

def process_bedrooms_toilets(entry: Dict) -> Dict:
    if "area" in entry and isinstance(entry["area"], str):
        area_value = entry["area"].split()[0].replace(",", ".")
        entry["area"] = float(area_value)

    if "bedrooms" in entry and isinstance(entry["bedrooms"], str):
        entry["bedrooms"] = int(entry["bedrooms"].split()[0])

    if "toilets" in entry and isinstance(entry["toilets"], str):
        entry["toilets"] = int(entry["toilets"].split()[0])

    return entry


def process_legal_status(entry):
    """
    Hàm chuẩn hóa dữ liệu legal status từ một object,
    cho phép khớp một phần giá trị với legal_status_mapping.
    Args:
        entry (dict): Một object chứa thông tin về tình trạng pháp lý.
    Returns:
        dict: Object với thuộc tính legal_status đã được mã hóa.
    """
    legal_status = entry.get("legal_status")
    if legal_status is not None:
        # Tìm key trong từ điển có chứa một phần của legal_status
        for key, value in legal_status_mapping.items():
            if key in legal_status:  # Kiểm tra khớp một phần
                entry["legal_status"] = value
                return entry
        # Nếu không khớp phần nào thì gán None
        entry["legal_status"] = None
    else:
        entry["legal_status"] = None

    return entry


def remove_keys_from_data(entry):
    """
    Hàm loại bỏ các khóa cụ thể khỏi một object nếu object đó chứa khóa 'longitude'.
    Args:
        entry (dict): Đối tượng chứa dữ liệu.
    Returns:
        dict: Đối tượng đã loại bỏ các khóa cụ thể nếu tồn tại 'longitude'.
    """
    keys_to_remove = ["title", "url", "location"]

    # Kiểm tra nếu entry có khóa 'longitude', sau đó loại bỏ các khóa trong keys_to_remove
    if entry is not None:
        for key in keys_to_remove:
            entry.pop(key, None)  # Xóa khóa nếu tồn tại

    return entry

def remove_price_square_deal(entry):
    """
    Hàm kiểm tra và loại bỏ một entry nếu có giá trị 'deal' cho 'price_square' hoặc 'price'.
    Args:
        entry (dict): Đối tượng chứa dữ liệu.
    Returns:
        dict hoặc None: Trả về entry nếu hợp lệ, ngược lại trả về None nếu có giá trị 'deal'.
    """
    if entry.get("price_square") == "deal" or entry.get("price") == "deal":
        return None
    return entry


def remove_other_keys(entry):
    """
    Hàm giữ lại các khóa cần thiết trong một đối tượng dữ liệu và loại bỏ các khóa khác.
    Args:
        entry (dict): Đối tượng chứa dữ liệu.
    Returns:
        dict: Đối tượng chỉ còn các khóa cần giữ lại hoặc None nếu entry là None.
    """
    if entry is None:
        return None  # Trả về None nếu entry là None

    # Danh sách các key cần giữ lại
    keys_to_keep = [
        "area", "price", "bedrooms", "toilets", "legal_status", "latitude", "longitude",
        "price_square", "furniture", "house_direction_x", "house_direction_y",
        "balcony_direction_x", "balcony_direction_y","location_group"
    ]

    # Tạo một đối tượng mới chỉ chứa các khóa cần giữ lại
    filtered_entry = {key: entry[key] for key in keys_to_keep if key in entry}
    return filtered_entry

def remove_objects_with_none(entry):
    """
    Hàm loại bỏ các object khỏi danh sách nếu bất kỳ key nào trong danh sách cần kiểm tra có giá trị None.
    Args:
        data (list): Mảng các object chứa dữ liệu.
    Returns:
        list: Mảng các object đã loại bỏ các phần tử chứa giá trị None trong các key cần kiểm tra.
    """
    keys_to_check = [
        "area", "price", "bedrooms", "toilets", "legal_status", "latitude", "longitude", "furniture", "house_direction_x", "house_direction_y",
        "balcony_direction_x", "balcony_direction_y"
    ]
    if entry is None:
        return None

    if all(entry.get(key) is not None for key in keys_to_check):
        return entry
    else: return None

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
        


