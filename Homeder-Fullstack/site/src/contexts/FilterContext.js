import { jsx as _jsx } from "react/jsx-runtime";
import { createContext, useContext, useState } from 'react';
const FilterContext = createContext(undefined);
export const FilterProvider = ({ children }) => {
    const [filters, setFilters] = useState({});
    const resetFilters = () => setFilters({});
    return (_jsx(FilterContext.Provider, { value: { filters, setFilters, resetFilters }, children: children }));
};
export const useFilters = () => {
    const context = useContext(FilterContext);
    if (!context) {
        throw new Error('useFilters must be used within FilterProvider');
    }
    return context;
};
