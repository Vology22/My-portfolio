import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useFavorites } from '../../hooks/useFavorites';
import { Button, Skeleton } from '../../components/ui';
import { IoMdHeart, IoMdHeartEmpty } from 'react-icons/io';
import { IoChevronBack, IoChevronForward, IoClose } from 'react-icons/io5';
import styles from './Favorites.module.scss';
import { createPortal } from "react-dom";
import { useState, useEffect } from 'react';
import utils from "../../scss/utils.module.scss";
const Favorites = () => {
    const { favorites, loading, error, removeFromFavorite } = useFavorites();
    console.log('RENDER', { loading, count: favorites.length, time: Date.now() });
    console.log('render:', { loading, favoritesCount: favorites.length });
    const [imageErrors, setImageErrors] = useState({});
    const [currentImageIndex, setCurrentImageIndex] = useState({});
    const [lightbox, setLightbox] = useState(null);
    useEffect(() => {
        const newIndices = {};
        favorites.forEach(property => {
            newIndices[property.prop_id] = 0;
        });
        setCurrentImageIndex(newIndices);
    }, [favorites]);
    const handleRemoveFromFavorites = async (propId) => {
        await removeFromFavorite(propId);
    };
    const handleImageError = (propId) => {
        setImageErrors(prev => ({ ...prev, [propId]: true }));
    };
    const getCurrentImageUrl = (property, propId) => {
        if (imageErrors[propId])
            return '/placeholder-image.jpg';
        const currentIndex = currentImageIndex[propId] || 0;
        if (property.images && property.images.length > 0) {
            const currentImage = property.images[currentIndex];
            return currentImage?.img_url || property.image || '/placeholder-image.jpg';
        }
        return property.image || '/placeholder-image.jpg';
    };
    // Получение общего количества изображений
    const getTotalImagesCount = (property) => {
        if (property.images && property.images.length > 0) {
            return property.images.length;
        }
        return property.image ? 1 : 0;
    };
    // Переключение на следующее фото
    const nextImage = (e, propId, totalCount) => {
        e.stopPropagation();
        const currentIndex = currentImageIndex[propId] || 0;
        if (currentIndex < totalCount - 1) {
            setCurrentImageIndex(prev => ({ ...prev, [propId]: currentIndex + 1 }));
        }
    };
    // Переключение на предыдущее фото
    const prevImage = (e, propId) => {
        e.stopPropagation();
        const currentIndex = currentImageIndex[propId] || 0;
        if (currentIndex > 0) {
            setCurrentImageIndex(prev => ({ ...prev, [propId]: currentIndex - 1 }));
        }
    };
    const lightboxNext = (e, propId, totalCount) => {
        e.stopPropagation();
        const currentIndex = currentImageIndex[propId] || 0;
        if (currentIndex < totalCount - 1) {
            setCurrentImageIndex(prev => ({ ...prev, [propId]: currentIndex + 1 }));
        }
    };
    const lightboxPrev = (e, propId) => {
        e.stopPropagation();
        const currentIndex = currentImageIndex[propId] || 0;
        if (currentIndex > 0) {
            setCurrentImageIndex(prev => ({ ...prev, [propId]: currentIndex - 1 }));
        }
    };
    if (loading) {
        return (_jsx("section", { className: styles.wrapper, children: _jsx("div", { className: utils.container, children: _jsx("div", { className: styles.content, children: _jsx("div", { className: styles.list, children: [1, 2, 3].map(i => (_jsxs("div", { className: styles.card, children: [_jsx("div", { className: styles.imageContainer }), _jsx("div", { style: { flex: 1 }, children: _jsx(Skeleton, { count: 3 }) })] }, i))) }) }) }) }));
    }
    if (error) {
        return (_jsx("section", { className: styles.wrapper, children: _jsx("div", { className: utils.container, children: _jsx("div", { className: styles.content, children: _jsxs("div", { className: styles.error, children: [_jsxs("p", { children: ["\u041E\u0448\u0438\u0431\u043A\u0430: ", error] }), _jsx(Button, { onClickAdditional: () => window.location.reload(), children: "\u041F\u043E\u043F\u0440\u043E\u0431\u043E\u0432\u0430\u0442\u044C \u0441\u043D\u043E\u0432\u0430" })] }) }) }) }));
    }
    if (favorites.length === 0) {
        return (_jsx("section", { className: styles.wrapper, children: _jsx("div", { className: utils.container, children: _jsx("div", { className: styles.content, children: _jsxs("div", { className: styles.empty, children: [_jsx(IoMdHeartEmpty, {}), _jsx("p", { children: "\u0423 \u0432\u0430\u0441 \u043F\u043E\u043A\u0430 \u043D\u0435\u0442 \u043F\u043E\u043D\u0440\u0430\u0432\u0438\u0432\u0448\u0438\u0445\u0441\u044F \u043E\u0431\u044A\u044F\u0432\u043B\u0435\u043D\u0438\u0439" }), _jsx("p", { className: styles.emptyHint, children: "\u041B\u0438\u0441\u0442\u0430\u0439\u0442\u0435 \u043A\u0430\u0440\u0442\u043E\u0447\u043A\u0438 \u0438 \u043D\u0430\u0436\u0438\u043C\u0430\u0439\u0442\u0435 \u2764\uFE0F, \u0447\u0442\u043E\u0431\u044B \u0434\u043E\u0431\u0430\u0432\u0438\u0442\u044C \u0441\u044E\u0434\u0430" })] }) }) }) }));
    }
    const lightboxProperty = lightbox
        ? favorites.find(f => f.prop_id === lightbox.propId)
        : null;
    return (_jsxs(_Fragment, { children: [_jsx("section", { className: styles.wrapper, children: _jsx("div", { className: utils.container, children: _jsx("div", { className: styles.content, children: _jsx("div", { className: styles.list, children: favorites.map(property => {
                                const totalImages = getTotalImagesCount(property);
                                const currentIndex = currentImageIndex[property.prop_id] || 0;
                                const hasImages = totalImages > 0;
                                return (_jsxs("div", { className: styles.card, children: [_jsxs("div", { className: styles.imageContainer, onClick: () => setLightbox({ propId: property.prop_id }), children: [hasImages ? (_jsxs(_Fragment, { children: [_jsx("img", { src: getCurrentImageUrl(property, property.prop_id), alt: property.title || 'Недвижимость', className: styles.card_image, onError: () => handleImageError(property.prop_id) }), totalImages > 1 && (_jsxs(_Fragment, { children: [_jsx("button", { className: `${styles.navButton} ${styles.navPrev}`, onClick: (e) => prevImage(e, property.prop_id), disabled: currentIndex === 0, children: _jsx(IoChevronBack, {}) }), _jsx("button", { className: `${styles.navButton} ${styles.navNext}`, onClick: (e) => nextImage(e, property.prop_id, totalImages), disabled: currentIndex === totalImages - 1, children: _jsx(IoChevronForward, {}) }), _jsxs("div", { className: styles.imageCounter, children: [currentIndex + 1, " / ", totalImages] })] })), totalImages > 1 && (_jsx("div", { className: styles.imageDots, children: Array.from({ length: totalImages }).map((_, idx) => (_jsx("button", { className: `${styles.dot} ${idx === currentIndex ? styles.dotActive : ''}`, onClick: (e) => {
                                                                    e.stopPropagation();
                                                                    setCurrentImageIndex(prev => ({ ...prev, [property.prop_id]: idx }));
                                                                } }, idx))) }))] })) : (
                                                // Если нет изображений, показываем заглушку
                                                _jsxs("div", { className: styles.noImage, children: [_jsx(IoMdHeartEmpty, {}), _jsx("p", { children: "\u041D\u0435\u0442 \u0444\u043E\u0442\u043E" })] })), _jsx("button", { className: styles.favoriteButton, onClick: (e) => {
                                                        e.stopPropagation();
                                                        handleRemoveFromFavorites(property.prop_id);
                                                    }, title: "\u0423\u0434\u0430\u043B\u0438\u0442\u044C \u0438\u0437 \u0438\u0437\u0431\u0440\u0430\u043D\u043D\u043E\u0433\u043E", children: _jsx(IoMdHeart, { className: styles.filledHeart }) })] }), _jsxs("p", { className: styles.card_cost, children: [property.price, " "] }), _jsxs("p", { children: [property.city || 'Город не указан', ", \u044D\u0442\u0430\u0436: ", property.floor || 'не указан', "."] }), _jsxs("p", { children: ["\u041A\u043E\u043B\u0438\u0447\u0435\u0441\u0442\u0432\u043E \u043A\u043E\u043C\u043D\u0430\u0442: ", property.rooms || 'не указано', "."] }), _jsxs("p", { children: ["\u041A\u043E\u043B\u0438\u0447\u0435\u0441\u0442\u0432\u043E \u043F\u0440\u043E\u0436\u0438\u0432\u0430\u044E\u0449\u0438\u0445 \u0441\u0435\u0439\u0447\u0430\u0441 \u043B\u044E\u0434\u0435\u0439: ", property.current_tenants || 'не указано', "."] }), _jsxs("p", { children: ["\u041A\u043E\u043B\u0438\u0447\u0435\u0441\u0442\u0432\u043E \u043F\u043E\u0442\u0435\u043D\u0446\u0438\u0430\u043B\u044C\u043D\u044B\u0445 \u0436\u0438\u043B\u044C\u0446\u043E\u0432: ", property.potential_tenants || 'не указано', "."] }), _jsxs("div", { className: styles.card_description, children: [_jsx("p", { children: property.title || 'Объявление' }), property.description?.slice(0, 100), property.description && property.description.length > 100 ? '...' : ''] })] }, property.prop_id));
                            }) }) }) }) }), lightbox && lightboxProperty && createPortal(_jsxs("div", { className: styles.lightbox, onClick: () => setLightbox(null), children: [_jsx("div", { className: styles.lightboxBg, style: { backgroundColor: 'rgba(0, 0, 0, 0.9)' } }), _jsx("button", { className: styles.lightboxClose, onClick: () => setLightbox(null), children: _jsx(IoClose, {}) }), (() => {
                        const totalImages = getTotalImagesCount(lightboxProperty);
                        const currentIndex = currentImageIndex[lightboxProperty.prop_id] || 0;
                        return (_jsxs(_Fragment, { children: [totalImages > 1 && (_jsxs(_Fragment, { children: [_jsx("button", { className: `${styles.lightboxNav} ${styles.lightboxPrev}`, onClick: (e) => lightboxPrev(e, lightboxProperty.prop_id), disabled: currentIndex === 0, children: _jsx(IoChevronBack, {}) }), _jsx("button", { className: `${styles.lightboxNav} ${styles.lightboxNext}`, onClick: (e) => lightboxNext(e, lightboxProperty.prop_id, totalImages), disabled: currentIndex === totalImages - 1, children: _jsx(IoChevronForward, {}) })] })), _jsx("div", { className: styles.lightboxImageWrap, onClick: (e) => e.stopPropagation(), children: _jsx("img", { className: styles.lightboxImage, src: getCurrentImageUrl(lightboxProperty, lightboxProperty.prop_id), alt: lightboxProperty.title || 'Недвижимость' }) }), totalImages > 1 && (_jsxs("div", { className: styles.lightboxCounter, children: [currentIndex + 1, " / ", totalImages] }))] }));
                    })()] }), document.body)] }));
};
export default Favorites;
