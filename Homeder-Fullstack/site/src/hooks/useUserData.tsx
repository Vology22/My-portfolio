import { useState, useCallback, useEffect } from 'react';
import { User } from '../pages/Profile/User';
import { userService, UserData } from '../services/userService';
import { getTgId } from '../utils/tg.utils';
 
const mapBackendToFrontendUser = (userData: UserData): User => {
  if (!userData) {
    return {
      id: '',
      avatar: undefined,
      name: '',
      surname: '',
      patronymic: '',
      age: 0,
      gender: 'male',
      badHabits: 'no',
      pet: 'no',
      hasRoommate: 'no',
    };
  }
 
  const nameParts = userData.full_name?.split(' ') || [];
 
  return {
    id: String(userData.user_id || ''),
    avatar: userData.avatar || undefined,
    name: nameParts[0] || '',
    surname: nameParts[1] || '',
    patronymic: nameParts[2] || '',
    age: userData.age ?? 0,
    gender: userData.gender || '',
    badHabits: userData.badHabits || '',
    pet: userData.pet || '',
    hasRoommate: userData.hasRoommate|| '',
  };
};
 
export const useUserData = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
 
  const fetchUser = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
 
      const tgId = getTgId();
 
      let userData: UserData | null = await userService.getUserByTgId(tgId);
 
      if (!userData) {
        userData = await userService.createOrUpdateUser({
          full_name: 'Новый пользователь',
          tg_id: tgId,
          bio: '',
          avatar: null,
          age: 0,
          gender: 'male',
          badHabits: 'no',
          pet: 'no',
          hasRoommate: 'no',
        });
      }
 
      const mappedUser = mapBackendToFrontendUser(userData);
      setUser(mappedUser);
 
    } catch (err) {
      setError("Ошибка при загрузке данных пользователя");
    } finally {
      setLoading(false);
    }
  }, []);
 
  useEffect(() => {
    fetchUser();
  }, [fetchUser]);
 
  return {
    user,
    loading,
    error,
    fetchUser,
  };
};