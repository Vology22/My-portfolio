import { useFavorites } from '../../hooks/useFavorites';
import { Button, Skeleton } from '../../components/ui';
import { IoMdHeart, IoMdHeartEmpty } from 'react-icons/io';
import { IoChevronBack, IoChevronForward, IoClose } from 'react-icons/io5';
import styles from './Favorites.module.scss';
import { createPortal } from "react-dom";
import { useState, useEffect } from 'react';
import utils from "../../scss/utils.module.scss";

type LightboxState = { propId: number } | null;

const Favorites = () => {
  const { favorites, loading, error, removeFromFavorite } = useFavorites();
  
  console.log('RENDER', { loading, count: favorites.length, time: Date.now() });
  
  console.log('render:', { loading, favoritesCount: favorites.length });
  const [imageErrors, setImageErrors] = useState<Record<number, boolean>>({});
  const [currentImageIndex, setCurrentImageIndex] = useState<Record<number, number>>({});
  const [lightbox, setLightbox] = useState<LightboxState>(null);

  useEffect(() => {
    const newIndices: Record<number, number> = {};
    favorites.forEach(property => {
      newIndices[property.prop_id] = 0;
    });
    setCurrentImageIndex(newIndices);
  }, [favorites]);

  const handleRemoveFromFavorites = async (propId: number) => {
    await removeFromFavorite(propId);
  };

  const handleImageError = (propId: number) => {
    setImageErrors(prev => ({ ...prev, [propId]: true }));
  };

  const getCurrentImageUrl = (property: any, propId: number) => {
    if (imageErrors[propId]) return '/placeholder-image.jpg';

    const currentIndex = currentImageIndex[propId] || 0;
    
    if (property.images && property.images.length > 0) {
      const currentImage = property.images[currentIndex];
      return currentImage?.img_url || property.image || '/placeholder-image.jpg';
    }
    
    return property.image || '/placeholder-image.jpg';
  };

  // Получение общего количества изображений
  const getTotalImagesCount = (property: any) => {
    if (property.images && property.images.length > 0) {
      return property.images.length;
    }
    return property.image ? 1 : 0;
  };

  // Переключение на следующее фото
  const nextImage = (e: React.MouseEvent, propId: number, totalCount: number) => {
    e.stopPropagation();
    const currentIndex = currentImageIndex[propId] || 0;
    if (currentIndex < totalCount - 1) {
      setCurrentImageIndex(prev => ({ ...prev, [propId]: currentIndex + 1 }));
    }
  };

  // Переключение на предыдущее фото
  const prevImage = (e: React.MouseEvent, propId: number) => {
    e.stopPropagation();
    const currentIndex = currentImageIndex[propId] || 0;
    if (currentIndex > 0) {
      setCurrentImageIndex(prev => ({ ...prev, [propId]: currentIndex - 1 }));
    }
  };

  const lightboxNext = (e: React.MouseEvent, propId: number, totalCount: number) => {
    e.stopPropagation();
    const currentIndex = currentImageIndex[propId] || 0;
    if (currentIndex < totalCount - 1) {
      setCurrentImageIndex(prev => ({ ...prev, [propId]: currentIndex + 1 }));
    }
  };

  const lightboxPrev = (e: React.MouseEvent, propId: number) => {
    e.stopPropagation();
    const currentIndex = currentImageIndex[propId] || 0;
    if (currentIndex > 0) {
      setCurrentImageIndex(prev => ({ ...prev, [propId]: currentIndex - 1 }));
    }
  };

  if (loading) {
    return (
    <section className={styles.wrapper}>
      <div className={utils.container}>
        <div className={styles.content}>
            <div className={styles.list}>
              {[1, 2, 3].map(i => (
                <div key={i} className={styles.card}>
                <div className={styles.imageContainer} /> 
                <div style={{ flex: 1 }}>
                  <Skeleton count={3} />
                </div>
              </div>
              ))}
            </div>
          </div>
      </div>
    </section>
    );
  }

  if (error) {
    return (
    <section className={styles.wrapper}>
      <div className={utils.container}>
        <div className={styles.content}>
          <div className={styles.error}>
            <p>Ошибка: {error}</p>
            <Button onClickAdditional={() => window.location.reload()}>
              Попробовать снова
            </Button>
          </div>
        </div>
      </div>
    </section>
    );
  }

  if (favorites.length === 0) {
    return (
    <section className={styles.wrapper}>
      <div className={utils.container}>
        <div className={styles.content}>
            <div className={styles.empty}>
              <IoMdHeartEmpty />
              <p>У вас пока нет понравившихся объявлений</p>
              <p className={styles.emptyHint}>
                Листайте карточки и нажимайте ❤️, чтобы добавить сюда
              </p>
            </div>
          </div>
      </div>
    </section>
    );
  }

  const lightboxProperty = lightbox
    ? favorites.find(f => f.prop_id === lightbox.propId)
    : null;

  return (
    <>
    <section className={styles.wrapper}>
      <div className={utils.container}>
        <div className={styles.content}>
          <div className={styles.list}>
              {favorites.map(property => {
              const totalImages = getTotalImagesCount(property);
              const currentIndex = currentImageIndex[property.prop_id] || 0;  
              const hasImages = totalImages > 0;     
              return (
              <div key={property.prop_id} className={styles.card}>
                  <div className={styles.imageContainer} onClick={() => setLightbox({ propId: property.prop_id })}>
                  {hasImages ? (
                    <>
                    <img
                      src={getCurrentImageUrl(property, property.prop_id)}
                      alt={property.title || 'Недвижимость'}
                      className={styles.card_image}
                      onError={() => handleImageError(property.prop_id)}
                    />
                  {/* Кнопки навигации по фото  */}
                      {totalImages > 1 && (
                        <>
                          <button
                            className={`${styles.navButton} ${styles.navPrev}`}
                            onClick={(e) => prevImage(e, property.prop_id)}
                            disabled={currentIndex === 0}
                          >
                            <IoChevronBack />
                          </button>
                          <button
                            className={`${styles.navButton} ${styles.navNext}`}
                            onClick={(e) => nextImage(e, property.prop_id, totalImages)}
                            disabled={currentIndex === totalImages - 1}
                          >
                            <IoChevronForward />
                          </button>
                          
                          {/* Индикатор текущего фото */}
                          <div className={styles.imageCounter}>
                            {currentIndex + 1} / {totalImages}
                          </div>
                        </>
                      )}
                      
                      {/* Индикаторы-точки */}
                      {totalImages > 1 && (
                        <div className={styles.imageDots}>
                          {Array.from({ length: totalImages }).map((_, idx) => (
                            <button
                              key={idx}
                              className={`${styles.dot} ${idx === currentIndex ? styles.dotActive : ''}`}
                              onClick={(e) => {
                                e.stopPropagation();
                                setCurrentImageIndex(prev => ({ ...prev, [property.prop_id]: idx }));
                              }}
                            />
                          ))}
                        </div>
                      )}                   
                      </>
                      ) : (
                      // Если нет изображений, показываем заглушку
                      <div className={styles.noImage}>
                        <IoMdHeartEmpty />
                        <p>Нет фото</p>
                      </div>
                    )}
                  <button
                      className={styles.favoriteButton}
                      onClick={(e) => {
                          e.stopPropagation();
                          handleRemoveFromFavorites(property.prop_id);
                        }}
                      title="Удалить из избранного"
                  >
                      <IoMdHeart className={styles.filledHeart} />
                  </button>
                  </div>
              <p className={styles.card_cost}>{property.price} </p>
              <p>{property.city || 'Город не указан'}, этаж: {property.floor || 'не указан'}.</p> 
              <p>Количество комнат: {property.rooms || 'не указано'}.</p>
              <p>Количество проживающих сейчас людей: {property.current_tenants || 'не указано'}.</p>
              <p>Количество потенциальных жильцов: {property.potential_tenants || 'не указано'}.</p>
                  <div className={styles.card_description}>
                  <p>{property.title || 'Объявление'}</p>
                      {property.description?.slice(0, 100)}
                      {property.description && property.description.length > 100 ? '...' : ''}
                  </div>
              </div>
              )})}         
          </div>
        </div>
      </div>
    </section>
    {lightbox && lightboxProperty && createPortal(
        <div
          className={styles.lightbox}
          onClick={() => setLightbox(null)}
        >
          <div
            className={styles.lightboxBg}
            style={{ backgroundColor: 'rgba(0, 0, 0, 0.9)' }}
          />

          <button className={styles.lightboxClose} onClick={() => setLightbox(null)}>
            <IoClose />
          </button>

          {(() => {
            const totalImages = getTotalImagesCount(lightboxProperty);
            const currentIndex = currentImageIndex[lightboxProperty.prop_id] || 0;

            return (
              <>
                {totalImages > 1 && (
                  <>
                    <button
                      className={`${styles.lightboxNav} ${styles.lightboxPrev}`}
                      onClick={(e) => lightboxPrev(e, lightboxProperty.prop_id)}
                      disabled={currentIndex === 0}
                    >
                      <IoChevronBack />
                    </button>
                    <button
                      className={`${styles.lightboxNav} ${styles.lightboxNext}`}
                      onClick={(e) => lightboxNext(e, lightboxProperty.prop_id, totalImages)}
                      disabled={currentIndex === totalImages - 1}
                    >
                      <IoChevronForward />
                    </button>
                  </>
                )}

                <div className={styles.lightboxImageWrap} onClick={(e) => e.stopPropagation()}>
                  <img
                    className={styles.lightboxImage}
                    src={getCurrentImageUrl(lightboxProperty, lightboxProperty.prop_id)}
                    alt={lightboxProperty.title || 'Недвижимость'}
                  />
                </div>

                {totalImages > 1 && (
                  <div className={styles.lightboxCounter}>
                    {currentIndex + 1} / {totalImages}
                  </div>
                )}
              </>
            );
          })()}
        </div>,
        document.body
      )}
    </>
  );
};

export default Favorites;