import { useState, useEffect } from 'react';
import OverviewCard from '../components/dashboard/OverviewCard';
import TokenUsageChart from '../components/dashboard/TokenUsageChart';
import ModelDistributionChart from '../components/dashboard/ModelDistributionChart';
import FeatureUsageTable from '../components/dashboard/FeatureUsageTable';
import FilterBar from '../components/FilterBar';
import { useFilters } from '../contexts/FilterContext';

const Dashboard = () => {
  const [metric, setMetric] = useState<'tokens' | 'cost'>('tokens');
  const { filters } = useFilters();

  const toggleMetric = () => {
    setMetric(metric === 'tokens' ? 'cost' : 'tokens');
  };

  // Register event listener for filter changes
  useEffect(() => {
    const handleFilterChange = () => {
      // This is a lightweight effect to avoid modifying existing chart code
      // As per instructions, charts will listen to the custom event directly
      console.log('Filter changed event detected');
    };

    window.addEventListener('filter-changed', handleFilterChange);

    return () => {
      window.removeEventListener('filter-changed', handleFilterChange);
    };
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold mb-2">Dashboard</h1>
      
      {/* Global Filter Bar */}
      <FilterBar />
      
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
        </div>
        <TokenUsageChart metric={metric} interval={filters.interval} />
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