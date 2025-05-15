import { useState, useEffect } from 'react';
import { fetchFeatureUsage } from '../../api/analytics';
import type { FeatureUsageData } from '../../api/analytics';

interface FeatureUsageTableProps {
  metric: 'tokens' | 'cost';
}

const FeatureUsageTable = ({ metric }: FeatureUsageTableProps) => {
  const [data, setData] = useState<FeatureUsageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const featureData = await fetchFeatureUsage(undefined, undefined, metric);
        setData(featureData);
        setError(null);
      } catch (err) {
        console.error('Error fetching feature usage data:', err);
        setError('Failed to load feature data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [metric]);

  if (loading) {
    return (
      <div className="animate-pulse space-y-3">
        <div className="h-8 bg-gray-100 rounded-md w-full"></div>
        <div className="h-8 bg-gray-100 rounded-md w-full"></div>
        <div className="h-8 bg-gray-100 rounded-md w-full"></div>
        <div className="h-8 bg-gray-100 rounded-md w-full"></div>
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

  if (data.data.length === 0) {
    return (
      <div className="text-center py-6 text-gray-500">
        No feature usage data available
      </div>
    );
  }

  // Format number for display
  const formatNumber = (num: number): string => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  // Format cost for display
  const formatCost = (cost: number): string => {
    return `$${cost.toFixed(2)}`;
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead>
          <tr>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Feature
            </th>
            <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              {metric === 'tokens' ? 'Tokens' : 'Cost'}
            </th>
            <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Requests
            </th>
            <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Latency
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {data.data.map((feature) => (
            <tr key={feature.feature} className="hover:bg-gray-50">
              <td className="px-4 py-2 text-sm text-primary-text whitespace-nowrap">
                {feature.feature}
              </td>
              <td className="px-4 py-2 text-sm text-right text-primary-text whitespace-nowrap">
                {metric === 'tokens' 
                  ? formatNumber(feature.total_tokens) 
                  : formatCost(feature.total_cost)}
                <span className="ml-1 text-xs text-gray-500">
                  ({feature.percent}%)
                </span>
              </td>
              <td className="px-4 py-2 text-sm text-right text-primary-text whitespace-nowrap">
                {feature.request_count}
              </td>
              <td className="px-4 py-2 text-sm text-right text-primary-text whitespace-nowrap">
                {feature.avg_latency_ms} ms
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default FeatureUsageTable; 