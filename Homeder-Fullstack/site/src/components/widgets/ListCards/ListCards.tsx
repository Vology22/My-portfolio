import { Button, Icon, Skeleton } from "../../ui";
import { motion, useAnimation } from "framer-motion";
import { RxCross2 } from "react-icons/rx";
import { IoMdHeartEmpty } from "react-icons/io";
import { FaRedoAlt } from "react-icons/fa"; 
import { IoChevronBack, IoChevronForward, IoClose } from "react-icons/io5";
import styles from "./listCards.module.scss";
import { useEffect, useState, useRef } from "react";
import { createPortal } from "react-dom";
import { useProperties } from "../../../hooks/useProperties";
import { useFavorites } from "../../../hooks/useFavorites"; 

const ListCards = () => {
   const { 
      properties, 
      currentProperty, 
      loading, 
      error, 
      nextProperty, 
      totalCount,
      allViewed,
      setAllViewed,
      restartViewing,
      addCurrentToDisliked, 
      fetchProperties,
      removePropertyById,
      setFavoritesRef 
   } = useProperties();
   
   const { addToFavorite, fetchFavorites, favorites } = useFavorites();
   const controls = useAnimation();
   const [imageError, setImageError] = useState(false);
   const [currentImageIndex, setCurrentImageIndex] = useState(0);
   const [lightboxOpen, setLightboxOpen] = useState(false);
   const isInitialized = useRef(false);

   useEffect(() => {
      setCurrentImageIndex(0);
      setImageError(false);
   }, [currentProperty]);

   useEffect(() => {
      if (favorites) {
         console.log('[ListCards] Синхронизация favorites:', favorites.map(f => f.prop_id));
         setFavoritesRef(favorites);
      }
   }, [favorites, setFavoritesRef]);

   useEffect(() => {
      if (!isInitialized.current && favorites.length > 0) {
         console.log('[ListCards] Начальная синхронизация');
         setFavoritesRef(favorites);
         isInitialized.current = true;
      }
   }, [favorites, setFavoritesRef]);

   useEffect(() => {
      if (!allViewed && currentProperty) {
         controls.start({
            y: 0,
            opacity: 1,
            transition: { duration: 0.15 }
         });
      }
   }, [currentProperty, controls, allViewed]);

   const handleDislike = async () => {
      if (allViewed) return; // Если все просмотрены, не обрабатываем действия
      
      await controls.start({
         x: -100,
         opacity: 0,
         transition: { duration: 0.15 }
      });
      
      addCurrentToDisliked();
      nextProperty();
      setImageError(false);
      
      controls.set({ x: 100, opacity: 0 });
      controls.start({
         x: 0,
         opacity: 1,
         transition: { duration: 0.15 }
      });
   };

   const handleLike = async () => {
      if (allViewed) return; 

      await controls.start({
         x: 100,
         opacity: 0,
         transition: { duration: 0.15 }
      });
            
      await addToFavorite(currentProperty);

      console.log('Удаляю из локального массива...');
      removePropertyById(currentProperty.prop_id);

      if (properties.indexOf(currentProperty) + 1 >= properties.length) {
         // Дошли до конца массива
         setAllViewed(true);
         return;
      }

      setImageError(false);

      controls.set({ x: -100, opacity: 0 });
      controls.start({
         x: 0,
         opacity: 1,
         transition: { duration: 0.15 }
      });

   };

   const handleRestart = async () => {
      console.log('[ListCards] Перезапуск просмотра');
      setImageError(false);
      
      await fetchFavorites();
      
      setTimeout(() => {
        restartViewing();
        fetchProperties();
      }, 100);
   };

   // Навигация по фотографиям
   const nextImage = (e: React.MouseEvent) => {
      e.stopPropagation();
      if (currentProperty?.images && currentImageIndex < currentProperty.images.length - 1) {
         setCurrentImageIndex(prev => prev + 1);
      }
   };

   const prevImage = (e: React.MouseEvent) => {
      e.stopPropagation();
      if (currentImageIndex > 0) {
         setCurrentImageIndex(prev => prev - 1);
      }
   };

   const handleLightboxNext = () => {
      if (currentProperty?.images && currentImageIndex < currentProperty.images.length - 1) {
         setCurrentImageIndex(prev => prev + 1);
      }
   };

   const handleLightboxPrev = () => {
      if (currentImageIndex > 0) {
         setCurrentImageIndex(prev => prev - 1);
      }
   };

   const getCurrentImageUrl = () => {
      if (imageError) return '/placeholder-image.jpg';

      if (currentProperty?.images && currentProperty.images.length > 0) {
         const currentImage = currentProperty.images[currentImageIndex];
         return currentImage?.img_url || currentProperty.image || '/placeholder-image.jpg';
      }

      return currentProperty?.image || '/placeholder-image.jpg';
   };

   const getTotalImagesCount = () => {
      if (currentProperty?.images && currentProperty.images.length > 0) {
         return currentProperty.images.length;
      }
      // Если есть хотя бы одно изображение в поле image
      return currentProperty?.image ? 1 : 0;
   };

   if (loading) {
      return (
         <>
         <Skeleton height={300} />
         <Skeleton count={3} />
         <Skeleton height={50} />
         <div className={styles.buttons}>
            <Button disabled>Загрузка...</Button>
            <Button disabled>Загрузка...</Button>
         </div>
         </>
      );
   }

   if (error) {
      return (
         <div className={styles.error}>
         <p>Ошибка: {error}</p>
         <Button onClickAdditional={() => window.location.reload()}>
            Попробовать снова
         </Button>
         </div>
      );
   }

   if (!currentProperty && totalCount === 0 && !allViewed) {
      return (
         <div className={styles.empty}>
         <p>Нет доступных объявлений</p>
         </div>
      );
   }

   console.log('[ListCards] allViewed:', allViewed);

   const totalImages = getTotalImagesCount();
   const currentImageUrl = getCurrentImageUrl();

   return ( 
      <>    
      {allViewed ? (
         <motion.div 
            className={styles.completedView}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
         >
            <div className={styles.completedContent}>
               <p>Вы просмотрели все доступные объявления</p>
               <div className={styles.stats}>
                  <span>Просмотрено: {totalCount} из {totalCount}</span>
               </div>
               <Button onClickAdditional={handleRestart}> <Icon Icon={FaRedoAlt} /> Начать просмотр заново </Button>
            </div>
         </motion.div>
      ) : (
         <>
            {currentProperty && (
               <motion.div
                  animate={controls}
                  initial={{ y: -100, opacity: 0 }}
                  className={styles.card}
               >
                  <div className={styles.imageContainer} onClick={() => {console.log('click!'); setLightboxOpen(true)}}>
                        <img
                           className={styles.card_image}
                           src={currentImageUrl}
                           alt={currentProperty.title || 'Недвижимость'}
                           onError={() => setImageError(true)}
                        />

                        {/* Кнопки навигации по фото */}
                        {totalImages > 1 && (
                           <>
                              <button
                                 className={`${styles.navButton} ${styles.navPrev}`}
                                 onClick={prevImage}
                                 disabled={currentImageIndex === 0}
                              >
                                 <IoChevronBack />
                              </button>
                              <button
                                 className={`${styles.navButton} ${styles.navNext}`}
                                 onClick={nextImage}
                                 disabled={currentImageIndex === totalImages - 1}
                              >
                                 <IoChevronForward />
                              </button>

                              {/* Индикатор текущего фото */}
                              <div className={styles.imageCounter}>
                                 {currentImageIndex + 1} / {totalImages}
                              </div>
                           </>
                        )}

                        {/* Индикаторы-точки */}
                        {totalImages > 1 && (
                           <div className={styles.imageDots}>
                              {Array.from({ length: totalImages }).map((_, idx) => (
                                 <button
                                    key={idx}
                                    className={`${styles.dot} ${idx === currentImageIndex ? styles.dotActive : ''}`}
                                    onClick={(e) => {
                                       e.stopPropagation();
                                       setCurrentImageIndex(idx);
                                    }}
                                 />
                              ))}
                           </div>
                        )}
                  </div>
                  <p className={styles.card_cost}> {currentProperty.price} </p>
                  <p>{currentProperty.city || 'Город не указан'}, этаж: {currentProperty.floor || 'не указан'}.</p>
                  <p>Количество комнат: {currentProperty.rooms || 'не указано'}.</p>
                  <p>Количество проживающих сейчас людей: {currentProperty.current_tenants || 'не указано'}. </p> 
                  <p>Количество потенциальных жильцов: {currentProperty.potential_tenants || 'не указано'}.</p>
                  <div className={styles.card_description}>
                     <p>{currentProperty.title || 'Недвижимость'} </p>
                     {currentProperty.description || 'Описание отсутствует'}
                  </div>
                  <div className={styles.progress}>
                  </div>
               </motion.div>
            )}
            <div className={styles.buttons}>
               <Button onClickAdditional={handleDislike}>
                  <Icon Icon={RxCross2} />Не понравилось
               </Button>
               <Button onClickAdditional={handleLike}>
                  <Icon Icon={IoMdHeartEmpty} />Понравилось
               </Button>
            </div>
         </>
      )}
      {lightboxOpen && createPortal(
         <motion.div
            className={styles.lightbox}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={() => setLightboxOpen(false)}
         >
            {/* Размытый фон — копия изображения */}
            <div
               className={styles.lightboxBg}
               style={{ backgroundColor: 'rgba(0, 0, 0, 0.9)' }}
            />

            <button className={styles.lightboxClose} onClick={() => setLightboxOpen(false)}>
               <IoClose />
            </button>

            {totalImages > 1 && (
               <>
                  <button
                     className={`${styles.lightboxNav} ${styles.lightboxPrev}`}
                     onClick={(e) => { e.stopPropagation(); handleLightboxPrev(); }}
                     disabled={currentImageIndex === 0}
                  >
                     <IoChevronBack />
                  </button>
                  <button
                     className={`${styles.lightboxNav} ${styles.lightboxNext}`}
                     onClick={(e) => { e.stopPropagation(); handleLightboxNext(); }}
                     disabled={currentImageIndex === totalImages - 1}
                  >
                     <IoChevronForward />
                  </button>
               </>
            )}

            <div className={styles.lightboxImageWrap} onClick={(e) => e.stopPropagation()}>
               <img
                  className={styles.lightboxImage}
                  src={currentImageUrl}
                  alt={currentProperty?.title || 'Недвижимость'}
               />
            </div>

            {totalImages > 1 && (
               <div className={styles.lightboxCounter}>
                  {currentImageIndex + 1} / {totalImages}
               </div>
            )}
         </motion.div>,
         document.body
      )}
      </>
   );
};
 
export default ListCards;