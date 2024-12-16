
import numpy as np
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
from contextlib import asynccontextmanager
import joblib
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from ml.models.RandomForest import RandomForest

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
_logger = logging.getLogger(__name__)

# Lifespan quản lý khởi động và tắt server
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load model
    _logger.info("Loading model...")
    model_apartment = RandomForest("rf_model","apartment")
    model_apartment.load_model()
    # model_land = RandomForest("rf_model","land")
    # model_land.load_model()
    # model_house = RandomForest("rf_model","house")
    # model_house.load_model()
    app.state.model_apartment = model_apartment
    # app.state.model_land = model_land
    # app.state.model_house = model_house
    _logger.info("Model loaded successfully.")
    yield  
    _logger.info("Shutting down server...")
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = "./data.json"

async def read_json_file(file_path: str):
    loop = asyncio.get_event_loop()
    with open(file_path, "r") as file:
        data = await loop.run_in_executor(None, file.read)
        return json.loads(data)



@app.post("/predict/")
async def predict(request: Request):
    epsilon = 1e-10
    data = await request.json()
    _logger.info(f"Request data: {data}")
    if data.get('property_type') == 'land':
        model = app.state.model_land
    elif data.get('property_type') == 'house':
        model = app.state.model_house
    elif data.get('property_type') == 'apartment':
        model = app.state.model_apartment
    else:
        return {"error": "Invalid property_type. Must be 'land', 'house', or 'apartment'."}
    log_price = model.predict(data)
    price = np.exp(log_price - epsilon)
    if isinstance(price, np.ndarray):
        price = price.tolist()
    _logger.info(f"Predicted price: {price}")
    response = {
        "price": price
    }
    return response


@app.post("/view_statistic/")
async def view_statistic(request: Request):
    data = await request.json()
    _logger.info(f"Request data: {data}")
    property_type = data.get('property_type')

    if property_type == 'land':
        path = DATA_PATH
    elif property_type == 'house':
        path = DATA_PATH
    else:
        path = DATA_PATH

    properties = await read_json_file(path)

    price_min = data.get("price_min")
    price_max = data.get("price_max")
    area_min = data.get("area_min")
    area_max = data.get("area_max")
    price_square_min = data.get("price_square_min")
    price_square_max = data.get("price_square_max")

    filtered_properties = [
        prop for prop in properties
        if (price_min is None or prop.get("price") >= price_min) and
           (price_max is None or prop.get("price") <= price_max) and
           (area_min is None or prop.get("area") >= area_min) and
           (area_max is None or prop.get("area") <= area_max) and
           (price_square_min is None or prop.get("price_square") >= price_square_min) and
           (price_square_max is None or prop.get("price_square") <= price_square_max)
    ]

    if not filtered_properties:
        raise HTTPException(status_code=404, detail="No properties found matching the criteria")

    computed_area_min = min(prop["area"] for prop in filtered_properties) if filtered_properties else None
    computed_area_max = max(prop["area"] for prop in filtered_properties) if filtered_properties else None
    computed_price_min = min(prop["price"] for prop in filtered_properties) if filtered_properties else None
    computed_price_max = max(prop["price"] for prop in filtered_properties) if filtered_properties else None
    computed_price_square_min = min(prop["price_square"] for prop in filtered_properties) if filtered_properties else None
    computed_price_square_max = max(prop["price_square"] for prop in filtered_properties) if filtered_properties else None

    return {
        "area_min": computed_area_min,
        "area_max": computed_area_max,
        "price_min": computed_price_min,
        "price_max": computed_price_max,
        "price_square_min": computed_price_square_min,
        "price_square_max": computed_price_square_max,
        "total_count": len(filtered_properties),
        "data": filtered_properties
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
