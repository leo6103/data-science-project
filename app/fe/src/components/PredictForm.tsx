import React, { useState } from "react";
import { predictHousePrice } from "../services/apiService";
import { useMode } from "../context/ModeContext";

const directions = [
  { label: "Đông", value: "e" },
  { label: "Tây", value: "w" },
  { label: "Nam", value: "s" },
  { label: "Bắc", value: "n" },
  { label: "Đông - Nam", value: "se" },
  { label: "Tây - Nam", value: "sw" },
  { label: "Đông - Bắc", value: "ne" },
  { label: "Tây - Bắc", value: "nw" },
];

const furnitureOptions = [
  { label: "Không nội thất", value: 0 },
  { label: "Nội thất cơ bản", value: 1 },
  { label: "Đầy đủ nội thất", value: 2 },
  { label: "Nội thất cao cấp", value: 3 },
];

const legalStatusOptions = [
  { label: "Đang chờ sổ", value: 0 },
  { label: "Sổ đỏ", value: 1 },
  { label: "Đầy đủ sẵn sàng giao dịch", value: 2 },
];

interface PredictParams {
  property_type: string;
  area?: number;
  legal_status?: number;
  house_direction?: string;
  bedrooms?: number;
  toilets?: number;
  furniture?: number;
  balcony_direction?: string;
  frontage?: number;
  access_road_width?: number;
}

const PredictForm: React.FC = () => {
  const { marker } = useMode();
  const [params, setParams] = useState<PredictParams>({ property_type: "apartment" });
  const [error, setError] = useState<Record<string, string>>({});
  const [result, setResult] = useState<number | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setParams((prev) => ({
      ...prev,
      [name]: value === "" ? undefined : isNaN(Number(value)) ? value : Number(value),
    }));
  };

  const resetFields = () => {
    setParams({ property_type: "apartment" });
    setError({});
    setResult(null);
  };

  const validateFields = () => {
    const newErrors: Record<string, string> = {};
    if (!params.area) newErrors.area = "Diện tích là bắt buộc.";
    if (!params.legal_status) newErrors.legal_status = "Tình trạng pháp lý là bắt buộc.";
    if (!params.house_direction) newErrors.house_direction = "Hướng nhà là bắt buộc.";
    if (params.property_type !== "land" && !params.bedrooms)
      newErrors.bedrooms = "Số phòng ngủ là bắt buộc.";
    if (params.property_type !== "land" && !params.toilets)
      newErrors.toilets = "Số nhà vệ sinh là bắt buộc.";
    if ((params.property_type === "land" || params.property_type === "house") && !params.frontage)
      newErrors.frontage = "Chiều dài mặt tiền là bắt buộc.";
    if ((params.property_type === "land" || params.property_type === "house") && !params.access_road_width)
      newErrors.access_road_width = "Chiều rộng đường vào là bắt buộc.";
    if (!marker) newErrors.map = "Vui lòng chọn vị trí trên bản đồ.";

    setError(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const predict = async () => {
    if (!validateFields()) return;

    try {
      const result = await predictHousePrice({ ...params, ...marker });
      setResult(result.price);
      setError({});
    } catch (err: any) {
      setError({ api: err.message });
    }
  };

  const renderField = (label: string, name: string, type: "number" | "select", options?: any[]) => {
    return (
      <div>
        <label className={`block text-gray-600 font-medium mb-2 ${error[name] ? "text-red-500" : ""}`}>
          {label}:
        </label>
        {type === "number" ? (
          <input
            type="number"
            name={name}
            value={params[name as keyof PredictParams] || ""}
            onChange={handleChange}
            className={`w-full border rounded-md px-4 py-2 ${
              error[name] ? "border-red-500 focus:ring-red-500" : "border-gray-300 focus:ring-primary"
            }`}
          />
        ) : (
          <select
            name={name}
            value={params[name as keyof PredictParams] || ""}
            onChange={handleChange}
            className="w-full border border-gray-300 rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
          >
            {options?.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        )}
        {error[name] && <p className="text-red-500 text-sm">{error[name]}</p>}
      </div>
    );
  };

  return (
    <div className="p-6 bg-gray-50 rounded-md shadow-md max-w-lg mx-auto h-full overflow-y-auto">
      <h1 className="text-xl font-bold text-gray-700 mb-4">House Price Predictor</h1>
      <div className="space-y-4">
        {/* Property Type */}
        {renderField("Loại tài sản", "property_type", "select", [
          { label: "Chung cư", value: "apartment" },
          { label: "Đất", value: "land" },
          { label: "Nhà riêng", value: "house" },
        ])}

        {/* Shared Fields */}
        {renderField("Diện tích", "area", "number")}
        {renderField("Tình trạng pháp lý", "legal_status", "select", legalStatusOptions)}
        {renderField("Hướng nhà", "house_direction", "select", directions)}

        {/* Apartment and House */}
        {(params.property_type === "apartment" || params.property_type === "house") && (
          <>
            {renderField("Số phòng ngủ", "bedrooms", "number")}
            {renderField("Số nhà vệ sinh", "toilets", "number")}
            {renderField("Nội thất", "furniture", "select", furnitureOptions)}
            {renderField("Hướng ban công", "balcony_direction", "select", directions)}
          </>
        )}

        {/* Land and House */}
        {(params.property_type === "land" || params.property_type === "house") && (
          <>
            {renderField("Chiều dài mặt tiền", "frontage", "number")}
            {renderField("Chiều rộng đường vào", "access_road_width", "number")}
          </>
        )}

        {/* Map Error */}
        {error.map && (
          <p className="text-red-500 font-medium mb-4">Vui lòng chọn vị trí trên bản đồ.</p>
        )}

        {/* Buttons */}
        <div className="flex justify-between mt-4">
          <button
            onClick={resetFields}
            className="bg-gray-200 text-gray-700 font-medium py-2 px-4 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400"
          >
            Reset
          </button>
          <button
            onClick={predict}
            className="bg-primary text-white font-medium py-2 px-4 rounded-md hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
          >
            Predict
          </button>
        </div>

        {/* Result */}
        {result !== null && (
          <div className="mt-6">
            <h2 className="text-lg font-semibold text-gray-700 mb-2">Giá dự đoán:</h2>
            <p className="text-2xl font-bold text-primary">{result} VND</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PredictForm;
