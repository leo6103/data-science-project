import React from 'react';

interface InputPanelProps {
  area: string;
  setArea: React.Dispatch<React.SetStateAction<string>>;
  bedrooms: string;
  setBedrooms: React.Dispatch<React.SetStateAction<string>>;
  bathrooms: string;
  setBathrooms: React.Dispatch<React.SetStateAction<string>>;
  onPredict: () => void;
  predictedPrice: number | null; // Thêm prop cho kết quả dự đoán
}

const InputPanel: React.FC<InputPanelProps> = ({
  area,
  setArea,
  bedrooms,
  setBedrooms,
  bathrooms,
  setBathrooms,
  onPredict,
  predictedPrice,
}) => {
  return (
    <div className="flex flex-col gap-6 bg-gray-100 p-6 rounded-lg shadow-md w-full max-w-md">
      <h2 className="text-lg font-bold text-center">Dự đoán giá nhà</h2>

      {/* Kết quả dự đoán nằm trong ô riêng */}
      {predictedPrice !== null && (
        <div className="bg-green-100 text-green-800 rounded-md p-4 shadow-md mb-4">
          <h3 className="font-semibold text-sm">Giá dự đoán:</h3>
          <p className="text-xl font-bold">{predictedPrice.toLocaleString('vi-VN')} VND</p>
        </div>
      )}

      {/* Ô nhập diện tích */}
      <div className="flex flex-col gap-2 bg-white p-4 rounded-md shadow-sm">
        <label className="font-semibold">Diện tích (m²):</label>
        <input
          type="number"
          value={area}
          onChange={(e) => setArea(e.target.value)}
          placeholder="Nhập diện tích"
          className="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Ô nhập số phòng ngủ */}
      <div className="flex flex-col gap-2 bg-white p-4 rounded-md shadow-sm">
        <label className="font-semibold">Số phòng ngủ:</label>
        <input
          type="number"
          value={bedrooms}
          onChange={(e) => setBedrooms(e.target.value)}
          placeholder="Nhập số phòng ngủ"
          className="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Ô nhập số toilet */}
      <div className="flex flex-col gap-2 bg-white p-4 rounded-md shadow-sm">
        <label className="font-semibold">Số toilet:</label>
        <input
          type="number"
          value={bathrooms}
          onChange={(e) => setBathrooms(e.target.value)}
          placeholder="Nhập số toilet"
          className="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Nút Predict */}
      <button
        onClick={onPredict}
        className="w-full bg-blue-500 text-white font-semibold py-2 px-4 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 mt-4"
      >
        Predict
      </button>
    </div>
  );
};

export default InputPanel;
