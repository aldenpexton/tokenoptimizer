import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import axios from 'axios';

// API base URL - use environment variable if available or fallback to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL ? 
  `${import.meta.env.VITE_API_URL}/api` : 
  'http://localhost:5001/api';

export type FilterState = {
  from: Date       // default = now-30d
  to: Date         // default = now
  task: string     // '*' = all
  model: string    // '*' = all
  interval: 'day' | 'week' | 'month' | 'year'  // time aggregation
};

type FilterContextType = {
  filters: FilterState;
  setFilters: (filters: Partial<FilterState>) => void;
  taskOptions: string[];
  modelOptions: string[];
  isLoading: boolean;
};

const getDefaultDateRange = () => {
  const to = new Date();
  const from = new Date();
  from.setDate(from.getDate() - 30);
  return { from, to };
};

const initialState: FilterState = {
  ...getDefaultDateRange(),
  task: '*',
  model: '*',
  interval: 'day',
};

// Create the context with a default value
const FilterContext = createContext<FilterContextType>({
  filters: initialState,
  setFilters: () => {},
  taskOptions: [],
  modelOptions: [],
  isLoading: false,
});

// Custom hook to use the filter context
export const useFilters = () => useContext(FilterContext);

// Format date for URL parameters
const formatDateParam = (date: Date) => date.toISOString().split('T')[0];

export const FilterProvider = ({ children }: { children: ReactNode }) => {
  const [filters, setFiltersState] = useState<FilterState>(initialState);
  const [taskOptions, setTaskOptions] = useState<string[]>([]);
  const [modelOptions, setModelOptions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Load options for task and model selects
  useEffect(() => {
    const loadOptions = async () => {
      setIsLoading(true);
      try {
        // Load task options
        const taskResponse = await axios.get(`${API_BASE_URL}/distinct`, { 
          params: { field: 'endpoint_name' } 
        });
        setTaskOptions(['*', ...taskResponse.data]);

        // Load model options
        const modelResponse = await axios.get(`${API_BASE_URL}/distinct`, { 
          params: { field: 'model' } 
        });
        setModelOptions(['*', ...modelResponse.data]);
      } catch (error) {
        console.error('Failed to load filter options:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadOptions();
  }, []);

  // Initialize filters from URL on first load
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const fromParam = params.get('from');
    const toParam = params.get('to');
    const taskParam = params.get('task');
    const modelParam = params.get('model');
    const intervalParam = params.get('interval');

    const newFilters: Partial<FilterState> = {};

    if (fromParam) {
      newFilters.from = new Date(fromParam);
    }
    if (toParam) {
      newFilters.to = new Date(toParam);
    }
    if (taskParam) {
      newFilters.task = taskParam;
    }
    if (modelParam) {
      newFilters.model = modelParam;
    }
    if (intervalParam && ['day', 'week', 'month', 'year'].includes(intervalParam)) {
      newFilters.interval = intervalParam as 'day' | 'week' | 'month' | 'year';
    }

    if (Object.keys(newFilters).length > 0) {
      setFiltersState(prev => ({ ...prev, ...newFilters }));
    }
  }, []);

  // Update filters and handle side effects
  const setFilters = (newFilters: Partial<FilterState>) => {
    // Update state
    setFiltersState(prev => {
      const updated = { ...prev, ...newFilters };
      
      // Update URL parameters
      const params = new URLSearchParams();
      params.set('from', formatDateParam(updated.from));
      params.set('to', formatDateParam(updated.to));
      params.set('task', updated.task);
      params.set('model', updated.model);
      params.set('interval', updated.interval);
      
      // Push to history without full page reload
      const url = `${window.location.pathname}?${params.toString()}`;
      window.history.pushState({ path: url }, '', url);
      
      // Emit custom event
      const event = new CustomEvent('filter-changed', { detail: updated });
      window.dispatchEvent(event);
      
      return updated;
    });
  };

  return (
    <FilterContext.Provider value={{ filters, setFilters, taskOptions, modelOptions, isLoading }}>
      {children}
    </FilterContext.Provider>
  );
}; 