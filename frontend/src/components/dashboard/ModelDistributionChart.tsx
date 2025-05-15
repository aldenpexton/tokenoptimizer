import { useState, useEffect } from 'react';
import { 
  PieChart, Pie, Cell, ResponsiveContainer, 
  Legend, Tooltip, Sector
} from 'recharts';
import { fetchModelDistribution } from '../../api/analytics';
import type { ModelDistributionData, ModelData } from '../../api/analytics';

interface ModelDistributionChartProps {
  metric: 'tokens' | 'cost';
}

// Colors for the pie chart segments - using accessible palette
const COLORS = ['#6366F1', '#8B5CF6', '#EC4899', '#F97316', '#EAB308', '#10B981', '#0EA5E9', '#6B7280'];

// Custom active shape for the pie chart
const renderActiveShape = (props: any) => {
  const { 
    cx, cy, innerRadius, outerRadius, startAngle, endAngle,
    fill, payload, percent, value 
  } = props;

  return (
    <g>
      <Sector
        cx={cx}
        cy={cy}
        innerRadius={innerRadius}
        outerRadius={outerRadius + 6}
        startAngle={startAngle}
        endAngle={endAngle}
        fill={fill}
      />
      <text x={cx} y={cy} dy={-20} textAnchor="middle" fill="#333" className="text-sm">
        {payload.model}
      </text>
      <text x={cx} y={cy} dy={8} textAnchor="middle" fill="#333" fontWeight="bold" className="text-lg">
        {payload.percent}%
      </text>
    </g>
  );
};

const ModelDistributionChart = ({ metric }: ModelDistributionChartProps) => {
  const [data, setData] = useState<ModelDistributionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const modelData = await fetchModelDistribution(undefined, undefined, metric);
        setData(modelData);
        setError(null);
      } catch (err) {
        console.error('Error fetching model distribution data:', err);
        setError('Failed to load model data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [metric]);

  const onPieEnter = (_: any, index: number) => {
    setActiveIndex(index);
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

  // Prepare data for the chart
  const chartData = [...data.data];
  
  // Add "Other" category if it has value
  if (data.other && data.other.value > 0) {
    chartData.push({
      model: 'Other',
      value: data.other.value,
      percent: data.other.percent,
      cost: data.other.cost
    });
  }

  // Check if there's any data to display
  if (chartData.length === 0) {
    return (
      <div className="h-60 flex items-center justify-center text-gray-500">
        No model usage data available
      </div>
    );
  }

  // Format for tooltip
  const formatValue = (value: number): string => {
    if (metric === 'tokens') {
      return value >= 1000000
        ? `${(value / 1000000).toFixed(1)}M tokens`
        : value >= 1000
        ? `${(value / 1000).toFixed(1)}K tokens`
        : `${value} tokens`;
    } else {
      return `$${value.toFixed(2)}`;
    }
  };

  return (
    <div className="h-60">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            activeIndex={activeIndex}
            activeShape={renderActiveShape}
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            dataKey="value"
            onMouseEnter={onPieEnter}
            paddingAngle={2}
            nameKey="model"
            valueKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={COLORS[index % COLORS.length]} 
              />
            ))}
          </Pie>
          <Tooltip 
            formatter={(value: number) => formatValue(value)}
          />
          <Legend
            layout="vertical"
            align="right"
            verticalAlign="middle"
            formatter={(value) => {
              const item = chartData.find(i => i.model === value);
              return <span className="text-xs">{value} ({item?.percent}%)</span>;
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ModelDistributionChart; 