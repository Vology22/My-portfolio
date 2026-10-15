import { jsx as _jsx, Fragment as _Fragment } from "react/jsx-runtime";
import classObject from "clsx";
import { Link, useMatch } from 'react-router-dom';
import styles from './navLink.module.scss';
import { getTgId } from "../../../utils/tg.utils";
const NavLink = ({ path, children, className, isPurple = false }) => {
    const match = useMatch(path);
    let finalPath = path;
    const tgId = getTgId();
    if (tgId) {
        finalPath = `${path}?tg_id=${tgId}`;
    }
    return (_jsx(_Fragment, { children: _jsx(Link, { to: finalPath, className: classObject(styles.navlink, className, {
                [styles.active]: match,
                [styles.activePurple]: isPurple && match
            }), children: children }) }));
};
export default NavLink;
