import styles from "./questionnaires.module.scss";
import utils from "../../scss/utils.module.scss";
import { Skeleton } from "../../components/ui";
import { useState } from "react";
import { ListCards } from "../../components/widgets";

const Questionnaires = () => {
   const [isLoading, _] = useState(false); 

   return ( 
      <>
         <section className={styles.wrapper}>
            <div className={utils.container}>
               <div className={styles.content}>
                  {isLoading ? <>
                     <Skeleton height={300} />
                     <Skeleton count={3} />
                     <Skeleton height={50} />
                  </> : <ListCards />}
               </div>
            </div>
         </section>
      </>
   );
}
 
export default Questionnaires;