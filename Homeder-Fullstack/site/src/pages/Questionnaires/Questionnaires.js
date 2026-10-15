import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
import styles from "./questionnaires.module.scss";
import utils from "../../scss/utils.module.scss";
import { Skeleton } from "../../components/ui";
import { useState } from "react";
import { ListCards } from "../../components/widgets";
const Questionnaires = () => {
    const [isLoading, _] = useState(false);
    return (_jsx(_Fragment, { children: _jsx("section", { className: styles.wrapper, children: _jsx("div", { className: utils.container, children: _jsx("div", { className: styles.content, children: isLoading ? _jsxs(_Fragment, { children: [_jsx(Skeleton, { height: 300 }), _jsx(Skeleton, { count: 3 }), _jsx(Skeleton, { height: 50 })] }) : _jsx(ListCards, {}) }) }) }) }));
};
export default Questionnaires;
