import { jsx as _jsx } from "react/jsx-runtime";
import { useEffect, useRef } from "react";
import styles from "./animatedScroll.module.scss";
export const top = {
    opacity: 0,
    transform: "translate(0, -50px)"
};
export const bottom = {
    opacity: 0,
    transform: "translate(0, 50px)"
};
export const left = {
    opacity: 0,
    transform: "translate(-50px, 0)"
};
export const right = {
    opacity: 0,
    transform: "translate(50px, 0)"
};
export const none = {
    opacity: 0
};
const AnimatedScroll = ({ children, className, scrollType = bottom, delay = 2 }) => {
    const ref = useRef(null);
    const timer = useRef(null);
    useEffect(() => {
        const options = { threshold: [0, 0.8] };
        const observer = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    timer.current = setTimeout(() => {
                        const element = entry.target;
                        element.style.opacity = "1";
                        element.style.transform = "translate(0, 0)";
                        observer.unobserve(element);
                    }, 100 * delay);
                }
            });
        }, options);
        if (ref.current)
            observer.observe(ref.current);
        return () => {
            observer.disconnect();
            if (timer.current) {
                clearTimeout(timer.current);
                timer.current = null;
            }
        };
    }, [delay]);
    return (_jsx("div", { ref: ref, className: `${className || ""} ${styles.lazyLoading}`, style: scrollType, children: children }));
};
export default AnimatedScroll;
