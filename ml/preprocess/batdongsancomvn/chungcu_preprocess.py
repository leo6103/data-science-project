import sys
import os
import json
import pandas as pd
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from ml.preprocess.utils.json_handle import merge_data_with_paths, read_json,merge_json_files,write_json
from ml.preprocess.batdongsancomvn.attribute_handler.chungcu_attribute_handler import remove_duplicates_by_url,normalize_interim_item,normalize_process_item


apartment_raw_directory = 'data/raw/batdongsancomvn/chungcu'
list_paths_apartment =  merge_json_files(apartment_raw_directory)
apartment_raw_data = merge_data_with_paths(list_paths_apartment)
print("Number sample in apartments raw data: ",len(apartment_raw_data))



remove_duplicates_by_url(apartment_raw_data)

for i in range(len(apartment_raw_data)):
    apartment_raw_data[i] = normalize_interim_item(apartment_raw_data[i])
interim_path = "data/interim/batdongsancomvn/chungcu/interim_merged_chungcu.json"
write_json(apartment_raw_data,interim_path)

for i in range(len(apartment_raw_data)):
    apartment_raw_data[i] = normalize_process_item(apartment_raw_data[i])
apartment_raw_data = [entry for entry in apartment_raw_data if entry is not None]
preprocess_path = "data/processed/batdongsancomvn/chungcu/preprocess_merged_chungcu.csv"
df = pd.DataFrame(apartment_raw_data)
df['legal_status'] = df['legal_status'].fillna(1)

# Tính trung vị và điền giá trị thiếu cho cột 'Bedrooms'
median_bedrooms = df['bedrooms'].median()
df['bedrooms'] = df['bedrooms'].fillna(median_bedrooms)

# Tính trung vị và điền giá trị thiếu cho cột 'Toilets'
median_toilets = df['toilets'].median()
df['toilets'] = df['toilets'].fillna(median_toilets)
# Chuyển đổi list các dictionaries thành DataFrame

# Loại bỏ các hàng có giá trị NaN hoặc None trong các cột area, price, longitude, latitude
df = df.dropna(subset=['area', 'price', 'longitude', 'latitude'])
columns_to_drop = [
    'house_direction_x', 
    'house_direction_y', 
    'balcony_direction_x', 
    'balcony_direction_y', 
    'furniture'
]
df['bedrooms'] = df['bedrooms'].replace(0, 1)

# Tạo đặc trưng mới 'area_per_bedroom'
df['area_per_bedroom'] = df['area'] / df['bedrooms']

# Loại bỏ các cột
df = df.drop(columns=columns_to_drop)
df.to_csv(preprocess_path, index=False)

# In ra các key và tần suất xuất hiện
key_frequency = {}
for item in apartment_raw_data:
    if item is not None :
        for key in item.keys():
            key_frequency[key] = key_frequency.get(key, 0) + 1
print("Tần suất xuất hiện của các key trong data:")
for key, frequency in key_frequency.items():
    print(f"{key}: {frequency}/{len(apartment_raw_data)}")


# Bây giờ df là một DataFrame
missing_counts = df.isnull().sum()
print("Số lượng mẫu dữ liệu:", len(df))

print("Số lượng giá trị None hoặc NaN tại mỗi thuộc tính:")
print(missing_counts)

# Tìm giá trị xuất hiện nhiều nhất trong cột 'legal_status'
mode_legal_status = df['legal_status'].mode()

if not mode_legal_status.empty:
    # Nếu có nhiều hơn một mode, mode() sẽ trả về một Series
    print("Giá trị xuất hiện nhiều nhất của đặc trưng 'legal_status':")
    for mode in mode_legal_status:
        print(mode)
else:
    print("Cột 'legal_status' không có giá trị nào để tính mode.")

