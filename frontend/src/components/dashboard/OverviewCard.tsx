import { useState, useEffect } from 'react';
import { fetchSummary } from '../../api/analytics';
import type { SummaryData } from '../../api/analytics';

interface OverviewCardProps {
  metric: 'tokens' | 'cost';
}

const OverviewCard = ({ metric }: OverviewCardProps) => {
  const [data, setData] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const summary = await fetchSummary();
        setData(summary);
        setError(null);
      } catch (err) {
        console.error('Error fetching summary data:', err);
        setError('Failed to load overview data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) {
    return (
      <div className="animate-pulse grid grid-cols-1 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-24 bg-gray-100 rounded-md"></div>
        ))}
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

  // Format numbers for display
  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  // Format cost for display
  const formatCost = (cost: number) => {
    return `$${cost.toFixed(2)}`;
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
      {/* Total Usage */}
      <div className="bg-gray-50 p-4 rounded-md">
        <h3 className="text-sm font-medium text-gray-500 mb-1">
          {metric === 'tokens' ? 'Total Tokens' : 'Total Cost'}
        </h3>
        <p className="text-2xl font-bold">
          {metric === 'tokens' ? formatNumber(data.total_tokens) : formatCost(data.total_cost)}
        </p>
        <div className="mt-1 text-xs text-gray-500">
          {data.time_period.days} days
        </div>
      </div>

      {/* Token Breakdown */}
      <div className="bg-gray-50 p-4 rounded-md">
        <h3 className="text-sm font-medium text-gray-500 mb-1">
          {metric === 'tokens' ? 'Prompt/Completion' : 'Input/Output Cost'}
        </h3>
        <div className="flex items-center gap-2">
          <span className="text-lg font-semibold">
            {metric === 'tokens' 
              ? formatNumber(data.prompt_tokens) 
              : formatCost(data.total_cost * 0.4) /* Estimate input cost */}
          </span>
          <span className="text-gray-400">/</span>
          <span className="text-lg font-semibold">
            {metric === 'tokens' 
              ? formatNumber(data.completion_tokens) 
              : formatCost(data.total_cost * 0.6) /* Estimate output cost */}
          </span>
        </div>
        <div className="mt-1 text-xs text-gray-500">
          {metric === 'tokens' ? 'prompt / completion' : 'input / output'}
        </div>
      </div>

      {/* Top Model */}
      <div className="bg-gray-50 p-4 rounded-md">
        <h3 className="text-sm font-medium text-gray-500 mb-1">Top Model</h3>
        <p className="text-xl font-semibold truncate">{data.top_model.name}</p>
        <div className="mt-1 text-xs text-gray-500">
          {data.top_model.usage_percent}% of usage
        </div>
      </div>

      {/* Average Latency */}
      <div className="bg-gray-50 p-4 rounded-md">
        <h3 className="text-sm font-medium text-gray-500 mb-1">Avg Latency</h3>
        <p className="text-2xl font-bold">{data.avg_latency_ms}ms</p>
        <div className="mt-1 text-xs text-gray-500">
          response time
        </div>
      </div>
    </div>
  );
};

export default OverviewCard; 