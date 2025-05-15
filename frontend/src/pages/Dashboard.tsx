import { useState } from 'react';
import OverviewCard from '../components/dashboard/OverviewCard';
import TokenUsageChart from '../components/dashboard/TokenUsageChart';
import ModelDistributionChart from '../components/dashboard/ModelDistributionChart';
import FeatureUsageTable from '../components/dashboard/FeatureUsageTable';

const Dashboard = () => {
  const [metric, setMetric] = useState<'tokens' | 'cost'>('tokens');

  const toggleMetric = () => {
    setMetric(metric === 'tokens' ? 'cost' : 'tokens');
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      
      {/* Overview Card */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Overview</h2>
          <button 
            className="btn btn-outline text-xs"
            onClick={toggleMetric}
          >
            Show {metric === 'tokens' ? 'Cost' : 'Tokens'}
          </button>
        </div>
        <OverviewCard metric={metric} />
      </div>
      
      {/* Token Usage Over Time Chart */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Usage Over Time</h2>
          <div className="flex items-center gap-2">
            <select className="text-sm border border-gray-200 rounded-md px-2 py-1">
              <option value="day">Daily</option>
              <option value="week">Weekly</option>
              <option value="month">Monthly</option>
            </select>
          </div>
        </div>
        <TokenUsageChart metric={metric} />
      </div>
      
      {/* Model Distribution Chart */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Model Distribution</h2>
          <ModelDistributionChart metric={metric} />
        </div>
        
        {/* Feature Usage Table */}
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Feature Usage</h2>
          <FeatureUsageTable metric={metric} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 