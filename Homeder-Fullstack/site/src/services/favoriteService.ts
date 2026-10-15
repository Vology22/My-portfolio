import api from './api';

export interface FavoriteWithProperty {
  user_id: number;
  prop_id: number;
  property: {
    prop_id: number;
    owner_id: number;
    price: string;
    title: string;
    description: string;
    city: string;
    floor: number;
    rooms: number;
    current_tenants: number;
    potential_tenants: number;
    images: Array<{
      img_id: number;
      img_url: string;
      is_cover: boolean;
    }>;
    created_at?: string;
  };
}

class FavoriteService {
  // Добавить в избранное
  async addToFavorite(userId: number, propId: number): Promise<{ status: string }> {
    try {
      console.log('[FavoriteService] Добавление в избранное:', { userId, propId });
      const response = await api.post('/favorites', { user_id: userId, prop_id: propId });
      console.log('[FavoriteService] Результат:', response.data);
      return response.data;
    } catch (error) {
      console.error('[FavoriteService] Ошибка при добавлении в избранное:', error);
      throw error;
    }
  }

  // Получить все избранные объявления пользователя
  async getUserFavorites(userId: number): Promise<FavoriteWithProperty[]> {
    try {
      console.log('[FavoriteService] Запрос избранного для пользователя:', userId);
      const response = await api.get(`/favorites/user/${userId}`);
      console.log('[FavoriteService] Получено избранных:', response.data.count);
      return response.data.favorites || [];
    } catch (error) {
      console.error('[FavoriteService] Ошибка при получении избранного:', error);
      throw error;
    }
  }

  // Удалить из избранного (если добавите эндпоинт на бэкенде)
  async removeFromFavorite(userId: number, propId: number): Promise<void> {
    try {
      console.log('[FavoriteService] Удаление из избранного:', propId);
      await api.delete(`/favorites/${userId}/${propId}`);
    } catch (error) {
      console.error('[FavoriteService] Ошибка при удалении из избранного:', error);
      throw error;
    }
  }
}

export const favoriteService = new FavoriteService();