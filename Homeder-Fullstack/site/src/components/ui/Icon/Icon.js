import { jsx as _jsx } from "react/jsx-runtime";
import styles from "./icon.module.scss";
const Icon = ({ Icon, className }) => {
    return (_jsx(Icon, { className: `${styles.icon} ${className || ''}` }));
};
export default Icon;
