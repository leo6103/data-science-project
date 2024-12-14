const BASE_URL = import.meta.env.VITE_BACKEND_URL;

interface ViewStatisticParams {
  price_min?: number;
  price_max?: number;
  area_min?: number;
  area_max?: number;
  price_square_min?: number;
  price_square_max?: number;
}

interface ViewStatisticResponse {
  area_min: number | null;
  area_max: number | null;
  price_min: number | null;
  price_max: number | null;
  price_square_min: number | null;
  price_square_max: number | null;
  data: Array<Record<string, any>>;
}

export const viewStatistic = async (
  params: ViewStatisticParams
): Promise<ViewStatisticResponse> => {
  const response = await fetch(`${BASE_URL}/view_statistic/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Error fetching statistics");
  }

  return response.json();
};

export const predictHousePrice = async (params: any): Promise<{ price: number }> => {
    const response = await fetch(`${BASE_URL}/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(params),
    });
  
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Error predicting house price");
    }
  
    return response.json();
};

