import api from './api';
class PropertyService {
    async getProperties(limit = 50, offset = 0) {
        try {
            api.interceptors.request.use((config) => {
                console.log("Full URL:", config.baseURL + config.url);
                return config;
            });
            console.log("API baseURL:", api.defaults.baseURL);
            console.log('[PropertyService] Запрос объявлений:', { limit, offset });
            const response = await api.get('/properties', { params: { limit, offset } });
            console.log('[PropertyService] Получено объявлений:', response.data.length);
            return response.data;
        }
        catch (error) {
            console.error('[PropertyService] Ошибка при получении объявлений:', error);
            throw error;
        }
    }
    async getPropertyById(propId) {
        try {
            console.log('[PropertyService] Запрос объявления:', propId);
            const response = await api.get(`/properties/${propId}`);
            return response.data;
        }
        catch (error) {
            console.error('[PropertyService] Ошибка при получении объявления:', error);
            throw error;
        }
    }
}
export const propertyService = new PropertyService();
