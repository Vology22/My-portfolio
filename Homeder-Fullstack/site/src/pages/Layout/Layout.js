import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
import { Header } from "../../components/widgets";
const Layout = ({ children }) => {
    return (_jsxs(_Fragment, { children: [_jsx(Header, {}), _jsx("main", { style: { flexGrow: "1" }, children: children })] }));
};
export default Layout;
