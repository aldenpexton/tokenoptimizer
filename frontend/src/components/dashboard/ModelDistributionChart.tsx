import { useState, useEffect } from 'react';
import { 
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import { fetchModelDistribution } from '../../api/analytics';
import { useFilters } from '../../contexts/FilterContext';
import type { ModelDistributionData } from '../../api/analytics';

interface ModelDistributionChartProps {
  metric: 'tokens' | 'cost';
}

// Color palette for chart
const COLORS = ['#6366F1', '#818CF8', '#A5B4FC', '#C7D2FE', '#DDD6FE', '#EDE9FE', '#F5F3FF'];

const ModelDistributionChart = ({ metric }: ModelDistributionChartProps) => {
  const [data, setData] = useState<ModelDistributionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { filters } = useFilters();

  // Format date for API request
  const formatDateParam = (date: Date) => date.toISOString().split('T')[0];

  // Function to load data, can be called on filter changes or initial load
  const loadData = async () => {
    try {
      setLoading(true);
      
      // Apply all filters including interval
      const fromParam = formatDateParam(filters.from);
      const toParam = formatDateParam(filters.to);
      
      const modelsData = await fetchModelDistribution(
        fromParam,
        toParam,
        metric,
        10, // limit
        filters.model,
        filters.task,
        filters.interval
      );
      
      setData(modelsData);
      setError(null);
    } catch (err) {
      console.error('Error fetching model distribution:', err);
      setError('Failed to load model data');
    } finally {
      setLoading(false);
    }
  };

  // Initial data load and reload on filter changes
  useEffect(() => {
    loadData();
  }, [metric, filters.from, filters.to, filters.model, filters.task, filters.interval]);

  // Also listen for filter-changed events
  useEffect(() => {
    const handleFilterChange = (event: Event) => {
      console.log('Filter change event detected in ModelDistributionChart');
    };

    window.addEventListener('filter-changed', handleFilterChange);
    return () => {
      window.removeEventListener('filter-changed', handleFilterChange);
    };
  }, []);

  // Custom tooltip formatter
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-2 border border-gray-200 rounded shadow-sm text-xs">
          <p className="font-semibold">{data.model}</p>
          <p>{metric === 'tokens' ? 'Tokens:' : 'Cost:'} {formatValue(data.value)}</p>
          <p>Percent: {data.percent}%</p>
        </div>
      );
    }
    return null;
  };

  // Custom legend formatter to truncate long model names
  const renderLegendText = (value: string) => {
    if (value.length > 20) {
      return value.substring(0, 17) + '...';
    }
    return value;
  };

  // Format value based on metric
  const formatValue = (value: number): string => {
    if (metric === 'tokens') {
      return value >= 1000 ? `${(value / 1000).toFixed(1)}K` : value.toString();
    } else {
      return `$${value.toFixed(2)}`;
    }
  };

  // Format percentage for display
  const formatPercent = (percent: number): string => {
    // Assumes percent is already in the range 0-100
    return `${Math.round(percent)}%`;
  };

  if (loading) {
    return (
      <div className="animate-pulse h-60 bg-gray-100 rounded-md"></div>
    );
  }

  if (error || !data) {
    return (
      <div className="text-center py-6 text-red-500">
        <p>{error || 'No data available'}</p>
      </div>
    );
  }

  // Prepare chart data, combining smaller values into "Other"
  const chartData = [
    ...data.data,
    ...(data.other && data.other.value > 0 ? [{
      model: 'Other',
      value: data.other.value,
      percent: data.other.percent,
      cost: data.other.cost
    }] : [])
  ];

  // If we apply model filter, only show that model
  const modelFilterApplied = filters.model !== '*';
  const filteredChartData = modelFilterApplied 
    ? chartData.filter(item => item.model === filters.model)
    : chartData;

  if (filteredChartData.length === 0) {
    return (
      <div className="h-60 flex items-center justify-center text-gray-500">
        No model distribution data available for the current filters
      </div>
    );
  }

  return (
    <div className="h-60">
      {chartData.length === 0 ? (
        <div className="h-full flex items-center justify-center text-gray-500">
          No model distribution data available
        </div>
      ) : (
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              dataKey="value"
              nameKey="model"
              cx="50%"
              cy="50%"
              outerRadius={80}
              fill="#8884d8"
              label={false}
              labelLine={false}
            >
              {chartData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              formatter={(value, entry) => {
                // Get the entry data from the chartData
                const item = chartData.find(d => d.model === value);
                // Format the model name (truncate if too long)
                const displayName = value.length > 15 ? `${value.substring(0, 12)}...` : value;
                return `${displayName} (${item ? formatPercent(item.percent) : '0%'})`;
              }}
              layout="vertical" 
              verticalAlign="middle" 
              align="right"
              wrapperStyle={{ 
                fontSize: '12px',
                maxWidth: '140px',
                paddingLeft: '10px'
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      )}
    </div>
  );
};

export default ModelDistributionChart; 