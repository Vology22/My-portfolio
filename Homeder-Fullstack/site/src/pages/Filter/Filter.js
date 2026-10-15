import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useFilters } from '../../contexts/FilterContext';
import { Button, Icon } from '../../components/ui';
import { RxCross2, RxCheck } from "react-icons/rx";
import styles from './Filter.module.scss';
import utils from "../../scss/utils.module.scss";
const Filter = () => {
    const { setFilters, resetFilters, filters } = useFilters();
    const navigate = useNavigate();
    const [minCount, setMinCount] = useState(filters.minCount?.toString() || '');
    const [maxCount, setMaxCount] = useState(filters.maxCount?.toString() || '');
    const [minFloor, setMinFloor] = useState(filters.minFloor?.toString() || '');
    const [maxFloor, setMaxFloor] = useState(filters.maxFloor?.toString() || '');
    const [minPeople, setMinPeople] = useState(filters.minPeople?.toString() || '');
    const [maxPeople, setMaxPeople] = useState(filters.maxPeople?.toString() || '');
    const [minPeopleNow, setMinPeopleNow] = useState(filters.minPeopleNow?.toString() || '');
    const [maxPeopleNow, setMaxPeopleNow] = useState(filters.maxPeopleNow?.toString() || '');
    const [minSquare, setMinSquare] = useState(filters.minSquare?.toString() || '');
    const [maxSquare, setMaxSquare] = useState(filters.maxSquare?.toString() || '');
    const [city, setCity] = useState(filters.city || '');
    const handleApplyFilters = () => {
        const newFilters = {
            minCount: minCount ? Number(minCount) : undefined,
            maxCount: maxCount ? Number(maxCount) : undefined,
            minFloor: minFloor ? Number(minFloor) : undefined,
            maxFloor: maxFloor ? Number(maxFloor) : undefined,
            minPeople: minPeople ? Number(minPeople) : undefined,
            maxPeople: maxPeople ? Number(maxPeople) : undefined,
            minPeopleNow: minPeopleNow ? Number(minPeopleNow) : undefined,
            maxPeopleNow: maxPeopleNow ? Number(maxPeopleNow) : undefined,
            minSquare: minSquare ? Number(minSquare) : undefined,
            maxSquare: maxSquare ? Number(maxSquare) : undefined,
            city: city || undefined,
        };
        setFilters(newFilters);
        navigate('/'); // Возвращаемся на страницу с квартирами
    };
    const handleReset = () => {
        setMinCount('');
        setMaxCount('');
        setMinFloor('');
        setMaxFloor('');
        setMinPeople('');
        setMaxPeople('');
        setMinPeopleNow('');
        setMaxPeopleNow('');
        setMinSquare('');
        setMaxSquare('');
        setCity('');
        resetFilters();
    };
    return (_jsx("div", { className: utils.container, children: _jsxs("div", { className: styles.filterPage, children: [_jsxs("div", { className: styles.filtersCard, children: [_jsx("label", { className: styles.filtersCard_label, children: "\u041A\u043E\u043B\u0438\u0447\u0435\u0441\u0442\u0432\u043E \u043A\u043E\u043C\u043D\u0430\u0442 " }), _jsxs("div", { className: styles.rangeInputs, children: [_jsx("input", { type: "number", placeholder: "\u041E\u0442", value: minCount, onChange: (e) => setMinCount(e.target.value) }), _jsx("span", { children: "\u2014" }), _jsx("input", { type: "number", placeholder: "\u0414\u043E", value: maxCount, onChange: (e) => setMaxCount(e.target.value) })] })] }), _jsxs("div", { className: styles.filtersCard, children: [_jsx("label", { className: styles.filtersCard_label, children: "\u041F\u043B\u043E\u0449\u0430\u0434\u044C (\u043C\u00B2)" }), _jsxs("div", { className: styles.rangeInputs, children: [_jsx("input", { type: "number", placeholder: "\u041E\u0442", value: minSquare, onChange: (e) => setMinSquare(e.target.value) }), _jsx("span", { children: "\u2014" }), _jsx("input", { type: "number", placeholder: "\u0414\u043E", value: maxSquare, onChange: (e) => setMaxSquare(e.target.value) })] })] }), _jsxs("div", { className: styles.filtersCard, children: [_jsx("label", { className: styles.filtersCard_label, children: "\u0413\u043E\u0440\u043E\u0434" }), _jsx("input", { type: "text", placeholder: "\u041D\u0430\u043F\u0440\u0438\u043C\u0435\u0440: \u041C\u043E\u0441\u043A\u0432\u0430", className: styles.inputField, value: city, onChange: (e) => setCity(e.target.value) })] }), _jsxs("div", { className: styles.filtersCard, children: [_jsx("label", { className: styles.filtersCard_label, children: "\u042D\u0442\u0430\u0436 " }), _jsxs("div", { className: styles.rangeInputs, children: [_jsx("input", { type: "number", placeholder: "\u041E\u0442", value: minFloor, onChange: (e) => setMinFloor(e.target.value) }), _jsx("span", { children: "\u2014" }), _jsx("input", { type: "number", placeholder: "\u0414\u043E", value: maxFloor, onChange: (e) => setMaxFloor(e.target.value) })] })] }), _jsxs("div", { className: styles.filtersCard, children: [_jsx("label", { className: styles.filtersCard_label, children: "\u041A\u043E\u043B\u0438\u0447\u0435\u0441\u0442\u0432\u043E \u043F\u043E\u0442\u0435\u043D\u0446\u0438\u0430\u043B\u044C\u043D\u044B\u0445 \u0441\u043E\u0441\u0435\u0434\u0435\u0439 " }), _jsxs("div", { className: styles.rangeInputs, children: [_jsx("input", { type: "number", placeholder: "\u041E\u0442", value: minPeople, onChange: (e) => setMinPeople(e.target.value) }), _jsx("span", { children: "\u2014" }), _jsx("input", { type: "number", placeholder: "\u0414\u043E", value: maxPeople, onChange: (e) => setMaxPeople(e.target.value) })] })] }), _jsxs("div", { className: styles.filtersCard, children: [_jsx("label", { className: styles.filtersCard_label, children: "\u041A\u043E\u043B\u0438\u0447\u0435\u0441\u0442\u0432\u043E \u043F\u0440\u043E\u0436\u0438\u0432\u0430\u044E\u0449\u0438\u0445 \u0441\u0435\u0439\u0447\u0430\u0441 \u043B\u044E\u0434\u0435\u0439 " }), _jsxs("div", { className: styles.rangeInputs, children: [_jsx("input", { type: "number", placeholder: "\u041E\u0442", value: minPeopleNow, onChange: (e) => setMinPeopleNow(e.target.value) }), _jsx("span", { children: "\u2014" }), _jsx("input", { type: "number", placeholder: "\u0414\u043E", value: maxPeopleNow, onChange: (e) => setMaxPeopleNow(e.target.value) })] })] }), _jsxs("div", { className: styles.buttons, children: [_jsxs(Button, { onClickAdditional: handleApplyFilters, children: [" ", _jsx(Icon, { Icon: RxCheck }), "\u041F\u0440\u0438\u043C\u0435\u043D\u0438\u0442\u044C"] }), _jsxs(Button, { onClickAdditional: handleReset, children: [" ", _jsx(Icon, { Icon: RxCross2 }), " \u0421\u0431\u0440\u043E\u0441\u0438\u0442\u044C"] })] })] }) }));
};
export default Filter;
