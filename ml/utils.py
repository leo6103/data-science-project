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
    
    

def prepare_data_dat(df: pd.DataFrame) -> pd.DataFrame:

    df['z_score'] = np.abs(stats.zscore(df['price']))
    df = df[df['z_score'] <= 3]
    df = df.drop(columns=['z_score'])
    print("Số lượng mẫu sau khi lọc ngoại lai:", len(df))

    # Biến đổi logarit cho cột giá và diẹn tích
    epsilon = 1e-10
    df['log_area'] = np.log(df['area'] + epsilon)
    df['log_price'] = np.log(df['price'] + epsilon)
    variables = ['frontage', 'access_road_width', 'area']
    for var in variables:
        Q1 = df[var].quantile(0.25)
        Q3 = df[var].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Lọc dữ liệu chỉ giữ các giá trị trong ngữ nghừa
        df = df[(df[var] >= lower_bound) & (df[var] <= upper_bound)]
    print("Số lượng mẫu sau khi lọc ngoại lai:", len(df))
    
    X = df.drop(columns=['price','area','log_price']).values
    y = df['log_price'].values
    
    return X,y


def prepare_data_chungcu(df: pd.DataFrame) -> tuple:
    # Chuyển đổi các giá trị không phải số trong cột 'price' thành NaN
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    
    # Loại bỏ các giá trị NaN trong cột 'price'
    df = df.dropna(subset=['price'])
    
    # Tính z-score cho cột 'price'
    df['z_score'] = np.abs(stats.zscore(df['price']))
    
    # Lọc các giá trị ngoại lai dựa trên z-score
    df = df[df['z_score'] <= 3]
    df = df.drop(columns=['z_score'])
    print("Số lượng mẫu sau khi lọc ngoại lai:", len(df))

    # Biến đổi logarit cho cột giá và diện tích
    epsilon = 1e-10
    df['log_area'] = np.log(df['area'] + epsilon)
    df['log_price'] = np.log(df['price'] + epsilon)
    
    # In ra các giá trị của cột 'log_area'
    print("Column names:")
    test = df.drop(columns=['price', 'log_price', 'area'])
    for column in test.columns:
        print(f"- {column}")
    
    # Tạo X và y
    X = df.drop(columns=['price', 'log_price', 'area']).values
    y = df['log_price'].values

    return X, y


def prepare_data_nharieng(df: pd.DataFrame) -> pd.DataFrame:
    df['z_score'] = np.abs(stats.zscore(df['price']))
    df = df[df['z_score'] <= 3]
    df = df.drop(columns=['z_score'])
    print("Số lượng mẫu sau khi lọc ngoại lai:", len(df))

    # Biến đổi logarit cho cột giá và diẹn tích
    epsilon = 1e-10
    df['log_area'] = np.log(df['area'] + epsilon)
    df['log_price'] = np.log(df['price'] + epsilon)

    print("Column names:")
    test = df.drop(columns=['price','log_price','area','price_square','location_group','furniture'])
    for column in test.columns:
        print(f"- {column}")
    X = df.drop(columns=['price','log_price','area','price_square','location_group']).values
    y = df['log_price'].values

    return X,y

def prepare_data_predict(X):
    """
    Chuẩn bị dữ liệu từ JSON để dự đoán.
    :param X: JSON đầu vào
    :return: DataFrame đã chuẩn bị cho mô hình
    """

    # Kiểm tra và chuyển đổi JSON thành DataFrame
    if isinstance(X, dict):
        X = pd.DataFrame([X])  # Chuyển dict thành DataFrame (1 hàng)
    elif isinstance(X, list):
        X = pd.DataFrame(X)

    # Kiểm tra property_type
    if 'property_type' not in X.columns:
        raise ValueError("Dữ liệu đầu vào thiếu 'property_type'.")

    property_type = X.loc[0, 'property_type']  # Lấy giá trị property_type từ dòng đầu tiên

    # Xử lý từng loại property_type
    if property_type == 'land':
        if 'price' not in X.columns:
            raise ValueError("Dữ liệu 'land' cần có cột 'price'.")
        epsilon = 1e-10
        X['log_price'] = np.log(X['price'] + epsilon)

    elif property_type == 'house':
        if 'price' not in X.columns:
            raise ValueError("Dữ liệu 'house' cần có cột 'price'.")
        X['log_price'] = np.log(X['price'] + epsilon)

    elif property_type == 'apartment':
        epsilon = 1e-10
        print("Area values and types:", X['area'].head(), X['area'].dtype)
        # Tính log_area
        X['log_area'] = np.log(X['area'].values + epsilon)
        print("log_area:", X['log_area'])
        print("area:", X['area'])
        X= X.drop(columns=['area'])

        # Loại bỏ các cột không cần thiết
        if 'property_type' in X.columns:
            X = X.drop(columns=['property_type'])

        # Xử lý hướng nhà và hướng ban công
        if 'house_direction' in X.columns and 'balcony_direction' in X.columns:
            house_direction = X['house_direction'].values
            balcony_direction = X['balcony_direction'].values
            X = X.drop(columns=['house_direction', 'balcony_direction'])
            print("house_direction:", house_direction)
            print("balcony_direction:", balcony_direction)

            # Giả sử convert_direction() trả về 2 giá trị x và y
            X['house_direction_x'], X['house_direction_y'] = convert_direction(house_direction)
            X['balcony_direction_x'], X['balcony_direction_y'] = convert_direction(balcony_direction)

        # Chuyển đổi lat và lng thành latitude và longitude
        if 'lat' in X.columns and 'lng' in X.columns:
            X['latitude'] = X['lat']
            X['longitude'] = X['lng']
            X = X.drop(columns=['lat', 'lng'])

        # Debug thông tin các cột
        print("Column names after processing:")
        for column in X.columns:
            print(f"- {column}")
        print("X after processing:", X)

    else:
        raise ValueError("Invalid property_type. Must be 'land', 'house', or 'apartment'.")

    return X

def convert_direction(direction):
    directions = ['e', 'w', 's', 'n', 'se', 'sw', 'ne', 'nw']
    N = len(directions) - 1
    def circular_encoding(index, N):
        angle = 2 * np.pi * index / N
        x = np.cos(angle)
        y = np.sin(angle)
        return x, y
    
    if direction == 'None':
        x, y = 0, 0
    else:
        index = directions.index(direction)
        x, y = circular_encoding(index - 1, N)
    return x, y

def prepare_data_test_predict(df: pd.DataFrame) -> pd.DataFrame:
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    
    # Loại bỏ các giá trị NaN trong cột 'price'
    df = df.dropna(subset=['price'])
    epsilon = 1e-10
    df['log_area'] = np.log(df['area'] + epsilon)
    df['log_price'] = np.log(df['price'] + epsilon)
    # in ra các giá trị của cột log_area

    print("Column names:")
    test = df.drop(columns=['price','log_price','area'])
    for column in test.columns:
        print(f"- {column}")
    X = df.drop(columns=['price','log_price'])
    y = df['log_price'].values
    return X, y