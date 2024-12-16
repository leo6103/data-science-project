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
    "longitude": "longitude"
}
key_to_check = ["area","price","longitude","latitude"]
neccessary_key = ["frontage", "access_road_width","area","price","longitude","latitude"]


# Xử lí data từ raw sang interim 
def normalize_interim_item(entry: Dict) -> Dict:
    entry = translate_key(entry)
    entry = remove_unnecessary_key(entry)
    entry = process_frontage(entry)
    entry = process_access_road_width(entry)
    entry = process_area_price(entry)
    entry = process_coordinates(entry)
    return entry

# xử lí data từ interim sang preprocessed 
def normalize_process_item(entry: Dict) -> Dict:
    entry = remove_price_deal(entry)
    if entry is None:
        return None
    entry = remove_objects_with_none(entry)
    return entry

def process_frontage(entry: Dict) -> Dict:
    frontage = entry.get("frontage")
    if frontage is not None and isinstance(frontage, str):
        try:
            frontage = float(frontage.replace(" m", "").replace(",", "."))
        except ValueError:
            frontage = None
    entry["frontage"] = frontage
    return entry

def process_access_road_width(entry: Dict) -> Dict:
    access_road_width = entry.get("access_road_width")
    if access_road_width is not None and isinstance(access_road_width, str):
        try:
            access_road_width = float(access_road_width.replace(" m", "").replace(",", "."))
        except ValueError:
            access_road_width = None
    entry["access_road_width"] = access_road_width
    return entry

def process_area_price(entry: Dict) -> Dict:
    # Xử lý key "area"
    area = entry.get("area")
    if area is not None and isinstance(area, str):
        try:
            area = float(area.replace(" m²", "").replace(".", "").replace(",", "."))
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
    
def translate_key(entry: Dict) -> Dict:
    translated_entry = {}
    
    for key, value in entry.items():
        new_key = translation_dict.get(key, key)
        translated_entry[new_key] = value
    
    return translated_entry

def remove_unnecessary_key(entry: Dict)-> Dict:
    filtered_item = {key: entry[key] for key in neccessary_key if key in entry}
    return filtered_item

def remove_duplicates_by_url(data):
    seen_urls = set()
    unique_data = []

    for item in data:
        url = item.get('url')
        if url not in seen_urls:
            unique_data.append(item)
            seen_urls.add(url)
    return unique_data

def process_coordinates(entry: Dict) -> Dict:
    latitude = entry.get("latitude")
    longitude = entry.get("longitude")
    if latitude is not None and longitude is not None:
        entry["latitude"] = float(latitude)
        entry["longitude"] = float(longitude)
    return entry



def process_house_directions(entry: Dict) -> Dict:
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
    return entry


def remove_price_deal(entry: Dict)-> Dict:
    if  entry.get("price") == "deal":
        return None
    return entry

def remove_objects_with_none(entry: Dict)-> Dict:
    if entry is None:
            return None

    if any(entry.get(key) is None for key in key_to_check):
            return None
    return entry

# làm đầy bằng trung vị
def fill_with_mean(data):
    frontages = [entry['frontage'] for entry in data if entry.get('frontage') is not None]
    access_widths = [entry['access_road_width'] for entry in data if entry.get('access_road_width') is not None]

    mean_frontage = np.mean(frontages)
    mean_access_width = np.mean(access_widths)

    for entry in data:
        if entry.get('frontage') is None:
            entry['frontage'] = mean_frontage
        if entry.get('access_road_width') is None:
            entry['access_road_width'] = mean_access_width
    return data
