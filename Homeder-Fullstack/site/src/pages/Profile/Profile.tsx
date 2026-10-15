import { useEffect} from 'react';
import { useUserData } from '../../hooks/useUserData';
import styles from './profile.module.scss';
import { Button } from "../../components/ui";

const Profile = () => {
  const { user, loading, error, fetchUser } = useUserData();

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);


  //Получаем инициалы, если аватара нет
  const getInitials = (name: string): string => {
    return name
      .split(' ')
      .map(part => part.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  if (loading && !user) {
    return (
    <div className={styles.wrapper}>
      <div className={styles.profile}>
         <div className={styles.content}>
          <div className={styles.loading}>
            <div className={styles.loading_spinner}></div>
            <div className={styles.loading_text}>Загрузка профиля...</div>
          </div>
        </div>
      </div>
    </div>
   );
  }

  if (error && !user) {
    return (
    <div className={styles.wrapper}>
      <div className={styles.profile}>
        <div className={styles.content}>
          <div className={styles.error}> 
            <div className={styles.error_message}>Ошибка: {error}</div>
            <Button 
              className={styles.error_button}
              onClickAdditional={() => fetchUser()}> Попробовать снова
            </Button>
          </div>
        </div>
      </div>
    </div>
   );
  }

  if (!user) {
    return (
      <div className="profile-page">
        <div className="error-message">Пользователь не найден</div>
      </div>
    );
  }

  console.log('User data:', user);

  return (
    <div className={styles.wrapper}>
      <div className={styles.profile}>
        {/* Первый прямоугольник - фото профиля */}
        <div className={styles.photo_card}>
          {user.avatar ? (
            <img src={user.avatar}className={styles.photo_card_image} />
          ) : (
            <div className={styles.photo_card_placeholder}>
              {getInitials(user.name)}
            </div>
          )}
        </div>

        {/* Второй прямоугольник - личная информация */}
        <div className={styles.info_card}>
          <div className={styles.info_card_header}>
            <h2 className={styles.info_card_title}>Личная информация</h2>
          </div>
            <div className={styles.info_card_grid}>
              {/* Поле имени */}
              <div className={styles.info_card_item}>
                <span className={styles.info_card_label}>Имя</span>
                <span className={styles.info_card_value}>{user.name}</span>
              </div>
              {/* Поле фамилии */}
              <div className={styles.info_card_item}>
                <span className={styles.info_card_label}>Фамилия</span>
                <span className={styles.info_card_value}>{user.surname}</span>
              </div>
              {/* Поле отчества*/}
              <div className={styles.info_card_item}>
                <span className={styles.info_card_label}>Отчество</span>
                <span className={styles.info_card_value}>{user.patronymic || '-'}</span>
              </div>
              {/* Поле даты рождения */}
              <div className={styles.info_card_item}>
                <span className={styles.info_card_label}>Возраст (лет)</span>
                <span className={styles.info_card_value}>{user.age}</span>
              </div>
              {/* Поле пола */}
              <div className={styles.info_card_item}>
                <span className={styles.info_card_label}>Пол</span>
                <span className={styles.info_card_value}>{user.gender}</span>
              </div>
              {/* Поле плохих привычек*/}
              <div className={styles.info_card_item}>
                <span className={styles.info_card_label}>Плохие привычки</span>
                <span className={styles.info_card_value}>{user.badHabits}</span>
              </div>
              {/* Поле питомцев*/}
              <div className={styles.info_card_item}>
                <span className={styles.info_card_label}>Питомцы</span>
                <span className={styles.info_card_value}>{user.pet}</span>
              </div>
              {/* Поле соседа */}
              <div className={styles.info_card_item}>
                <span className={styles.info_card_label}>Сожитель</span>
                <span className={styles.info_card_value}>{user.hasRoommate}</span>
              </div>
            </div>
        </div>
      </div>
    </div>
  );
};
export default Profile;
