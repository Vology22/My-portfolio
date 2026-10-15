import api from './api';

export interface UserData {
  user_id: number;
  full_name: string;
  bio?: string;
  tg_id: string;
  avatar?: string | null; 
   age: number;
  gender: string; 
  badHabits:string;
  pet:string;
  hasRoommate: string;
}

export interface CreateUserData {
  full_name: string;
  bio?: string;
  tg_id: string;
  avatar?: string | null; 
  age: number;
  gender: string;
  badHabits: string;
  pet: string;
  hasRoommate: string;
}

class UserService {
  async getUserByTgId(tgId: string): Promise<UserData | null> {
    try {
      console.log('Запрос пользователя с tg_id:', tgId);
      const response = await api.get(`/users/by-tg/${tgId}`);
      console.log('Ответ от сервера:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Ошибка при получении пользователя:', error);
      if (error.response?.status === 404) {
        return null; 
      }
      throw error;
    }
  }

  async createOrUpdateUser(userData: CreateUserData): Promise<UserData> {
    console.log('Создание/обновление пользователя:', userData);
    const response = await api.post('/users', userData);
    console.log('Результат:', response.data);
    return response.data;
  }
}

export const userService = new UserService();