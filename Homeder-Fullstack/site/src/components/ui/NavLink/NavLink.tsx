import { ReactNode } from 'react';
import classObject from "clsx";
import { Link, useMatch} from 'react-router-dom';
import styles from './navLink.module.scss';
import { getTgId } from "../../../utils/tg.utils";

interface INavLink{
   path: string,
   children: Readonly<ReactNode>
   className?: string,
   isPurple?: boolean
}

const NavLink = ({path, children, className, isPurple = false}: INavLink) => {
   const match = useMatch(path);

   let finalPath = path;
   const tgId = getTgId();
   if (tgId) {
      finalPath = `${path}?tg_id=${tgId}`;
   }

   return ( 
      <>
         <Link to={finalPath} className={classObject(styles.navlink, className, {
            [styles.active]: match,
            [styles.activePurple]: isPurple && match
         })}>{children}</Link>
      </>
   );
}

export default NavLink;