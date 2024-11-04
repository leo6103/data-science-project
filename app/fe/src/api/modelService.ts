import apiClient from './apiClient';

export const predictHousePrice = async (data: {
  area: number;
  bedrooms: number;
  bathrooms: number;
  location: { lat: number; lng: number };
}) => {
  try {
    const response = await apiClient.post('/predict-house-price', data);
    return response.data;
  } catch (error) {
    console.error('Error predicting house price:', error);
    throw error;
  }
};
