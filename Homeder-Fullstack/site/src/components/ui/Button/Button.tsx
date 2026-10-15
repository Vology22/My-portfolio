import { ReactNode, useCallback, useEffect, useRef } from "react";
import styles from "./button.module.scss"

interface TypesButton{
   children: ReactNode,
   onClickAdditional?: (event: React.MouseEvent<HTMLButtonElement>) => void,
   className?: string,
   type?: "button" | "submit" | "reset",
   disabled?: boolean,
}

const Button = ({children, onClickAdditional, className, type = "button",  disabled = false}: TypesButton) => {
   const animationRef = useRef<number | null>(null);
   const handleClick = useCallback((event: React.MouseEvent<HTMLButtonElement>) => {
      if (disabled) return;
      const target = event.currentTarget;
      const rect = target.getBoundingClientRect();
      const sizeElement = rect.width / 10;
      const elementX = event.clientX - rect.left - sizeElement / 2;
      const elementY = event.clientY - rect.top - sizeElement / 2;

      const element = document.createElement('span');
      target.appendChild(element);
      element.style.width = `${sizeElement}px`;
      element.style.height = `${sizeElement}px`;
      element.style.left = `${elementX}px`;
      element.style.top = `${elementY}px`;

      const bgColor = getComputedStyle(target).color.match(/\d+(\.\d+)?/g);
      if (!bgColor) return;
      element.style.backgroundColor = `rgba(${bgColor[0]}, ${bgColor[1]}, ${bgColor[2]}, 0.2)`;

      const startTime = performance.now();
      const animate = () => {
         const progress = Math.min((performance.now() - startTime) / 800, 1);
         const opacity = Math.max(0, 1 - progress*4);
         element.style.transform = `scale(${1 + progress * 80})`;
         element.style.opacity = opacity.toString();
         if (progress < 1) {
            animationRef.current = requestAnimationFrame(animate);
         } else element.remove();
      }
      animationRef.current = requestAnimationFrame(animate);

      onClickAdditional?.(event);
   }, [onClickAdditional, disabled])

   useEffect(() => {
      return () => {
         if (animationRef.current) cancelAnimationFrame(animationRef.current);
      }
   }, [])

   return ( 
      <>
         <button type={type} className={`${styles.button} ${className || ''}`} onClick={(event) => {handleClick(event)}} disabled={disabled}>{children}</button>
      </>   
   );
}
 
export default Button;