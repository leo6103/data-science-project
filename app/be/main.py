from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
_logger = logging.getLogger(__name__)

app = FastAPI()

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
    data = await request.json()
    _logger.info(f"Request data: {data}")
    response = {
        "price": 4.6 * 10e9
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
