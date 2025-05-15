import { useState, useEffect } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { fetchTimeSeries } from '../../api/analytics';
import type { TimeSeriesData } from '../../api/analytics';

interface TokenUsageChartProps {
  metric: 'tokens' | 'cost';
}

const TokenUsageChart = ({ metric }: TokenUsageChartProps) => {
  const [data, setData] = useState<TimeSeriesData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [interval] = useState<'day' | 'week' | 'month'>('day');

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const timeseriesData = await fetchTimeSeries(undefined, undefined, interval, metric);
        setData(timeseriesData);
        setError(null);
      } catch (err) {
        console.error('Error fetching time series data:', err);
        setError('Failed to load usage data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [interval, metric]);

  // Format the date for the chart tooltip
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short', 
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="animate-pulse h-64 bg-gray-100 rounded-md"></div>
    );
  }

  if (error || !data) {
    return (
      <div className="text-center py-6 text-red-500">
        <p>{error || 'No data available'}</p>
      </div>
    );
  }

  // Filter out days with no data to make the chart more meaningful
  const filteredData = data.data.filter(item => item.value > 0);

  // Format for tooltip display
  const formatValue = (value: number): string => {
    if (metric === 'tokens') {
      return value >= 1000 ? `${(value / 1000).toFixed(1)}K` : value.toString();
    } else {
      return `$${value.toFixed(2)}`;
    }
  };

  return (
    <div className="h-72">
      {filteredData.length === 0 ? (
        <div className="h-full flex items-center justify-center text-gray-500">
          No {metric} usage data available for this time period
        </div>
      ) : (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={filteredData}
            margin={{ top: 10, right: 30, left: 0, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
            <XAxis 
              dataKey="date" 
              tickFormatter={formatDate}
              tick={{ fontSize: 12 }}
              tickMargin={10}
            />
            <YAxis 
              tickFormatter={formatValue}
              tick={{ fontSize: 12 }}
              width={40}
            />
            <Tooltip 
              formatter={(value: number) => [formatValue(value), metric === 'tokens' ? 'Tokens' : 'Cost']}
              labelFormatter={formatDate}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="value"
              name={metric === 'tokens' ? 'Total Tokens' : 'Total Cost'}
              stroke="#6366F1"
              activeDot={{ r: 8 }}
              strokeWidth={2}
            />
            {metric === 'tokens' && (
              <>
                <Line
                  type="monotone"
                  dataKey="prompt_tokens"
                  name="Prompt Tokens"
                  stroke="#818CF8"
                  strokeWidth={1.5}
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="completion_tokens"
                  name="Completion Tokens"
                  stroke="#A5B4FC"
                  strokeWidth={1.5}
                  dot={false}
                />
              </>
            )}
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
};

export default TokenUsageChart; 