import React, { useState, useMemo } from 'react';
import { useLogs } from '../api/queries';
import { formatNumber, formatCurrency } from '../components/charts/ChartDefaults';

const LogsPage: React.FC = () => {
  const [page, setPage] = useState(1);
  const [perPage] = useState(50);

  // Memoize the date range to prevent re-renders
  const dateRange = useMemo(() => {
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 30);
    return {
      start_date: start.toISOString(),
      end_date: end.toISOString()
    };
  }, []); // Empty dependency array since this shouldn't change

  const { data, isLoading } = useLogs({
    page,
    per_page: perPage,
    ...dateRange
  });

  if (isLoading) {
    return (
      <div className="p-6 space-y-6">
        <div className="h-8 w-48 bg-gradient-to-r from-primary-100 to-purple-100 rounded animate-pulse mb-6"></div>
        
        {/* Table Loading State */}
        <div className="bg-white shadow-stripe-sm rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-primary-200">
              <thead className="bg-primary-50">
                <tr>
                  {['Timestamp', 'Model', 'Endpoint', 'Tokens', 'Cost', 'Provider'].map((header) => (
                    <th key={header} className="px-6 py-3 text-left">
                      <div className="h-4 w-20 bg-gradient-to-r from-primary-100 to-purple-100 rounded animate-pulse"></div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-primary-200">
                {[1, 2, 3, 4, 5].map((i) => (
                  <tr key={i}>
                    <td className="px-6 py-4">
                      <div className="h-4 w-32 bg-gradient-to-r from-primary-50 to-purple-50 rounded animate-pulse"></div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="h-4 w-24 bg-gradient-to-r from-primary-50 to-purple-50 rounded animate-pulse"></div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="h-4 w-28 bg-gradient-to-r from-primary-50 to-purple-50 rounded animate-pulse"></div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="h-4 w-16 bg-gradient-to-r from-primary-50 to-purple-50 rounded animate-pulse"></div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="h-4 w-16 bg-gradient-to-r from-primary-50 to-purple-50 rounded animate-pulse"></div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="h-4 w-20 bg-gradient-to-r from-primary-50 to-purple-50 rounded animate-pulse"></div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {/* Pagination Loading State */}
          <div className="px-6 py-4 flex items-center justify-between border-t border-primary-200">
            <div className="flex-1 flex justify-between items-center">
              <div className="h-4 w-48 bg-gradient-to-r from-primary-50 to-purple-50 rounded animate-pulse"></div>
              <div className="flex space-x-2">
                <div className="h-8 w-20 bg-gradient-to-r from-primary-50 to-purple-50 rounded animate-pulse"></div>
                <div className="h-8 w-20 bg-gradient-to-r from-primary-50 to-purple-50 rounded animate-pulse"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-semibold text-primary-900">Token Usage Logs</h1>
      
      {/* Table */}
      <div className="bg-white shadow-stripe-sm rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-primary-200">
            <thead className="bg-primary-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-primary-500 uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-primary-500 uppercase tracking-wider">
                  Model
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-primary-500 uppercase tracking-wider">
                  Endpoint
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-primary-500 uppercase tracking-wider">
                  Tokens
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-primary-500 uppercase tracking-wider">
                  Cost
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-primary-500 uppercase tracking-wider">
                  Provider
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-primary-200">
              {data?.logs.map((log) => (
                <tr key={log.id} className="hover:bg-primary-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-primary-900">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-primary-900">
                    {log.model}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-primary-900">
                    {log.endpoint_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-primary-900 text-right">
                    {formatNumber(log.total_tokens)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-primary-900 text-right">
                    {formatCurrency(log.total_cost)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-primary-900">
                    {log.api_provider}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {data && data.pagination && (
          <div className="px-6 py-4 flex items-center justify-between border-t border-primary-200">
            <div className="flex-1 flex justify-between items-center">
              <div>
                <p className="text-sm text-primary-700">
                  Showing {((page - 1) * perPage) + 1} to {Math.min(page * perPage, data.pagination.total_records)} of{' '}
                  {data.pagination.total_records} results
                </p>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setPage(page - 1)}
                  disabled={page === 1}
                  className={`px-4 py-2 text-sm font-medium rounded-md ${
                    page === 1
                      ? 'text-primary-400 bg-primary-50 cursor-not-allowed'
                      : 'text-primary-700 bg-primary-100 hover:bg-primary-200'
                  }`}
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage(page + 1)}
                  disabled={page >= data.pagination.total_pages}
                  className={`px-4 py-2 text-sm font-medium rounded-md ${
                    page >= data.pagination.total_pages
                      ? 'text-primary-400 bg-primary-50 cursor-not-allowed'
                      : 'text-primary-700 bg-primary-100 hover:bg-primary-200'
                  }`}
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LogsPage; 