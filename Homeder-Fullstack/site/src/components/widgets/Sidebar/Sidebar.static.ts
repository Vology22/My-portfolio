import { VscSettings } from "react-icons/vsc";
import { AiOutlineHome } from "react-icons/ai";
import { IoMdHeartEmpty } from "react-icons/io";
import { isTabletSmall } from "../../../utils/media.utils";

export const navigations = [
   {
      id: 0,
      text: "Анкеты",
      image: AiOutlineHome,
      path: "/"
   },
   {
      id: 1,
      text: isTabletSmall() ? "Избранное" : "Понравившееся жильё",
      image: IoMdHeartEmpty,
      path: "/like"
   },
   {
      id: 2,
      text: "Фильтры",
      image: VscSettings,
      path: "/filter"
   }
]