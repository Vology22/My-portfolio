import { useState, useCallback, useEffect} from 'react';
import { Property } from '../components/widgets//ListCards/Property';
import { favoriteService, FavoriteWithProperty } from '../services/favoriteService';
import { userService } from '../services/userService';
import { getTgId } from '../utils/tg.utils';

export const useFavorites = () => {
  const [favorites, setFavorites] = useState<Property[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

    // Маппинг избранного в формат Property
  const mapFavoriteToProperty = (favorite: FavoriteWithProperty): Property => {
    console.log('[mapFavoriteToProperty] Входящий favorite:', favorite);
    
    const propertyData = favorite.property;
    
    // Если property нет, возвращаем заглушку или выбрасываем ошибку
    if (!propertyData) {
      console.error('[mapFavoriteToProperty] Нет данных property в favorite:', favorite);
      return {
        prop_id: favorite.prop_id,
        owner_id: 0,
        image: '',
        images: [],
        price: 'не указана',
        title: 'Данные не загружены',
        description: '',
        square: '',
        city: '',
        floor: 0,
        rooms: 0,
        current_tenants: 0,
        potential_tenants: 0,
        created_at: '',
      };
    }
    
    // Парсим квадратуру из description
    let square = '';
    if (propertyData.description) {
      const squareMatch = propertyData.description.match(/(\d+)\s*кв\.?м/i);
      if (squareMatch) square = `${squareMatch[1]} м²`;
    }
    
    // Получаем массив всех изображений
    let imagesArray: any[] = [];
    let imageUrl = '';
    
    if (propertyData.images && propertyData.images.length > 0) {
      // Сохраняем все изображения
      imagesArray = propertyData.images;
      
      // Ищем обложку или берем первое изображение для поля image (для обратной совместимости)
      const coverImage = propertyData.images.find((img: any) => img.is_cover);
      imageUrl = coverImage ? coverImage.img_url : propertyData.images[0].img_url;
    }
    
    const mapped = {
      prop_id: propertyData.prop_id,
      owner_id: propertyData.owner_id || 0,
      image: imageUrl,
      images: imagesArray, // Добавляем массив всех изображений
      price: propertyData.price || 'Не указана',
      title: propertyData.title || 'Без названия',
      description: propertyData.description || '',
      square: square,
      city: propertyData.city || '',
      floor: propertyData.floor || 0,
      rooms: propertyData.rooms || 0,
      current_tenants: propertyData.current_tenants || 0,
      potential_tenants: propertyData.potential_tenants || 0,
      created_at: propertyData.created_at || '',
    };
    
    console.log('[mapFavoriteToProperty] Результат маппинга:', mapped);
    return mapped;
  };

  // Загрузить избранное
  const fetchFavorites = useCallback(async () => {
    console.log('FETCH START', Date.now());
    console.log('[useFavorites] === НАЧАЛО ЗАГРУЗКИ ИЗБРАННОГО ===');
    try {
      setLoading(true);
      setError(null);

      const tgId = getTgId();
      console.log('[useFavorites] tg_id:', tgId);

      const user = await userService.getUserByTgId(tgId);
      if (!user) {
        throw new Error('Пользователь не найден');
      }

      console.log('[useFavorites] user_id:', user.user_id);

      const favoritesData = await favoriteService.getUserFavorites(user.user_id);
      console.log('[useFavorites] Получено избранных объявлений:', favoritesData.length);

      const mappedFavorites = favoritesData.map(mapFavoriteToProperty);
      console.log('[useFavorites] После маппинга:', mappedFavorites.length);

      setFavorites(mappedFavorites);
      setLoading(false);
    } catch (err) {
      console.error('[useFavorites] Ошибка:', err);
      setError('Не удалось загрузить избранное');
    }
  }, []);

  // Добавить в избранное
  const addToFavorite = useCallback(async (property: Property): Promise<boolean> => {
    try {
      const tgId = getTgId();
      const user = await userService.getUserByTgId(tgId);
      
      if (!user) {
        throw new Error('Пользователь не найден');
      }

      await favoriteService.addToFavorite(user.user_id, property.prop_id);
      console.log('[useFavorites] Добавлено в избранное:', property.prop_id);
      
      // Обновляем список избранного
      setFavorites(prev => [...prev, property]);
      return true;
    } catch (err) {
      console.error('[useFavorites] Ошибка при добавлении:', err);
      return false;
    }
  }, [fetchFavorites]);

  // Удалить из избранного
  const removeFromFavorite = useCallback(async (propId: number): Promise<boolean> => {
    try {
      const tgId = getTgId();
      const user = await userService.getUserByTgId(tgId);
      
      if (!user) {
        throw new Error('Пользователь не найден');
      }

      await favoriteService.removeFromFavorite(user.user_id, propId);
      console.log('[useFavorites] Удалено из избранного:', propId);
      
      // Обновляем список
      setFavorites(prev => prev.filter(f => f.prop_id !== propId));
      return true;
    } catch (err) {
      console.error('[useFavorites] Ошибка при удалении:', err);
      return false;
    }
  }, []); 

  useEffect(() => {
    fetchFavorites();
  }, [fetchFavorites]);

  const syncFavorites = useCallback(async () => {
      console.log('[useFavorites] Принудительная синхронизация');
      const tgId = getTgId();
      const user = await userService.getUserByTgId(tgId);
      if (!user) {
        throw new Error('Пользователь не найден');
      }
      const favoritesData = await favoriteService.getUserFavorites(user.user_id);
      const mappedFavorites = favoritesData.map(mapFavoriteToProperty);
      setFavorites(mappedFavorites);
      return mappedFavorites;
    }, []);

  return {
    favorites,
    loading,
    error,
    fetchFavorites,
    addToFavorite,
    removeFromFavorite,
    favoritesLoading: loading,
    syncFavorites
  };
};