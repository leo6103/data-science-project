import React, { useState } from 'react';
import './App.css';
import MapComponent from './components/Map';
import InputPanel from './components/InputPanel';
import { predictHousePrice } from './api';

function App() {
  const [area, setArea] = useState<string>('');
  const [bedrooms, setBedrooms] = useState<string>('');
  const [bathrooms, setBathrooms] = useState<string>('');
  const [markerPosition, setMarkerPosition] = useState<{ lat: number; lng: number } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [predictedPrice, setPredictedPrice] = useState<number | null>(null); // State để lưu kết quả dự đoán

  const handlePredict = () => {
    if (!area || !bedrooms || !bathrooms || !markerPosition) {
      setError('Vui lòng nhập đầy đủ thông tin và chọn vị trí trên bản đồ.');
      return;
    }
    setError(null);

    predictHousePrice({
      area: parseFloat(area),
      bedrooms: parseInt(bedrooms),
      bathrooms: parseInt(bathrooms),
      location: markerPosition,
    })
      .then((data) => {
        setPredictedPrice(data.predicted_price); // Lưu kết quả vào state
      })
      .catch((error) => {
        console.error('Error predicting house price:', error);
        setError('Có lỗi xảy ra khi dự đoán giá nhà.');
      });
  };

  return (
    <div className="flex flex-col items-center gap-6 p-6">
      <InputPanel
        area={area}
        setArea={setArea}
        bedrooms={bedrooms}
        setBedrooms={setBedrooms}
        bathrooms={bathrooms}
        setBathrooms={setBathrooms}
        onPredict={handlePredict}
        predictedPrice={predictedPrice} // Truyền predictedPrice vào InputPanel
      />

      <MapComponent markerPosition={markerPosition} setMarkerPosition={setMarkerPosition} />

      {error && <div className="text-red-500 font-semibold mt-4">{error}</div>}
    </div>
  );
}

export default App;
