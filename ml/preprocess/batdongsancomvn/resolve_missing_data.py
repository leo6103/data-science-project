import ml.preprocess.batdongsancomvn.attribute_handler.chungcu_attribute_handler as chungcu_attribute_handler
import ml.preprocess.utils.json_handler as json_handler

file_path = 'data/processed/batdongsancomvn/chungcu/merged_1_743.json'
data = json_handler.read_json(file_path)

print('aa')
resolver = json_handler.BaseMissingDataResolver(file_path, chungcu_attribute_handler.is_missing_data, chungcu_attribute_handler.normalize_item)