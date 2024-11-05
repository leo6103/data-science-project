import json
from typing import List, Dict, Callable


def read_json(file_path: str) -> List[Dict]:
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    return data


def merge_data_with_paths(path_list: List[str]) -> List[Dict]:
    merged_data = []

    for path in path_list:
        try:
            with open(path, "r") as file:
                data = json.load(file)
                merged_data.extend(data)
        except FileNotFoundError:
            print(f"File không tồn tại: {path}")
        except json.JSONDecodeError:
            print(f"File không đúng định dạng JSON: {path}")

    print(f'Total items : {len(merged_data)}')
    
    return merged_data


def write_json(data: list, output_path: str):
    with open(output_path, 'w') as output_file:
        json.dump(data, output_file, indent=4)


def remove_duplicated_data_with_key(data: List[Dict], key: str) -> List[Dict]:
    seen_vals = set()
    unique_data = []

    for item in data:
        val = item.get(key)

        if val not in seen_vals:
            unique_data.append(item)
            seen_vals.add(val)

    print(f'Removed duplicated data, number of items : {len(unique_data)}')


class BaseMissingDataResolver():
    def __init__(
        self,
        file_path: str,
        is_missing: Callable[[Dict], bool], # check if a data is missing ?
        resolve_item: Callable[[Dict], Dict] # Resolve and return fulfilled version of item
    ):
        self.file_path = file_path
        self.is_missing = is_missing
        self.resolve_item = resolve_item
    
    def run(self):
        data = read_json(self.file_path)

        mising_num = 0
        for item in data:
            if self.is_missing(item):
                mising_num += 1
                item = self.item_resolver

        print(f'Total missing data : {mising_num}')
        write_json(data, self.file_path)
