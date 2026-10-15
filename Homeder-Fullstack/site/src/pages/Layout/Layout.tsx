import { ReactNode } from "react";
import { Header } from "../../components/widgets";

const Layout = ({children}: {children: Readonly<ReactNode>}) => {
   return ( 
      <>
         <Header />
         <main style={{flexGrow: "1"}}>
            {children}
         </main>
      </>
   );
}
 
export default Layout;