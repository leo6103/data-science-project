import sys
import os
import json
import pandas as pd
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from ml.preprocess.utils.json_handle import merge_data_with_paths, read_json,merge_json_files,write_json
from ml.preprocess.batdongsancomvn.attribute_handler.dat_attribute_handler import fill_with_mean,remove_duplicates_by_url,normalize_interim_item,normalize_process_item

raw_directory = 'data/raw/batdongsancomvn/dat'

# Đọc dữ liệu thô 
list_paths =  merge_json_files(raw_directory)
raw_data = merge_data_with_paths(list_paths)

# Loại bỏ các data bị trùng lặp dữ liệu 
remove_duplicates_by_url(raw_data)

# Viết đoạn code in ra tất cả các giá trị khác nhau của thuộc tính Mặt tiền
frontage_values = set()
for item in raw_data:
    if item.get("Mặt tiền") is not None:
        frontage_values.add(item.get("Mặt tiền"))
print("Các giá trị khác nhau của thuộc tính Mặt tiền:")
print(frontage_values)

# Chuẩn hoá dữ liệu và lưu về dạng trung gian 
for i in range(len(raw_data)):
    raw_data[i] = normalize_interim_item(raw_data[i])
interim_path = "data/interim/batdongsancomvn/dat/interim_merged_data.json"
write_json(raw_data,interim_path)
sum = 0
# for item in raw_data:
#     if item.get("frontage") is not None and item.get("frontage") >100:
#         sum+=1
#         print(item.get("frontage"))
# print(sum)

# Làm đầy frontage và access road width bằng trung vị
raw_data = fill_with_mean(raw_data)

# Chuẩn hoá dữ liệu để train và lưu
for i in range(len(raw_data)):
    raw_data[i] = normalize_process_item(raw_data[i])
raw_data = [entry for entry in raw_data if entry is not None]
preprocess_path = "data/processed/batdongsancomvn/dat/preprocess_merged_dat.csv"
df = pd.DataFrame(raw_data)
df.to_csv(preprocess_path, index=False)



# In ra các key và tần suất xuất hiện
key_frequency = {}
for item in raw_data:
    for key in item.keys():
        key_frequency[key] = key_frequency.get(key, 0) + 1
print("Tần suất xuất hiện của các key trong data:")
for key, frequency in key_frequency.items():
    print(f"{key}: {frequency} lần")






