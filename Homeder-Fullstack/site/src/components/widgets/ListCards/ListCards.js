import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
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
    const { properties, currentProperty, loading, error, nextProperty, totalCount, allViewed, setAllViewed, restartViewing, addCurrentToDisliked, fetchProperties, removePropertyById, setFavoritesRef } = useProperties();
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
        if (allViewed)
            return; // Если все просмотрены, не обрабатываем действия
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
        if (allViewed)
            return;
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
    const nextImage = (e) => {
        e.stopPropagation();
        if (currentProperty?.images && currentImageIndex < currentProperty.images.length - 1) {
            setCurrentImageIndex(prev => prev + 1);
        }
    };
    const prevImage = (e) => {
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
        if (imageError)
            return '/placeholder-image.jpg';
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
        return (_jsxs(_Fragment, { children: [_jsx(Skeleton, { height: 300 }), _jsx(Skeleton, { count: 3 }), _jsx(Skeleton, { height: 50 }), _jsxs("div", { className: styles.buttons, children: [_jsx(Button, { disabled: true, children: "\u0417\u0430\u0433\u0440\u0443\u0437\u043A\u0430..." }), _jsx(Button, { disabled: true, children: "\u0417\u0430\u0433\u0440\u0443\u0437\u043A\u0430..." })] })] }));
    }
    if (error) {
        return (_jsxs("div", { className: styles.error, children: [_jsxs("p", { children: ["\u041E\u0448\u0438\u0431\u043A\u0430: ", error] }), _jsx(Button, { onClickAdditional: () => window.location.reload(), children: "\u041F\u043E\u043F\u0440\u043E\u0431\u043E\u0432\u0430\u0442\u044C \u0441\u043D\u043E\u0432\u0430" })] }));
    }
    if (!currentProperty && totalCount === 0 && !allViewed) {
        return (_jsx("div", { className: styles.empty, children: _jsx("p", { children: "\u041D\u0435\u0442 \u0434\u043E\u0441\u0442\u0443\u043F\u043D\u044B\u0445 \u043E\u0431\u044A\u044F\u0432\u043B\u0435\u043D\u0438\u0439" }) }));
    }
    console.log('[ListCards] allViewed:', allViewed);
    const totalImages = getTotalImagesCount();
    const currentImageUrl = getCurrentImageUrl();
    return (_jsxs(_Fragment, { children: [allViewed ? (_jsx(motion.div, { className: styles.completedView, initial: { opacity: 0, scale: 0.9 }, animate: { opacity: 1, scale: 1 }, transition: { duration: 0.3 }, children: _jsxs("div", { className: styles.completedContent, children: [_jsx("p", { children: "\u0412\u044B \u043F\u0440\u043E\u0441\u043C\u043E\u0442\u0440\u0435\u043B\u0438 \u0432\u0441\u0435 \u0434\u043E\u0441\u0442\u0443\u043F\u043D\u044B\u0435 \u043E\u0431\u044A\u044F\u0432\u043B\u0435\u043D\u0438\u044F" }), _jsx("div", { className: styles.stats, children: _jsxs("span", { children: ["\u041F\u0440\u043E\u0441\u043C\u043E\u0442\u0440\u0435\u043D\u043E: ", totalCount, " \u0438\u0437 ", totalCount] }) }), _jsxs(Button, { onClickAdditional: handleRestart, children: [" ", _jsx(Icon, { Icon: FaRedoAlt }), " \u041D\u0430\u0447\u0430\u0442\u044C \u043F\u0440\u043E\u0441\u043C\u043E\u0442\u0440 \u0437\u0430\u043D\u043E\u0432\u043E "] })] }) })) : (_jsxs(_Fragment, { children: [currentProperty && (_jsxs(motion.div, { animate: controls, initial: { y: -100, opacity: 0 }, className: styles.card, children: [_jsxs("div", { className: styles.imageContainer, onClick: () => { console.log('click!'); setLightboxOpen(true); }, children: [_jsx("img", { className: styles.card_image, src: currentImageUrl, alt: currentProperty.title || 'Недвижимость', onError: () => setImageError(true) }), totalImages > 1 && (_jsxs(_Fragment, { children: [_jsx("button", { className: `${styles.navButton} ${styles.navPrev}`, onClick: prevImage, disabled: currentImageIndex === 0, children: _jsx(IoChevronBack, {}) }), _jsx("button", { className: `${styles.navButton} ${styles.navNext}`, onClick: nextImage, disabled: currentImageIndex === totalImages - 1, children: _jsx(IoChevronForward, {}) }), _jsxs("div", { className: styles.imageCounter, children: [currentImageIndex + 1, " / ", totalImages] })] })), totalImages > 1 && (_jsx("div", { className: styles.imageDots, children: Array.from({ length: totalImages }).map((_, idx) => (_jsx("button", { className: `${styles.dot} ${idx === currentImageIndex ? styles.dotActive : ''}`, onClick: (e) => {
                                                e.stopPropagation();
                                                setCurrentImageIndex(idx);
                                            } }, idx))) }))] }), _jsxs("p", { className: styles.card_cost, children: [" ", currentProperty.price, " "] }), _jsxs("p", { children: [currentProperty.city || 'Город не указан', ", \u044D\u0442\u0430\u0436: ", currentProperty.floor || 'не указан', "."] }), _jsxs("p", { children: ["\u041A\u043E\u043B\u0438\u0447\u0435\u0441\u0442\u0432\u043E \u043A\u043E\u043C\u043D\u0430\u0442: ", currentProperty.rooms || 'не указано', "."] }), _jsxs("p", { children: ["\u041A\u043E\u043B\u0438\u0447\u0435\u0441\u0442\u0432\u043E \u043F\u0440\u043E\u0436\u0438\u0432\u0430\u044E\u0449\u0438\u0445 \u0441\u0435\u0439\u0447\u0430\u0441 \u043B\u044E\u0434\u0435\u0439: ", currentProperty.current_tenants || 'не указано', ". "] }), _jsxs("p", { children: ["\u041A\u043E\u043B\u0438\u0447\u0435\u0441\u0442\u0432\u043E \u043F\u043E\u0442\u0435\u043D\u0446\u0438\u0430\u043B\u044C\u043D\u044B\u0445 \u0436\u0438\u043B\u044C\u0446\u043E\u0432: ", currentProperty.potential_tenants || 'не указано', "."] }), _jsxs("div", { className: styles.card_description, children: [_jsxs("p", { children: [currentProperty.title || 'Недвижимость', " "] }), currentProperty.description || 'Описание отсутствует'] }), _jsx("div", { className: styles.progress })] })), _jsxs("div", { className: styles.buttons, children: [_jsxs(Button, { onClickAdditional: handleDislike, children: [_jsx(Icon, { Icon: RxCross2 }), "\u041D\u0435 \u043F\u043E\u043D\u0440\u0430\u0432\u0438\u043B\u043E\u0441\u044C"] }), _jsxs(Button, { onClickAdditional: handleLike, children: [_jsx(Icon, { Icon: IoMdHeartEmpty }), "\u041F\u043E\u043D\u0440\u0430\u0432\u0438\u043B\u043E\u0441\u044C"] })] })] })), lightboxOpen && createPortal(_jsxs(motion.div, { className: styles.lightbox, initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0 }, transition: { duration: 0.2 }, onClick: () => setLightboxOpen(false), children: [_jsx("div", { className: styles.lightboxBg, style: { backgroundColor: 'rgba(0, 0, 0, 0.9)' } }), _jsx("button", { className: styles.lightboxClose, onClick: () => setLightboxOpen(false), children: _jsx(IoClose, {}) }), totalImages > 1 && (_jsxs(_Fragment, { children: [_jsx("button", { className: `${styles.lightboxNav} ${styles.lightboxPrev}`, onClick: (e) => { e.stopPropagation(); handleLightboxPrev(); }, disabled: currentImageIndex === 0, children: _jsx(IoChevronBack, {}) }), _jsx("button", { className: `${styles.lightboxNav} ${styles.lightboxNext}`, onClick: (e) => { e.stopPropagation(); handleLightboxNext(); }, disabled: currentImageIndex === totalImages - 1, children: _jsx(IoChevronForward, {}) })] })), _jsx("div", { className: styles.lightboxImageWrap, onClick: (e) => e.stopPropagation(), children: _jsx("img", { className: styles.lightboxImage, src: currentImageUrl, alt: currentProperty?.title || 'Недвижимость' }) }), totalImages > 1 && (_jsxs("div", { className: styles.lightboxCounter, children: [currentImageIndex + 1, " / ", totalImages] }))] }), document.body)] }));
};
export default ListCards;
