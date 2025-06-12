import React from 'react';
import { useQuery } from '@tanstack/react-query';
import config from '../config';

interface FilterBarProps {
  onFiltersChange: (filters: {
    models: string[];
    endpoints: string[];
  }) => void;
}

const fetchFilters = async () => {
  const response = await fetch(`${config.apiUrl}/api/filters`);
  if (!response.ok) {
    throw new Error('Failed to fetch filters');
  }
  return response.json();
};

export const FilterBar: React.FC<FilterBarProps> = ({ onFiltersChange }) => {
  const { data: filterOptions, isLoading } = useQuery({
    queryKey: ['filters'],
    queryFn: fetchFilters
  });

  const [selectedModels, setSelectedModels] = React.useState<string[]>([]);
  const [selectedEndpoints, setSelectedEndpoints] = React.useState<string[]>([]);

  // Update filters when selections change
  React.useEffect(() => {
    onFiltersChange({
      models: selectedModels,
      endpoints: selectedEndpoints
    });
  }, [selectedModels, selectedEndpoints, onFiltersChange]);

  if (isLoading) {
    return <div className="animate-pulse bg-gray-100 h-12 rounded-lg"></div>;
  }

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm space-y-4">
      <div className="flex flex-wrap gap-4">
        {/* Time Period Label */}
        <div className="flex-1 min-w-[200px]">
          <label className="block text-sm font-medium text-gray-700 mb-1">Time Period</label>
          <div className="text-sm text-gray-600">Last 12 Months</div>
        </div>

        {/* Model Filter */}
        <div className="flex-1 min-w-[200px]">
          <label className="block text-sm font-medium text-gray-700 mb-1">Models</label>
          <select
            className="w-full rounded-md border border-gray-300 shadow-sm px-3 py-2 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            multiple
            value={selectedModels}
            onChange={(e) => setSelectedModels(Array.from(e.target.selectedOptions, option => option.value))}
          >
            {filterOptions?.models?.map((model: string) => (
              <option key={model} value={model}>{model}</option>
            ))}
          </select>
        </div>

        {/* Endpoint Filter */}
        <div className="flex-1 min-w-[200px]">
          <label className="block text-sm font-medium text-gray-700 mb-1">Endpoints</label>
          <select
            className="w-full rounded-md border border-gray-300 shadow-sm px-3 py-2 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            multiple
            value={selectedEndpoints}
            onChange={(e) => setSelectedEndpoints(Array.from(e.target.selectedOptions, option => option.value))}
          >
            {filterOptions?.endpoints?.map((endpoint: string) => (
              <option key={endpoint} value={endpoint}>{endpoint}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Reset Button */}
      <button
        className="text-sm text-gray-600 hover:text-gray-900"
        onClick={() => {
          setSelectedModels([]);
          setSelectedEndpoints([]);
        }}
      >
        Reset Filters
      </button>
    </div>
  );
}; 