import React, { useState } from "react";
import { viewStatistic } from "../services/apiService";
import { useMode } from "../context/ModeContext";

interface ViewStatisticParams {
  property_type?: string;
  price_min?: number;
  price_max?: number;
  area_min?: number;
  area_max?: number;
  price_square_min?: number;
  price_square_max?: number;
}

const StatisticForm: React.FC = () => {
  const [params, setParams] = useState<ViewStatisticParams>({
    property_type: "land",
    price_min: 3000,
    price_max: 6000,
    area_min: 50,
    area_max: 100,
    price_square_min: 60,
    price_square_max: 80,
  });
  const { setStatistics } = useMode();
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setParams((prev) => ({
      ...prev,
      [name]: value === "" ? undefined : isNaN(Number(value)) ? value : Number(value),
    }));
  };

  const resetFields = () => {
    setParams({
      property_type: "land",
      price_min: undefined,
      price_max: undefined,
      area_min: undefined,
      area_max: undefined,
      price_square_min: undefined,
      price_square_max: undefined,
    });
    setError(null);
    setStatistics([]);
  };

    const calculateColor = (value: number, min: number, max: number): string => {
        const clampedValue = Math.max(min, Math.min(value, max));


        const ratio = (clampedValue - min) / (max - min);


        const red = Math.round(255 * ratio);

        return `rgb(${red}, 0, 100)`;
    };

  const fetchStatistics = async () => {
    try {
      const result = await viewStatistic(params);
      const minPriceSquare = params.price_square_min || 0;
      const maxPriceSquare = params.price_square_max || 100;

      const dataWithColors = result.data.map((item: any) => ({
        ...item,
        color: calculateColor(item.price_square, minPriceSquare, maxPriceSquare),
      }));

      setStatistics(dataWithColors);
      setError(null);
    } catch (err: any) {
      setError(err.message);
      setStatistics([]);
    }
  };

  return (
    <div className="p-6 bg-gray-50 rounded-md shadow-md max-w-lg mx-auto">
      <h1 className="text-xl font-bold text-gray-700 mb-4">Statistics Viewer</h1>
      <div className="space-y-4">
        <div>
          <label className="block text-gray-600 font-medium mb-2">Property Type:</label>
          <select
            name="property_type"
            value={params.property_type || ""}
            onChange={handleChange}
            className="w-full border border-gray-300 rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="land">Land</option>
            <option value="apartment">Apartment</option>
            <option value="house">House</option>
          </select>
        </div>

        {["price_min", "price_max", "area_min", "area_max", "price_square_min", "price_square_max"].map(
          (field) => (
            <div key={field}>
              <label
                className="block text-gray-600 font-medium mb-2"
                htmlFor={field}
              >
                {field
                  .replace("_", " ")
                  .replace(/(^|\s)\S/g, (t) => t.toUpperCase())}:
              </label>
              <input
                type="number"
                name={field}
                id={field}
                value={params[field as keyof ViewStatisticParams] || ""}
                onChange={handleChange}
                className="w-full border border-gray-300 rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          )
        )}

        <div className="flex justify-between mt-4">
          <button
            onClick={resetFields}
            className="bg-gray-200 text-gray-700 font-medium py-2 px-4 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400"
          >
            Reset
          </button>
          <button
            onClick={fetchStatistics}
            className="bg-primary text-white font-medium py-2 px-4 rounded-md hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
          >
            Fetch Statistics
          </button>
        </div>
      </div>

      {error && <p className="text-red-500 font-medium mt-4">{error}</p>}
    </div>
  );
};

export default StatisticForm;
