import { jsx as _jsx, Fragment as _Fragment } from "react/jsx-runtime";
import styles from "./skeleton.module.scss";
const Skeleton = ({ type = 'rect', width = "100%", height = "1rem", count = 1, className }) => {
    const skeletons = [];
    for (let i = 0; i < count; i++)
        skeletons.push(_jsx("div", { style: { width, height, borderRadius: type == 'circle' ? '50%' : 5 }, className: `${styles.skeleton} ${className || ''}` }, i));
    return (_jsx(_Fragment, { children: skeletons }));
};
export default Skeleton;
