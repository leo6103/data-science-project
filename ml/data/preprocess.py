import os
import json

def merge_json(input_directory):
    # Danh sách để lưu trữ tất cả dữ liệu từ các file JSON
    data_list = []

    # Duyệt qua tất cả các file trong thư mục
    for filename in os.listdir(input_directory):
        if filename.endswith('.json'):
            file_path = os.path.join(input_directory, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                    data_list.append(data)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from file {filename}")

    # Ghi dữ liệu gộp vào một file JSON mới
    print("merged success")
    return data_list


def remove_duplicates_by_url(data):
    seen_urls = set()  # Tạo một tập hợp để lưu trữ các URL đã gặp
    unique_data = []  # Danh sách chứa các phần tử có URL duy nhất

    for item in data:
        if isinstance(item, dict):  # Kiểm tra xem item có phải là dict không
            url = item.get('url')  # Lấy giá trị URL từ từng phần tử

            # Nếu URL chưa tồn tại trong tập hợp, thêm phần tử vào danh sách kết quả
            if url not in seen_urls:
                unique_data.append(item)
                seen_urls.add(url)  # Đánh dấu URL đã xuất hiện
        else:
            print(f"Item không phải là dict: {item}")
    print(data)
    print("remove_duplicates_by_url success")

    return unique_data


def translate_keys(data):
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
    translated_data = [{translation_dict.get(key, key): value for key, value in entry.items()} for entry in data]
    print("translate_keys success")
    return translated_data


# Hàm để chuyển đổi "bedrooms" và "toilets" từ chuỗi thành số nguyên
def convert_bedrooms_toilets_to_int(data):
    for entry in data:
        if "area" in entry and isinstance(entry["area"], str):
            area_value = entry["area"].split()[0].replace(",", ".")  # Thay thế dấu phẩy bằng dấu chấm
            entry["area"] = float(area_value)  # Chuyển thành số thực
        # Chuyển đổi số phòng ngủ
        if "bedrooms" in entry and isinstance(entry["bedrooms"], str):
            entry["bedrooms"] = int(entry["bedrooms"].split()[0])  # Lấy số đầu tiên và chuyển thành số nguyên

        # Chuyển đổi số toilet
        if "toilets" in entry and isinstance(entry["toilets"], str):
            entry["toilets"] = int(entry["toilets"].split()[0])  # Lấy số đầu tiên và chuyển thành số nguyên
    print("convert_bedrooms_toilets_to_int success")
    return data


# Hàm để chuyển đổi giá trị của "price"
def convert_price(data):
    for entry in data:
        area = entry.get("area", None)  # Lấy giá trị diện tích
        price = entry.get("price", None)  # Lấy giá trị price

        # Nếu giá là "Thỏa thuận"
        if price == "Thỏa thuận":
            entry["price"] = "deal"
            entry["price_square"] = "deal"

        # Nếu giá có dạng "X triệu/m²"
        elif isinstance(price, str) and "triệu/m²" in price:
            price_per_sqm = float(price.split()[0].replace(",", "."))  # Lấy số trước "triệu/m²" và chuyển thành float
            entry["price_square"] = price_per_sqm  # Lưu giá trị gốc vào "price_square"
            if area is not None:
                entry["price"] = price_per_sqm * area  # Tính giá tổng

        # Nếu giá có dạng "X tỷ"
        elif isinstance(price, str) and "tỷ" in price:
            total_price_billion = float(price.split()[0].replace(",", "."))  # Lấy số trước "tỷ" và chuyển thành float
            total_price = total_price_billion * 1e3  # Chuyển từ tỷ sang triệu
            entry["price_square"] = total_price / area if area else None  # Tính giá trên m² và lưu vào "price_square"
            entry["price"] = total_price  # Lưu giá tổng vào "price"
    print("convert_price success")
    return  data

def write_json_file(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print("write_json_file success")

if __name__ == '__main__':
    input_directory = 'data/raw/batdongsancomvn/chungcu'
    output_file = 'data/processed/batdongsancomvn/chungcu/merged_chungcu.json'
    data = merge_json(input_directory)
    data = remove_duplicates_by_url(data)
    data = translate_keys(data)
    data = convert_bedrooms_toilets_to_int(data)
    data = convert_price(data)
    write_json_file(data,output_file)


