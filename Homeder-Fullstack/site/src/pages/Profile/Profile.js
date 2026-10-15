import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect } from 'react';
import { useUserData } from '../../hooks/useUserData';
import styles from './profile.module.scss';
import { Button } from "../../components/ui";
const Profile = () => {
    const { user, loading, error, fetchUser } = useUserData();
    useEffect(() => {
        fetchUser();
    }, [fetchUser]);
    //Получаем инициалы, если аватара нет
    const getInitials = (name) => {
        return name
            .split(' ')
            .map(part => part.charAt(0))
            .join('')
            .toUpperCase()
            .slice(0, 2);
    };
    if (loading && !user) {
        return (_jsx("div", { className: styles.wrapper, children: _jsx("div", { className: styles.profile, children: _jsx("div", { className: styles.content, children: _jsxs("div", { className: styles.loading, children: [_jsx("div", { className: styles.loading_spinner }), _jsx("div", { className: styles.loading_text, children: "\u0417\u0430\u0433\u0440\u0443\u0437\u043A\u0430 \u043F\u0440\u043E\u0444\u0438\u043B\u044F..." })] }) }) }) }));
    }
    if (error && !user) {
        return (_jsx("div", { className: styles.wrapper, children: _jsx("div", { className: styles.profile, children: _jsx("div", { className: styles.content, children: _jsxs("div", { className: styles.error, children: [_jsxs("div", { className: styles.error_message, children: ["\u041E\u0448\u0438\u0431\u043A\u0430: ", error] }), _jsx(Button, { className: styles.error_button, onClickAdditional: () => fetchUser(), children: " \u041F\u043E\u043F\u0440\u043E\u0431\u043E\u0432\u0430\u0442\u044C \u0441\u043D\u043E\u0432\u0430" })] }) }) }) }));
    }
    if (!user) {
        return (_jsx("div", { className: "profile-page", children: _jsx("div", { className: "error-message", children: "\u041F\u043E\u043B\u044C\u0437\u043E\u0432\u0430\u0442\u0435\u043B\u044C \u043D\u0435 \u043D\u0430\u0439\u0434\u0435\u043D" }) }));
    }
    console.log('User data:', user);
    return (_jsx("div", { className: styles.wrapper, children: _jsxs("div", { className: styles.profile, children: [_jsx("div", { className: styles.photo_card, children: user.avatar ? (_jsx("img", { src: user.avatar, className: styles.photo_card_image })) : (_jsx("div", { className: styles.photo_card_placeholder, children: getInitials(user.name) })) }), _jsxs("div", { className: styles.info_card, children: [_jsx("div", { className: styles.info_card_header, children: _jsx("h2", { className: styles.info_card_title, children: "\u041B\u0438\u0447\u043D\u0430\u044F \u0438\u043D\u0444\u043E\u0440\u043C\u0430\u0446\u0438\u044F" }) }), _jsxs("div", { className: styles.info_card_grid, children: [_jsxs("div", { className: styles.info_card_item, children: [_jsx("span", { className: styles.info_card_label, children: "\u0418\u043C\u044F" }), _jsx("span", { className: styles.info_card_value, children: user.name })] }), _jsxs("div", { className: styles.info_card_item, children: [_jsx("span", { className: styles.info_card_label, children: "\u0424\u0430\u043C\u0438\u043B\u0438\u044F" }), _jsx("span", { className: styles.info_card_value, children: user.surname })] }), _jsxs("div", { className: styles.info_card_item, children: [_jsx("span", { className: styles.info_card_label, children: "\u041E\u0442\u0447\u0435\u0441\u0442\u0432\u043E" }), _jsx("span", { className: styles.info_card_value, children: user.patronymic || '-' })] }), _jsxs("div", { className: styles.info_card_item, children: [_jsx("span", { className: styles.info_card_label, children: "\u0412\u043E\u0437\u0440\u0430\u0441\u0442 (\u043B\u0435\u0442)" }), _jsx("span", { className: styles.info_card_value, children: user.age })] }), _jsxs("div", { className: styles.info_card_item, children: [_jsx("span", { className: styles.info_card_label, children: "\u041F\u043E\u043B" }), _jsx("span", { className: styles.info_card_value, children: user.gender })] }), _jsxs("div", { className: styles.info_card_item, children: [_jsx("span", { className: styles.info_card_label, children: "\u041F\u043B\u043E\u0445\u0438\u0435 \u043F\u0440\u0438\u0432\u044B\u0447\u043A\u0438" }), _jsx("span", { className: styles.info_card_value, children: user.badHabits })] }), _jsxs("div", { className: styles.info_card_item, children: [_jsx("span", { className: styles.info_card_label, children: "\u041F\u0438\u0442\u043E\u043C\u0446\u044B" }), _jsx("span", { className: styles.info_card_value, children: user.pet })] }), _jsxs("div", { className: styles.info_card_item, children: [_jsx("span", { className: styles.info_card_label, children: "\u0421\u043E\u0436\u0438\u0442\u0435\u043B\u044C" }), _jsx("span", { className: styles.info_card_value, children: user.hasRoommate })] })] })] })] }) }));
};
export default Profile;
