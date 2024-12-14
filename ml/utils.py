import json
from typing import List, Dict
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans


def read_json (file_path: str) -> List[Dict]:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    return data

def write_json(data: list, output_path: str):
    with open(output_path, 'w', encoding='utf-8') as output_file:
        json.dump(data, output_file, indent=4)
    
def read_csv (file_path: str) -> List[Dict]:
    try:
        print("Start reading file...")
        df = pd.read_csv(file_path)
        df = df.astype(np.float32) 
    except FileNotFoundError:
        print(f"Error: File '{file_path}' không tồn tại.")
    except pd.errors.EmptyDataError:
        print(f"Error: File '{file_path}' không chứa dữ liệu.")
    except pd.errors.ParserError:
        print(f"Error: File '{file_path}' không đúng định dạng CSV.")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
    return df 
    
    

def prepare_data1(df: pd.DataFrame) -> pd.DataFrame:
    # encoder = OneHotEncoder(sparse_output=False)
    # encoded_location_group = encoder.fit_transform(df[['location_group']])
    df['z_score'] = np.abs(stats.zscore(df['price']))
    df = df[df['z_score'] <= 3]
    df = df.drop(columns=['z_score'])
    print("Số lượng mẫu sau khi lọc ngoại lai:", len(df))
    # df = df.drop_duplicates(subset=['price_square', 'longitude', 'latitude'])
    # print("Số lượng mẫu sau khi loại bỏ các dòng trùng lặp:", len(df))

    # Biến đổi logarit cho cột giá và diẹn tích
    epsilon = 1e-10
    df['log_area'] = np.log(df['area'] + epsilon)
    df['log_price'] = np.log(df['price'] + epsilon)
    # df = pd.get_dummies(df, columns=['legal_status', 'furniture'], drop_first=True)
    kmeans = KMeans(n_clusters=5, random_state=42)
    # df['location_cluster'] = kmeans.fit_predict(df[['latitude', 'longitude']])
    df['area_per_room'] = df['log_area'] / df['bedrooms']
    print("Column names:")
    for column in df.columns:
        print(f"- {column}")
    X = df.drop(columns=['price','log_price','area','price_square','legal_status','location_group','furniture']).values
    y = df['log_price'].values

    return X,y

def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    df['z_score'] = np.abs(stats.zscore(df['price']))
    df = df[df['z_score'] <= 3]
    df = df.drop(columns=['z_score'])
    print("Số lượng mẫu sau khi lọc ngoại lai:", len(df))

    # Biến đổi logarit cho cột giá và diẹn tích
    epsilon = 1e-10
    df['log_area'] = np.log(df['area'] + epsilon)
    df['log_price'] = np.log(df['price'] + epsilon)

    for column in df.columns:
        print(f"- {column}")
    X = df.drop(columns=['price','log_price','area']).values
    y = df['log_price'].values

    return X,y

def prepare_data_predict(df: pd.DataFrame, reference_columns: list = None) -> pd.DataFrame:
    epsilon = 1e-10
    # df['z_score'] = np.abs(stats.zscore(df['price']))
    # df = df[df['z_score'] <= 3]
    # df = df.drop(columns=['z_score'])
    # print("Số lượng mẫu sau khi lọc ngoại lai:", len(df))
    # Tạo log_area và log_price
    df['log_area'] = np.log(df['area'] + epsilon)
    df['log_price'] = np.log(df['price'] + epsilon)
    
    # One-hot encoding cho legal_status và furniture
    # df = pd.get_dummies(df, columns=['legal_status', 'furniture'], drop_first=True)
    
    # KMeans clustering
    # if len(df) >= 5:
    #     n_clusters = 5
    #     kmeans = KMeans(n_clusters, random_state=42)
    #     df['location_cluster'] = kmeans.fit_predict(df[['latitude', 'longitude']])
    # else:
    #     n_clusters = 1
    #     kmeans = KMeans(n_clusters, random_state=42)
    #     df['location_cluster'] = kmeans.fit_predict(df[['latitude', 'longitude']])
    
    # Feature engineering
    df['area_per_room'] = df['log_area'] / df['bedrooms']
    
    # Đảm bảo số cột khớp với quá trình huấn luyện
    if reference_columns is not None:
        # Thêm cột bị thiếu
        for col in reference_columns:
            if col not in df.columns:
                df[col] = 0
        # Loại bỏ cột thừa
        df = df[reference_columns]

    print("Column names in predict data:")
    for column in df.columns:
        print(f"- {column}")
    
    # Chuẩn bị X và y
    X = df.drop(columns=['price', 'log_price', 'area','legal_status','furniture']).values
    y = df['log_price'].values if 'log_price' in df.columns else None
    return X, y