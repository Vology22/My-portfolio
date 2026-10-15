import styles from "./skeleton.module.scss";

interface ISkeleton{
   type: "rect" | "circle",
   width: string | number,
   height: string | number,
   count: number,
   className: string,
}

const Skeleton = ({type = 'rect', width = "100%", height = "1rem", count = 1, className}: Partial<ISkeleton>) => {
   const skeletons = [];
   for (let i = 0; i < count; i++) skeletons.push(
      <div style={{width, height, borderRadius: type == 'circle' ? '50%' : 5}}
      key={i} className={`${styles.skeleton} ${className || ''}`} />
   );

   return ( 
      <>{skeletons}</>
   );
}
 
export default Skeleton;