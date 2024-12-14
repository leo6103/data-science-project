
import sys
import os
import json
import pandas as pd
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from ml.preprocess.utils.json_handle import merge_data_with_paths, read_json,merge_json_files,write_json
from ml.preprocess.batdongsancomvn.attribute_handler.nharieng_attribute_handler import remove_duplicates_by_url,normalize_interim_item,normalize_process_item

raw_directory = 'data/raw/batdongsancomvn/nharieng'

# Đọc dữ liệu thô 
list_paths =  merge_json_files(raw_directory)
raw_data = merge_data_with_paths(list_paths)

# Loại bỏ các data bị trùng lặp dữ liệu 
remove_duplicates_by_url(raw_data)

# Chuẩn hoá dữ liệu và lưu về dạng trung gian
for i in range(len(raw_data)):
    raw_data[i] = normalize_interim_item(raw_data[i])
raw_data = [entry for entry in raw_data if entry is not None]
    
# lưu về dạng trung gian
interim_path = "data/interim/batdongsancomvn/nharieng/interim_merged_nharieng.json"
write_json(raw_data, interim_path)


frontage_values = set()
for item in raw_data:
    if item is not None :
        if item.get("furniture") is not None:
            frontage_values.add(item.get("furniture"))
print("Các giá trị khác nhau của thuộc tính diện tích:")
print(frontage_values)

# for item in raw_data:
#     if item.get("area") == 3:
#         print(item)

# In ra các key và tần suất xuất hiện
key_frequency = {}
for item in raw_data:
    if item is not None :
        for key in item.keys():
            key_frequency[key] = key_frequency.get(key, 0) + 1
print("Tần suất xuất hiện của các key trong data:")
for key, frequency in key_frequency.items():
    print(f"{key}: {frequency} lần")
