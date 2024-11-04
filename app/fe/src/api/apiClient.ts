import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:3000', // URL gốc của API
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // Giới hạn thời gian chờ request
});

// Interceptor để xử lý request hoặc thêm token
apiClient.interceptors.request.use(
  (config) => {
    // Có thể thêm token vào headers tại đây nếu cần
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor để xử lý response và lỗi
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API call error:', error);
    return Promise.reject(error);
  }
);

export default apiClient;
