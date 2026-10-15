import styles from "./icon.module.scss";
import { IconType } from "react-icons";

interface IIcon{
   Icon: IconType,
   className?: string,
}

const Icon = ({Icon, className}: IIcon) => {
   return ( 
      <Icon className={`${styles.icon} ${className || ''}`} />
   );
}
 
export default Icon;