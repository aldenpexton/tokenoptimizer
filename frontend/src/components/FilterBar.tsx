import React from 'react';
import { useQuery } from '@tanstack/react-query';
import config from '../config';
import { FilterParams } from '../types/api';

interface FilterBarProps {
  filters: FilterParams;
  onFiltersChange: (filters: FilterParams) => void;
}

interface FilterRelationships {
  model_endpoints: Record<string, string[]>;
  model_providers: Record<string, string[]>;
  endpoint_providers: Record<string, string[]>;
  provider_models: Record<string, string[]>;
  provider_endpoints: Record<string, string[]>;
  endpoint_models: Record<string, string[]>;
}

const fetchFilters = async () => {
  const response = await fetch(`${config.apiUrl}/api/filters`);
  if (!response.ok) {
    throw new Error('Failed to fetch filters');
  }
  return response.json();
};

export const FilterBar: React.FC<FilterBarProps> = ({ filters, onFiltersChange }) => {
  const { data: filterOptions, isLoading } = useQuery({
    queryKey: ['filters'],
    queryFn: fetchFilters
  });

  // Initialize local state from props
  const [selectedModels, setSelectedModels] = React.useState<string[]>(filters.models || []);
  const [selectedEndpoints, setSelectedEndpoints] = React.useState<string[]>(filters.endpoints || []);
  const [selectedProviders, setSelectedProviders] = React.useState<string[]>(filters.providers || []);

  // Update local state when props change
  React.useEffect(() => {
    setSelectedModels(filters.models || []);
    setSelectedEndpoints(filters.endpoints || []);
    setSelectedProviders(filters.providers || []);
  }, [filters]);

  // Handle removing individual filters
  const removeModel = (model: string) => {
    const newModels = selectedModels.filter(m => m !== model);
    setSelectedModels(newModels);
    onFiltersChange({
      ...filters,
      models: newModels
    });
  };

  const removeEndpoint = (endpoint: string) => {
    const newEndpoints = selectedEndpoints.filter(e => e !== endpoint);
    setSelectedEndpoints(newEndpoints);
    onFiltersChange({
      ...filters,
      endpoints: newEndpoints
    });
  };

  const removeProvider = (provider: string) => {
    const newProviders = selectedProviders.filter(p => p !== provider);
    setSelectedProviders(newProviders);
    onFiltersChange({
      ...filters,
      providers: newProviders
    });
  };

  // Filter available options based on selections
  const getFilteredOptions = () => {
    if (!filterOptions?.relationships) {
      return {
        availableModels: filterOptions?.models || [],
        availableEndpoints: filterOptions?.endpoints || [],
        availableProviders: filterOptions?.providers || []
      };
    }

    const relationships: FilterRelationships = filterOptions.relationships;
    let availableModels = new Set<string>(filterOptions.models);
    let availableEndpoints = new Set<string>(filterOptions.endpoints);
    let availableProviders = new Set<string>(filterOptions.providers);

    // Filter based on selected endpoints
    if (selectedEndpoints.length > 0) {
      const validModels = new Set<string>();
      const validProviders = new Set<string>();
      
      selectedEndpoints.forEach(endpoint => {
        relationships.endpoint_models[endpoint]?.forEach(model => validModels.add(model));
        relationships.endpoint_providers[endpoint]?.forEach(provider => validProviders.add(provider));
      });
      
      availableModels = new Set<string>(Array.from(availableModels).filter(model => validModels.has(model)));
      availableProviders = new Set<string>(Array.from(availableProviders).filter(provider => validProviders.has(provider)));
    }

    // Filter based on selected providers
    if (selectedProviders.length > 0) {
      const validModels = new Set<string>();
      const validEndpoints = new Set<string>();
      
      selectedProviders.forEach(provider => {
        relationships.provider_models[provider]?.forEach(model => validModels.add(model));
        relationships.provider_endpoints[provider]?.forEach(endpoint => validEndpoints.add(endpoint));
      });
      
      availableModels = new Set<string>(Array.from(availableModels).filter(model => validModels.has(model)));
      availableEndpoints = new Set<string>(Array.from(availableEndpoints).filter(endpoint => validEndpoints.has(endpoint)));
    }

    // Filter based on selected models
    if (selectedModels.length > 0) {
      const validEndpoints = new Set<string>();
      const validProviders = new Set<string>();
      
      selectedModels.forEach(model => {
        relationships.model_endpoints[model]?.forEach(endpoint => validEndpoints.add(endpoint));
        relationships.model_providers[model]?.forEach(provider => validProviders.add(provider));
      });
      
      availableEndpoints = new Set<string>(Array.from(availableEndpoints).filter(endpoint => validEndpoints.has(endpoint)));
      availableProviders = new Set<string>(Array.from(availableProviders).filter(provider => validProviders.has(provider)));
    }

    return {
      availableModels: Array.from(availableModels).sort(),
      availableEndpoints: Array.from(availableEndpoints).sort(),
      availableProviders: Array.from(availableProviders).sort()
    };
  };

  const { availableModels, availableEndpoints, availableProviders } = getFilteredOptions();

  // Handle multi-select changes
  const handleEndpointsChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedOption = event.target.value;
    const newEndpoints = selectedEndpoints.includes(selectedOption)
      ? selectedEndpoints.filter(item => item !== selectedOption)
      : [...selectedEndpoints, selectedOption];
    
    setSelectedEndpoints(newEndpoints);
    onFiltersChange({
      ...filters,
      endpoints: newEndpoints
    });
  };

  const handleProvidersChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedOption = event.target.value;
    const newProviders = selectedProviders.includes(selectedOption)
      ? selectedProviders.filter(item => item !== selectedOption)
      : [...selectedProviders, selectedOption];
    
    setSelectedProviders(newProviders);
    onFiltersChange({
      ...filters,
      providers: newProviders
    });
  };

  const handleModelsChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedOption = event.target.value;
    const newModels = selectedModels.includes(selectedOption)
      ? selectedModels.filter(item => item !== selectedOption)
      : [...selectedModels, selectedOption];
    
    setSelectedModels(newModels);
    onFiltersChange({
      ...filters,
      models: newModels
    });
  };

  const handleReset = React.useCallback(() => {
    setSelectedModels([]);
    setSelectedEndpoints([]);
    setSelectedProviders([]);
    onFiltersChange({
      ...filters,
      models: [],
      endpoints: [],
      providers: []
    });
  }, [filters, onFiltersChange]);

  if (isLoading) {
    return (
      <div className="bg-white p-4 rounded-lg shadow-sm space-y-4">
        <div className="flex flex-wrap gap-4">
          {/* Time Period Skeleton */}
          <div className="flex-1 min-w-[200px]">
            <div className="h-5 w-24 bg-gradient-to-r from-primary-100 to-purple-100 rounded animate-pulse mb-2"></div>
            <div className="h-6 w-32 bg-gradient-to-r from-primary-50 to-purple-50 rounded animate-pulse"></div>
          </div>

          {/* Endpoints Skeleton */}
          <div className="flex-1 min-w-[200px]">
            <div className="h-5 w-24 bg-gradient-to-r from-primary-100 to-purple-100 rounded animate-pulse mb-2"></div>
            <div className="h-[144px] bg-gradient-to-r from-primary-50 to-purple-50 rounded animate-pulse"></div>
          </div>

          {/* Providers Skeleton */}
          <div className="flex-1 min-w-[200px]">
            <div className="h-5 w-24 bg-gradient-to-r from-primary-100 to-purple-100 rounded animate-pulse mb-2"></div>
            <div className="h-[144px] bg-gradient-to-r from-primary-50 to-purple-50 rounded animate-pulse"></div>
          </div>

          {/* Models Skeleton */}
          <div className="flex-1 min-w-[200px]">
            <div className="h-5 w-24 bg-gradient-to-r from-primary-100 to-purple-100 rounded animate-pulse mb-2"></div>
            <div className="h-[144px] bg-gradient-to-r from-primary-50 to-purple-50 rounded animate-pulse"></div>
          </div>
        </div>
      </div>
    );
  }

  // Check if any filters are active
  const hasActiveFilters = selectedModels.length > 0 || selectedEndpoints.length > 0 || selectedProviders.length > 0;

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm space-y-4">
      <div className="flex flex-wrap gap-4">
        {/* Time Period Label */}
        <div className="flex-1 min-w-[200px]">
          <label className="block text-sm font-medium text-gray-700 mb-1">Time Period</label>
          <div className="text-sm text-gray-600">Last 12 Months</div>
        </div>

        {/* Endpoint Filter */}
        <div className="flex-1 min-w-[200px]">
          <label className="block text-sm font-medium text-gray-700 mb-1">Endpoints</label>
          <select
            className="w-full rounded-md border border-gray-300 shadow-sm px-3 py-2 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            multiple
            value={selectedEndpoints}
            onChange={handleEndpointsChange}
            onClick={(e) => e.stopPropagation()}
            size={4}
            aria-label="Select endpoints"
          >
            {availableEndpoints.map((endpoint: string) => (
              <option 
                key={endpoint} 
                value={endpoint}
                className={`p-2 ${
                  selectedEndpoints.includes(endpoint)
                    ? 'bg-gradient-to-r from-primary-600 to-purple-600 text-white'
                    : 'hover:bg-primary-50'
                }`}
              >
                {endpoint}
              </option>
            ))}
          </select>
        </div>

        {/* Provider Filter */}
        <div className="flex-1 min-w-[200px]">
          <label className="block text-sm font-medium text-gray-700 mb-1">Providers</label>
          <select
            className="w-full rounded-md border border-gray-300 shadow-sm px-3 py-2 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            multiple
            value={selectedProviders}
            onChange={handleProvidersChange}
            onClick={(e) => e.stopPropagation()}
            size={4}
            aria-label="Select providers"
          >
            {availableProviders.map((provider: string) => (
              <option 
                key={provider} 
                value={provider}
                className={`p-2 ${
                  selectedProviders.includes(provider)
                    ? 'bg-gradient-to-r from-primary-600 to-purple-600 text-white'
                    : 'hover:bg-primary-50'
                }`}
              >
                {provider}
              </option>
            ))}
          </select>
        </div>

        {/* Model Filter */}
        <div className="flex-1 min-w-[200px]">
          <label className="block text-sm font-medium text-gray-700 mb-1">Models</label>
          <select
            className="w-full rounded-md border border-gray-300 shadow-sm px-3 py-2 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            multiple
            value={selectedModels}
            onChange={handleModelsChange}
            onClick={(e) => e.stopPropagation()}
            size={4}
            aria-label="Select models"
          >
            {availableModels.map((model: string) => (
              <option 
                key={model} 
                value={model}
                className={`p-2 ${
                  selectedModels.includes(model)
                    ? 'bg-gradient-to-r from-primary-600 to-purple-600 text-white'
                    : 'hover:bg-primary-50'
                }`}
              >
                {model}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Active Filters Display */}
      {hasActiveFilters && (
        <div className="mt-4 space-y-2">
          <div className="text-sm font-medium text-gray-700">Active Filters:</div>
          <div className="flex flex-wrap gap-2">
            {selectedEndpoints.map(endpoint => (
              <span
                key={`endpoint-${endpoint}`}
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
              >
                <span className="mr-1">Endpoint: {endpoint}</span>
                <button
                  onClick={() => removeEndpoint(endpoint)}
                  className="ml-0.5 inline-flex items-center justify-center h-4 w-4 rounded-full hover:bg-green-200 focus:outline-none"
                  aria-label={`Remove ${endpoint} filter`}
                >
                  <span className="sr-only">Remove {endpoint} filter</span>
                  ×
                </button>
              </span>
            ))}
            {selectedProviders.map(provider => (
              <span
                key={`provider-${provider}`}
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800"
              >
                <span className="mr-1">Provider: {provider}</span>
                <button
                  onClick={() => removeProvider(provider)}
                  className="ml-0.5 inline-flex items-center justify-center h-4 w-4 rounded-full hover:bg-purple-200 focus:outline-none"
                  aria-label={`Remove ${provider} filter`}
                >
                  <span className="sr-only">Remove {provider} filter</span>
                  ×
                </button>
              </span>
            ))}
            {selectedModels.map(model => (
              <span
                key={`model-${model}`}
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
              >
                <span className="mr-1">Model: {model}</span>
                <button
                  onClick={() => removeModel(model)}
                  className="ml-0.5 inline-flex items-center justify-center h-4 w-4 rounded-full hover:bg-blue-200 focus:outline-none"
                  aria-label={`Remove ${model} filter`}
                >
                  <span className="sr-only">Remove {model} filter</span>
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Reset Button */}
      <button
        className="text-sm text-gray-600 hover:text-gray-900"
        onClick={handleReset}
      >
        Reset Filters
      </button>
    </div>
  );
}; 