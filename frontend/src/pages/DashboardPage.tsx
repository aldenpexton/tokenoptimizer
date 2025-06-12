import React, { useState } from 'react';
import { useMetricsSummary, useMetricsTrend } from '../api/queries';
import { formatCurrency, formatNumber } from '../components/charts/ChartDefaults';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { FilterBar } from '../components/FilterBar';
import { FilterParams, RecommendationsResponse } from '../types/api';
import { useQuery } from '@tanstack/react-query';
import { fetchJson } from '../api/queries';

// Add this at the top with other hooks
const useRecommendations = (filters?: FilterParams) => {
  return useQuery<RecommendationsResponse>({
    queryKey: ['recommendations', filters],
    queryFn: () => fetchJson('/api/recommendations', filters),
  });
};

const DashboardPage: React.FC = () => {
  // Global filters state including date range
  const [filters, setFilters] = React.useState<FilterParams>(() => {
    const end = new Date();
    const start = new Date();
    start.setMonth(start.getMonth() - 12);
    
    return {
      models: [],
      endpoints: [],
      providers: [],
      start_date: start.toISOString(),
      end_date: end.toISOString()
    };
  });
  const [showSpend, setShowSpend] = useState(false);

  // Fetch data using React Query with filters
  const { data: summary, isLoading: summaryLoading } = useMetricsSummary(filters);
  const { data: trend, isLoading: trendLoading } = useMetricsTrend(filters);
  const { data: recommendations, isLoading: recommendationsLoading } = useRecommendations(filters);

  if (summaryLoading || trendLoading || recommendationsLoading) {
    return (
      <div className="p-6 space-y-6">
        {/* Filter Bar Loading State - match the height of FilterBar */}
        <div className="bg-white p-4 rounded-lg shadow-sm">
          <div className="flex flex-wrap gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="flex-1 min-w-[200px]">
                <div className="h-5 w-24 bg-gradient-to-r from-primary-100 to-purple-100 rounded animate-pulse mb-2"></div>
                <div className="h-[144px] bg-gradient-to-r from-primary-50 to-purple-50 rounded animate-pulse"></div>
              </div>
            ))}
          </div>
        </div>

        {/* Summary Cards Loading State */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-lg shadow-stripe-sm p-6">
              <div className="h-5 w-32 bg-gradient-to-r from-primary-100 to-purple-100 rounded animate-pulse mb-3"></div>
              <div className="h-8 w-40 bg-gradient-to-r from-primary-50 to-purple-50 rounded animate-pulse"></div>
            </div>
          ))}
        </div>

        {/* Chart Loading State */}
        <div className="bg-white rounded-lg shadow-stripe-sm p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="h-8 w-48 bg-gradient-to-r from-primary-100 to-purple-100 rounded animate-pulse"></div>
            <div className="flex items-center space-x-2">
              <div className="h-8 w-20 bg-gradient-to-r from-primary-50 to-purple-50 rounded animate-pulse"></div>
              <div className="h-8 w-20 bg-gradient-to-r from-primary-50 to-purple-50 rounded animate-pulse"></div>
            </div>
          </div>
          <div className="h-[400px] bg-gradient-to-r from-primary-50 to-purple-50 rounded animate-pulse"></div>
        </div>

        {/* Breakdowns Loading State */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-lg shadow-stripe-sm p-6">
              <div className="h-5 w-32 bg-gradient-to-r from-primary-100 to-purple-100 rounded animate-pulse mb-4"></div>
              <div className="space-y-4">
                {[1, 2, 3, 4].map((j) => (
                  <div key={j} className="flex justify-between items-center">
                    <div className="h-4 w-24 bg-gradient-to-r from-primary-50 to-purple-50 rounded animate-pulse"></div>
                    <div className="h-4 w-16 bg-gradient-to-r from-primary-50 to-purple-50 rounded animate-pulse"></div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const totalPotentialSavings = recommendations?.total_potential_savings || 0;

  return (
    <div className="p-6 space-y-6">
      {/* Global Filters */}
      <FilterBar filters={filters} onFiltersChange={setFilters} />

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-stripe-sm p-6">
          <h3 className="text-sm font-medium text-primary-600">Total Spend</h3>
          <p className="mt-2 text-3xl font-semibold text-primary-900">
            {formatCurrency(summary?.total_spend || 0)}
          </p>
        </div>
        
        <div className="bg-white rounded-lg shadow-stripe-sm p-6">
          <h3 className="text-sm font-medium text-primary-600">Total Requests</h3>
          <p className="mt-2 text-3xl font-semibold text-primary-900">
            {formatNumber(summary?.total_requests || 0)}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-stripe-sm p-6">
          <h3 className="text-sm font-medium text-primary-600">Avg Cost/Request</h3>
          <p className="mt-2 text-3xl font-semibold text-primary-900">
            {formatCurrency(summary?.avg_cost_per_request || 0)}
          </p>
        </div>
      </div>

      {/* Token Usage Chart */}
      <div className="bg-white rounded-lg shadow-stripe-sm p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">{showSpend ? 'Spend Over Time' : 'Token Usage'}</h2>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-primary-600">Show:</span>
            <button
              onClick={() => setShowSpend(false)}
              className={`px-3 py-1 text-sm font-medium rounded-l-md ${
                !showSpend
                  ? 'bg-primary-100 text-primary-800'
                  : 'bg-white text-primary-600 hover:bg-primary-50'
              }`}
            >
              Tokens
            </button>
            <button
              onClick={() => setShowSpend(true)}
              className={`px-3 py-1 text-sm font-medium rounded-r-md ${
                showSpend
                  ? 'bg-primary-100 text-primary-800'
                  : 'bg-white text-primary-600 hover:bg-primary-50'
              }`}
            >
              Spend
            </button>
          </div>
        </div>
        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart 
              data={trend?.metrics || []}
              margin={{ top: 20, right: 30, left: 40, bottom: 40 }}
            >
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis 
                dataKey="period_label" 
                tick={{ fill: '#000000', fontSize: 12 }}
                axisLine={{ stroke: '#E5E7EB' }}
                tickLine={false}
                interval={0}
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis 
                tick={{ fill: '#000000', fontSize: 12 }}
                axisLine={{ stroke: '#E5E7EB' }}
                tickLine={false}
                tickFormatter={(value) => 
                  showSpend 
                    ? formatCurrency(value)
                    : `${(value / 1000).toFixed(0)}K`
                }
                domain={[0, 'auto']}
                padding={{ top: 20 }}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #E5E7EB',
                  borderRadius: '4px',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                }}
                formatter={(value: any) => 
                  showSpend 
                    ? [formatCurrency(value), 'Spend']
                    : [`${(value / 1000).toFixed(1)}K tokens`, 'Usage']
                }
                labelFormatter={(label: string) => label}
              />
              <Bar 
                dataKey={showSpend ? "total_spend" : "total_tokens"}
                fill="#4F46E5"
                radius={[4, 4, 0, 0]}
                maxBarSize={50}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Breakdowns Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Provider Breakdown */}
        <div className="bg-white rounded-lg shadow-stripe-sm p-6">
          <h3 className="text-sm font-medium text-primary-600 mb-4">Provider Breakdown</h3>
          <div className="space-y-4">
            {Object.entries(summary?.provider_breakdown || {})
              .sort(([, a], [, b]) => (b as any).total_spend - (a as any).total_spend)
              .map(([provider, metrics]) => (
                <div key={provider} className="flex justify-between items-center">
                  <span className="text-primary-700">{provider}</span>
                  <span className="text-primary-900 font-medium">
                    {formatCurrency((metrics as any).total_spend)}
                  </span>
                </div>
              ))}
          </div>
        </div>

        {/* Model Breakdown */}
        <div className="bg-white rounded-lg shadow-stripe-sm p-6">
          <h3 className="text-sm font-medium text-primary-600 mb-4">Model Breakdown</h3>
          <div className="space-y-4">
            {Object.entries(summary?.model_breakdown || {})
              .sort(([, a], [, b]) => (b as any).total_spend - (a as any).total_spend)
              .map(([model, metrics]) => (
                <div key={model} className="flex justify-between items-center">
                  <span className="text-primary-700">{model}</span>
                  <span className="text-primary-900 font-medium">
                    {formatCurrency((metrics as any).total_spend)}
                  </span>
                </div>
              ))}
          </div>
        </div>

        {/* Endpoint Breakdown */}
        <div className="bg-white rounded-lg shadow-stripe-sm p-6">
          <h3 className="text-sm font-medium text-primary-600 mb-4">Endpoint Breakdown</h3>
          <div className="space-y-4">
            {Object.entries(summary?.endpoint_breakdown || {})
              .sort(([, a], [, b]) => (b as any).total_spend - (a as any).total_spend)
              .map(([endpoint, metrics]) => (
                <div key={endpoint} className="flex justify-between items-center">
                  <span className="text-primary-700">{endpoint}</span>
                  <span className="text-primary-900 font-medium">
                    {formatCurrency((metrics as any).total_spend)}
                  </span>
                </div>
              ))}
          </div>
        </div>
      </div>

      {/* Recommendations Section */}
      <div className="bg-white rounded-lg shadow-stripe-sm p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">Optimization Recommendations</h2>
          {totalPotentialSavings > 0 && (
            <div className="bg-green-50 text-green-700 px-4 py-2 rounded-lg">
              Potential Savings: {formatCurrency(totalPotentialSavings)}
            </div>
          )}
        </div>
        
        <div className="space-y-6">
          {recommendations?.recommendations.map((rec: any) => (
            <div key={`${rec.current_model}-${rec.recommended_model}`} className="border border-primary-100 rounded-lg p-4">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h4 className="font-medium text-primary-900">
                    Replace <span className="text-primary-600">{rec.current_model}</span> with{' '}
                    <span className="text-primary-600">{rec.recommended_model}</span>
                  </h4>
                  <p className="text-sm text-primary-600 mt-1">
                    {rec.usage_count} requests in the last 30 days
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-green-600 font-medium">
                    Save {formatCurrency(rec.potential_savings)}
                  </div>
                  <div className="text-sm text-primary-500 mt-1">
                    {(rec.similarity_score * 100).toFixed(1)}% Similar
                  </div>
                </div>
              </div>
              {rec.reason && (
                <p className="text-sm text-primary-600 bg-primary-50 rounded p-2 mt-2">
                  {rec.reason}
                </p>
              )}
            </div>
          ))}
          
          {(!recommendations?.recommendations || recommendations.recommendations.length === 0) && (
            <div className="text-center py-8 text-primary-600">
              No optimization recommendations at this time.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage; 