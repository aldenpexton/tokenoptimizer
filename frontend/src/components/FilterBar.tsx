import { useState, useRef, useEffect } from 'react';
import { useFilters } from '../contexts/FilterContext';
import type { FilterState } from '../contexts/FilterContext';
import { ChevronLeft, ChevronRight, Calendar, ChevronDown } from 'lucide-react';

// Date range presets
const DATE_PRESETS = [
  { label: '24h', days: 1 },
  { label: '7d', days: 7 },
  { label: '30d', days: 30 },
  { label: 'Custom', days: 0 }
];

// Interval options
const INTERVAL_OPTIONS = [
  { value: 'month', label: 'Month' },
  { value: 'week', label: 'Week' },
  { value: 'day', label: 'Day' }
];

const FilterBar = () => {
  const { filters, setFilters, taskOptions, modelOptions, isLoading } = useFilters();
  const [activePreset, setActivePreset] = useState<string>('30d');
  const [showIntervalDropdown, setShowIntervalDropdown] = useState(false);
  const intervalDropdownRef = useRef<HTMLDivElement>(null);
  
  // Handle outside click for dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (intervalDropdownRef.current && !intervalDropdownRef.current.contains(event.target as Node)) {
        setShowIntervalDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);
  
  // Format date for display
  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    });
  };

  // Format date for display in the time navigation element
  const formatDateForNav = () => {
    const { from, to, interval } = filters;
    
    // For single day view
    if (interval === 'day') {
      return formatDate(to);
    }
    
    // For week view
    if (interval === 'week') {
      // The bar chart shows Sunday to Saturday, so we need to calculate those dates
      // Start with the 'to' date and find the current week's Saturday
      const endDate = new Date(to);
      // Adjust to make sure we're on Saturday (6 = Saturday in JS Date)
      const daysUntilSaturday = 6 - endDate.getDay();
      const saturday = new Date(endDate);
      saturday.setDate(endDate.getDate() + daysUntilSaturday);
      
      // Calculate Sunday (6 days before Saturday)
      const sunday = new Date(saturday);
      sunday.setDate(saturday.getDate() - 6);
      
      // Format the date range
      const sundayMonth = sunday.toLocaleDateString('en-US', { month: 'short' });
      const saturdayMonth = saturday.toLocaleDateString('en-US', { month: 'short' });
      const sundayDay = sunday.getDate();
      const saturdayDay = saturday.getDate();
      const year = saturday.getFullYear();
      
      // If same month, show "May 11-17, 2025"
      if (sundayMonth === saturdayMonth) {
        return `${sundayMonth} ${sundayDay}-${saturdayDay}, ${year}`;
      } 
      // If different months, show "Apr 28-May 4, 2025"
      else {
        return `${sundayMonth} ${sundayDay}-${saturdayMonth} ${saturdayDay}, ${year}`;
      }
    }
    
    // For month view
    if (interval === 'month') {
      return to.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
    }
    
    return formatDate(to);
  };
  
  // Handle date preset change
  const handleDatePresetChange = (preset: string, days: number) => {
    setActivePreset(preset);
    
    if (days > 0) {
      const to = new Date();
      const from = new Date();
      from.setDate(from.getDate() - days);
      setFilters({ from, to });
    }
  };
  
  // Navigate date range back/forward
  const navigateDate = (direction: 'back' | 'forward') => {
    const { interval, from, to } = filters;
    const newFrom = new Date(from);
    const newTo = new Date(to);
    
    // Calculate the adjustment based on interval
    switch (interval) {
      case 'day':
        // Move by 1 day
        if (direction === 'back') {
          newFrom.setDate(newFrom.getDate() - 1);
          newTo.setDate(newTo.getDate() - 1);
        } else {
          newFrom.setDate(newFrom.getDate() + 1);
          newTo.setDate(newTo.getDate() + 1);
        }
        break;
        
      case 'week':
        // Move by 7 days
        if (direction === 'back') {
          newFrom.setDate(newFrom.getDate() - 7);
          newTo.setDate(newTo.getDate() - 7);
        } else {
          newFrom.setDate(newFrom.getDate() + 7);
          newTo.setDate(newTo.getDate() + 7);
        }
        break;
        
      case 'month':
        // Move by 1 month
        if (direction === 'back') {
          newFrom.setMonth(newFrom.getMonth() - 1);
          newTo.setMonth(newTo.getMonth() - 1);
        } else {
          newFrom.setMonth(newFrom.getMonth() + 1);
          newTo.setMonth(newTo.getMonth() + 1);
        }
        break;
        
      default:
        // For any other interval, use the date difference
        const range = to.getTime() - from.getTime();
        const days = Math.round(range / (1000 * 60 * 60 * 24));
        
        if (direction === 'back') {
          newFrom.setDate(newFrom.getDate() - days);
          newTo.setDate(newTo.getDate() - days);
        } else {
          newFrom.setDate(newFrom.getDate() + days);
          newTo.setDate(newTo.getDate() + days);
        }
    }
    
    // Don't allow going into the future
    const now = new Date();
    if (newTo > now) {
      const diff = newTo.getTime() - now.getTime();
      newFrom.setTime(newFrom.getTime() - diff);
      newTo.setTime(now.getTime());
    }
    
    setFilters({ from: newFrom, to: newTo });
  };
  
  // Change the display interval
  const setInterval = (interval: 'day' | 'week' | 'month') => {
    setFilters({ interval });
    setShowIntervalDropdown(false);
  };
  
  return (
    <div className="flex flex-wrap items-center gap-4 mb-6">
      {/* Model Select (Anthropic Style) */}
      <div className="relative">
        <button 
          className="bg-black text-white px-4 py-2 rounded-md flex items-center gap-1 min-w-[150px]"
          onClick={() => {}} // This would open a modal with model selection
        >
          {filters.model === '*' ? 'All Models' : filters.model}
          <ChevronDown size={16} />
        </button>
      </div>
      
      {/* Interval Select (Anthropic Style) */}
      <div className="relative" ref={intervalDropdownRef}>
        <button 
          className="bg-black text-white px-4 py-2 rounded-md flex items-center gap-1 min-w-[120px]"
          onClick={() => setShowIntervalDropdown(!showIntervalDropdown)}
        >
          {INTERVAL_OPTIONS.find(option => option.value === filters.interval)?.label || 'Day'}
          <ChevronDown size={16} />
        </button>
        
        {/* Dropdown Menu */}
        {showIntervalDropdown && (
          <div className="absolute z-10 mt-1 w-48 bg-black rounded-md shadow-lg py-1">
            {INTERVAL_OPTIONS.map(option => (
              <button
                key={option.value}
                className="w-full px-4 py-2 text-left text-white flex items-center justify-between"
                onClick={() => setInterval(option.value as 'day' | 'week' | 'month')}
              >
                {option.label}
                {filters.interval === option.value && (
                  <div className="w-4 h-4 rounded-full bg-white"></div>
                )}
              </button>
            ))}
          </div>
        )}
      </div>
      
      {/* Date Navigation (Anthropic Style) */}
      <div className="flex items-center bg-black text-white rounded-md overflow-hidden">
        <button 
          className="p-2 hover:bg-gray-800"
          onClick={() => navigateDate('back')}
        >
          <ChevronLeft size={16} />
        </button>
        
        <div className="px-4 py-2 min-w-[130px] text-center">
          {formatDateForNav()}
        </div>
        
        <button 
          className="p-2 hover:bg-gray-800"
          onClick={() => navigateDate('forward')}
        >
          <ChevronRight size={16} />
        </button>
      </div>
      
      {/* Task Filter */}
      <div className="flex-1">
        <select
          className="w-full bg-black text-white border border-gray-700 rounded-md px-3 py-2 text-sm"
          value={filters.task}
          onChange={(e) => setFilters({ task: e.target.value })}
          disabled={isLoading}
        >
          {taskOptions.map(option => (
            <option key={option} value={option}>
              {option === '*' ? 'All Tasks' : option}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default FilterBar; 