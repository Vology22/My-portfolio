import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import styles from "./header.module.scss";
import utils from "../../../scss/utils.module.scss";
import { FaRegUser } from "react-icons/fa";
import { Button, Icon, NavLink } from "../../ui";
import { Sidebar } from "..";
const Header = () => {
    return (_jsx(_Fragment, { children: _jsx("header", { className: styles.header, children: _jsx("div", { className: utils.container, children: _jsxs("div", { className: styles.header_body, children: [_jsx("div", { className: styles.icon, children: _jsx("img", { src: "src\\assets\\png\\icon.png", alt: "icon" }) }), _jsx("nav", { className: styles.navigation, children: _jsx(NavLink, { className: styles.navigation_link, isPurple: true, path: "/profile", children: _jsx(Button, { className: styles.navigation_button, children: _jsx(Icon, { Icon: FaRegUser }) }) }) }), _jsx(Sidebar, {})] }) }) }) }));
};
export default Header;
