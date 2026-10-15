import { createContext, useContext, useState, ReactNode } from 'react';

export interface Filters {
  minCount?: number;
  maxCount?: number;
  minFloor?: number;
  maxFloor?: number;
  minPeople?: number;
  maxPeople?: number;
  minPeopleNow?: number;
  maxPeopleNow?: number;
  minSquare?: number;
  maxSquare?: number;
  city?: string;
}

interface FilterContextType {
  filters: Filters;
  setFilters: (filters: Filters) => void;
  resetFilters: () => void;
}

const FilterContext = createContext<FilterContextType | undefined>(undefined);

export const FilterProvider = ({ children }: { children: ReactNode }) => {
  const [filters, setFilters] = useState<Filters>({});

  const resetFilters = () => setFilters({});

  return (
    <FilterContext.Provider value={{ filters, setFilters, resetFilters }}>
      {children}
    </FilterContext.Provider>
  );
};

export const useFilters = () => {
  const context = useContext(FilterContext);
  if (!context) {
    throw new Error('useFilters must be used within FilterProvider');
  }
  return context;
};