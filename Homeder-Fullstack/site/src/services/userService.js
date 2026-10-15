import api from './api';
class UserService {
    async getUserByTgId(tgId) {
        try {
            console.log('Запрос пользователя с tg_id:', tgId);
            const response = await api.get(`/users/by-tg/${tgId}`);
            console.log('Ответ от сервера:', response.data);
            return response.data;
        }
        catch (error) {
            console.error('Ошибка при получении пользователя:', error);
            if (error.response?.status === 404) {
                return null;
            }
            throw error;
        }
    }
    async createOrUpdateUser(userData) {
        console.log('Создание/обновление пользователя:', userData);
        const response = await api.post('/users', userData);
        console.log('Результат:', response.data);
        return response.data;
    }
}
export const userService = new UserService();
