import api from './api';

export interface PropertyImage {
  img_id: number;
  img_url: string;
  is_cover: boolean;
}

export interface PropertyData {
  prop_id: number;
  owner_id: number;
  price?: string;
  title?: string;
  description?: string;
  city?: string;
  created_at?: string;
  floor?: number;
  rooms?: number;
  current_tenants?: number;
  potential_tenants?: number;
  images?: PropertyImage[];
}

class PropertyService {
  async getProperties(limit: number = 50, offset: number = 0): Promise<PropertyData[]> {
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
    } catch (error) {
      console.error('[PropertyService] Ошибка при получении объявлений:', error);
      throw error;
    }
  }

  async getPropertyById(propId: number): Promise<PropertyData> {
    try {
      console.log('[PropertyService] Запрос объявления:', propId);
      const response = await api.get(`/properties/${propId}`);
      return response.data;
    } catch (error) {
      console.error('[PropertyService] Ошибка при получении объявления:', error);
      throw error;
    }
  }
}

export const propertyService = new PropertyService();