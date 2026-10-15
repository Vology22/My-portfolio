import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { Button, Icon, NavLink } from "../../ui";
import styles from "./sidebar.module.scss";
import { navigations } from "./Sidebar.static";
const Sidebar = () => {
    return (_jsx(_Fragment, { children: _jsx("div", { className: styles.sidebar, children: navigations.map(item => {
                return (_jsx(NavLink, { className: styles.sidebar_link, path: item.path, children: _jsxs(Button, { className: styles.sidebar_button, children: [_jsx(Icon, { Icon: item.image }), _jsx("p", { children: item.text })] }) }, item.id));
            }) }) }));
};
export default Sidebar;
