import styles from "./header.module.scss"
import utils from "../../../scss/utils.module.scss"
import { FaRegUser } from "react-icons/fa";
import { Button, Icon, NavLink } from "../../ui";
import { Sidebar } from "..";

const Header = () => {
   return ( 
      <>
         <header className={styles.header}>
            <div className={utils.container}>
               <div className={styles.header_body}>
                  <div className={styles.icon}>
                     <img src="src\assets\png\icon.png" alt="icon" />
                  </div>
                  <nav className={styles.navigation}>
                     <NavLink className={styles.navigation_link} isPurple path="/profile">
                        <Button className={styles.navigation_button}>
                           <Icon Icon={FaRegUser}/>
                        </Button>
                     </NavLink>
                  </nav>
                  <Sidebar />
               </div>
            </div>
         </header>
      </>
   );
}
 
export default Header;