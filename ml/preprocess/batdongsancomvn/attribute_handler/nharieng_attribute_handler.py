from typing import List, Dict
import numpy as np

directions = ['None', 'Đông', 'Tây', 'Nam', 'Bắc', 'Đông - Nam', 'Tây - Nam', 'Đông - Bắc', 'Tây - Bắc']
N = len(directions) - 1

translation_dict = {
    "Mặt tiền": "frontage",
    "Đường vào": "access_road_width",
    "Diện tích": "area",
    "Mức giá": "price",
    "Hướng nhà": "house_direction",
    "latitude": "latitude",
    "longitude": "longitude",
    "Số phòng ngủ": "bedroom",
    "Số toilet": "toilet",
    "Pháp lý": "legal",
    "Số tầng": "floor",
    "Nội thất": "furniture",
    "Hướng ban công": "balcony_direction",
}

neccessary_key = ["frontage","area","price","longitude","latitude","bedroom","toilet","legal","floor","furniture"]




# Xử lý data từ raw sang interim
def normalize_interim_item(entry: Dict) -> Dict:
    entry = translate_key(entry)
    entry = remove_unnecessary_key(entry)
    entry = process_frontage(entry)
    entry = process_area_price(entry)
    entry = process_coordinates(entry)
    entry = process_legal(entry)
    entry = process_bedroom_toilet(entry)
    entry = process_floor(entry)
    entry = process_furniture(entry)
    return entry

# Xử lý data từ interim sang processed
def normalize_process_item(entry: Dict) -> Dict:
    entry = remove_price_deal(entry)
    if entry is None:
        return None
    entry = remove_objects_with_none(entry)
    return entry

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

def remove_unnecessary_key(entry: Dict)-> Dict:
    filtered_item = {key: entry[key] for key in neccessary_key if key in entry}
    return filtered_item

def process_frontage(entry: Dict) -> Dict:
    frontage = entry.get("frontage")
    if frontage is not None and isinstance(frontage, str):
        try:
            frontage = float(frontage.replace(" m", "").replace(",", "."))
        except ValueError:
            frontage = None
    entry["frontage"] = frontage
    return entry

def process_area_price(entry: Dict) -> Dict:
    # Xử lý key "area"
    area = entry.get("area")
    if area is not None and isinstance(area, str):
        try:
            area = area.replace(" m²", "").replace(".", "").replace(",", ".")
            area = float(area) 
        except ValueError:
            area = None  
    entry["area"] = area

    price = entry.get("price")
    if price is not None and isinstance(price, str):
        if price == "Thỏa thuận":
            price = "deal"
        else:
            try:
                price = float(price.replace(" triệu", "").replace(" tỷ", "").replace(",", "."))
                if "triệu" in entry.get("price", ""):
                    price /= 1000
                if "triệu/m²" in entry.get("price", "") and area is not None:
                    price *= area 
                    price /= 1000
            except ValueError:
                price = None
    entry["price"] = price

    return entry

def process_coordinates(entry: Dict) -> Dict:
    latitude = entry.get("latitude")
    longitude = entry.get("longitude")
    if latitude is not None and longitude is not None:
        entry["latitude"] = float(latitude)
        entry["longitude"] = float(longitude)
    return entry

def process_legal(entry: Dict) -> Dict:
    legal = entry.get("legal")
    if legal is not None:
        legal = legal.lower()
        if any(keyword in legal for keyword in ["sổ đỏ", "sổ hồng", "sổ chính chủ", "sổ riêng"]):
            entry["legal"] = 1
            return entry
        elif any(keyword in legal for keyword in ["pháp lý đầy đủ", "giấy tờ đầy đủ", "pháp lý rõ ràng"]):
            entry["legal"] = 1
            return entry
        elif any(keyword in legal for keyword in ["chưa sổ", "đang chờ sổ", "hợp đồng ủy quyền"]):
            entry["legal"] = 0
            return entry
        else:
            entry["legal"] = None
            return entry
    return entry

def process_bedroom_toilet(entry: Dict) -> Dict:

    # Xử lý bedrooms
    if "bedroom" in entry and isinstance(entry["bedroom"], str):
        try:
            entry["bedroom"] = int(entry["bedroom"].split()[0])
        except (ValueError, IndexError):
            entry["bedroom"] = None

    # Xử lý toilets
    if "toilet" in entry and isinstance(entry["toilet"], str):
        try:
            entry["toilet"] = int(entry["toilet"].split()[0])
        except (ValueError, IndexError):
            entry["toilet"] = None

    return entry

def process_floor(entry: Dict) -> Dict:
    if "floor" in entry and isinstance(entry["floor"], str):
        try:
            entry["floor"] = int(entry["floor"].split()[0])
        except (ValueError, IndexError):
            entry["floor"] = None
    return entry

def process_furniture(entry: Dict) -> Dict:
    furniture = entry.get("furniture")
    if furniture is not None:
        furniture = furniture.lower()
        if "không nội thất" in furniture:
            entry["furniture"] = 0
            return entry
        elif "cơ bản" in furniture:
            entry["furniture"] = 1
            return entry
        elif "đầy đủ" in furniture or "full nội thất" in furniture:
            entry["furniture"] = 2
            return entry
        elif "cao cấp" in furniture or "xịn sò" in furniture or "sang trọng" in furniture or "nhập khẩu" in furniture:
            entry["furniture"] = 3
            return entry
        else:
            entry["furniture"] = None
            return entry

def remove_price_deal(entry: Dict)-> Dict:
    if  entry.get("price") == "deal":
        return None
    return entry
key_to_check = ["area","price","longitude","latitude"]

def remove_objects_with_none(entry: Dict)-> Dict:
    if entry is None:
            return None

    if any(entry.get(key) is None for key in key_to_check):
            return None
    return entry

