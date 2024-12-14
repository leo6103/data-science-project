from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
app = FastAPI()

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả các nguồn (thay "*" bằng danh sách nguồn cụ thể để bảo mật hơn)
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả các phương thức (GET, POST, ...)
    allow_headers=["*"],  # Cho phép tất cả các header
)

@app.post('/predict-house-price')
def predict_house_price(data: dict):
    _logger.info(f"Received data: {data}")
    # Xử lý dữ liệu, tính toán giá nhà dự đoán
    return {'predicted_price': 1000000}
