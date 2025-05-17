import { useState, useEffect } from 'react';
import { fetchFeatureUsage } from '../../api/analytics';
import { useFilters } from '../../contexts/FilterContext';
import type { FeatureUsageData, FeatureData } from '../../api/analytics';

interface FeatureUsageTableProps {
  metric: 'tokens' | 'cost';
}

const FeatureUsageTable = ({ metric }: FeatureUsageTableProps) => {
  const [data, setData] = useState<FeatureUsageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { filters } = useFilters();

  // Format date for API request
  const formatDateParam = (date: Date) => date.toISOString().split('T')[0];

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        
        // Use all filters including interval
        const fromParam = formatDateParam(filters.from);
        const toParam = formatDateParam(filters.to);
        
        const featuresData = await fetchFeatureUsage(
          fromParam, 
          toParam, 
          metric,
          10, // limit
          filters.model,
          filters.task,
          filters.interval
        );
        
        setData(featuresData);
        setError(null);
      } catch (err) {
        console.error('Error fetching feature usage:', err);
        setError('Failed to load feature data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [metric, filters.from, filters.to, filters.model, filters.task, filters.interval]);

  // Also listen for filter-changed events
  useEffect(() => {
    const handleFilterChange = () => {
      console.log('Filter change event detected in FeatureUsageTable');
    };

    window.addEventListener('filter-changed', handleFilterChange);
    return () => {
      window.removeEventListener('filter-changed', handleFilterChange);
    };
  }, []);

  // Format values for display
  const formatValue = (value: number | undefined): string => {
    if (value === undefined || value === null) {
      return metric === 'tokens' ? '0' : '$0.00';
    }
    
    if (metric === 'tokens') {
      return value >= 1000000 
        ? `${(value / 1000000).toFixed(1)}M` 
        : value >= 1000 
        ? `${(value / 1000).toFixed(1)}K` 
        : value.toString();
    } else {
      return `$${value.toFixed(2)}`;
    }
  };

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-8 bg-gray-100 rounded mb-4"></div>
        <div className="h-8 bg-gray-100 rounded mb-4"></div>
        <div className="h-8 bg-gray-100 rounded mb-4"></div>
        <div className="h-8 bg-gray-100 rounded"></div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="text-center py-6 text-red-500">
        <p>{error || 'No data available'}</p>
      </div>
    );
  }

  // Ensure data.data is an array before using it
  const features = Array.isArray(data.data) ? data.data : [];

  // Apply task filter if needed
  const taskFilterApplied = filters.task !== '*';
  const filteredFeatures = taskFilterApplied
    ? features.filter(item => item && item.feature === filters.task)
    : features;

  if (filteredFeatures.length === 0) {
    return (
      <div className="text-center py-6 text-gray-500">
        No feature usage data available for the current filters
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="text-left text-gray-500 border-b">
            <th className="pb-2">Feature</th>
            <th className="pb-2 text-right">{metric === 'tokens' ? 'Tokens' : 'Cost'}</th>
            <th className="pb-2 text-right">%</th>
          </tr>
        </thead>
        <tbody>
          {filteredFeatures.map((feature: FeatureData) => (
            <tr 
              key={feature.feature} 
              className="hover:bg-gray-50 border-b border-gray-100"
            >
              <td className="py-2">
                <span className="truncate block max-w-[180px]" title={feature.feature}>
                  {feature.feature}
                </span>
              </td>
              <td className="py-2 text-right">
                {formatValue(metric === 'tokens' ? feature.total_tokens : feature.total_cost)}
              </td>
              <td className="py-2 text-right">{feature.percent ?? 0}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default FeatureUsageTable; 