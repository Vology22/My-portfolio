import axios from 'axios';
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://localhost:8000/api/v1';
const API_KEY = import.meta.env.VITE_API_KEY || 'homeder-service-key'; // Ключ из .env
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
    },
});
api.interceptors.response.use((response) => response, (error) => {
    if (error.response?.status === 401) {
        console.error('Ошибка авторизации: неверный API ключ');
    }
    return Promise.reject(error);
});
export default api;
