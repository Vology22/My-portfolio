import { Button, Icon, NavLink } from "../../ui";
import styles from "./sidebar.module.scss";
import { navigations } from "./Sidebar.static";

const Sidebar = () => {
   return ( 
      <>
         <div className={styles.sidebar}>
            {navigations.map(item => {return(
               <NavLink key={item.id} className={styles.sidebar_link} path={item.path}>
                  <Button  className={styles.sidebar_button}>
                     <Icon Icon={item.image} />
                     <p>{item.text}</p>
                  </Button>
               </NavLink>
            )})}
         </div>
      </>
   );
}
 
export default Sidebar;