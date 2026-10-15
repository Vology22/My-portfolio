import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Routes, Route } from 'react-router-dom';
import { Layout, Questionnaires, Profile, Favorite, Filter } from './pages';
import { FilterProvider } from './contexts/FilterContext';
const App = () => {
    return (_jsx(FilterProvider, { children: _jsx(Layout, { children: _jsxs(Routes, { children: [_jsx(Route, { path: '/', element: _jsx(Questionnaires, {}) }), _jsx(Route, { path: '/profile', element: _jsx(Profile, {}) }), _jsx(Route, { path: '/like', element: _jsx(Favorite, {}) }), _jsx(Route, { path: '/filter', element: _jsx(Filter, {}) })] }) }) }));
};
export default App;
