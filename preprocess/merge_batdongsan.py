import os
import json

def merge_json_files(directory, output_file):
    # Danh sách để lưu tất cả các đối tượng JSON có location chứa "Hà Nội"
    filtered_json_objects = []

    # Duyệt qua tất cả các tệp trong thư mục
    for filename in os.listdir(directory):
        if filename.endswith(".json"):  # Chỉ xử lý các tệp .json
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    # Đọc nội dung của tệp
                    json_data = json.load(file)
                    # Lọc các object có thuộc tính "location" chứa "Hà Nội"
                    for obj in json_data:
                        if 'location' in obj and 'Hà Nội' in obj['location']:
                            filtered_json_objects.append(obj)  # Thêm vào danh sách nếu phù hợp
                except json.JSONDecodeError as e:
                    print(f"Error decoding {filename}: {e}")
    
    print(f"Total objects with 'Hà Nội' location: {len(filtered_json_objects)}")
    # Ghi tất cả các đối tượng JSON đã được lọc vào một tệp mới
    with open(output_file, 'w', encoding='utf-8') as output_file:
        json.dump(filtered_json_objects, output_file, ensure_ascii=False, indent=4)
    
    print(f"Merge and filtering completed. Output file: {output_file.name}")

# Thay thế đường dẫn đến thư mục chứa các file .json của bạn
directory = 'data/raw/batdongsancomvn/chungcu'
output_file = 'data/raw/batdongsancomvn/chungcu/merged/1-10.json'

merge_json_files(directory, output_file)
