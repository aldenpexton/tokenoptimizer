import React from 'react';
import { Card } from '../components/ui/Card';

const Logs: React.FC = () => {
  const logs = [
    {
      id: 1,
      timestamp: '2024-03-20 14:23:45',
      model: 'GPT-4',
      tokens: 150,
      cost: 0.03,
      type: 'Completion'
    },
    {
      id: 2,
      timestamp: '2024-03-20 14:23:44',
      model: 'GPT-4',
      tokens: 50,
      cost: 0.01,
      type: 'Prompt'
    },
    // Add more sample logs as needed
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-600 to-purple-600">
          LLM API Logs
        </h1>
        <p className="mt-2 text-lg text-primary-600">
          Real-time token usage and cost tracking
        </p>
      </div>

      {/* Logs Table */}
      <Card className="overflow-hidden bg-white/80 backdrop-blur-sm border border-primary-100/20 shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-primary-100">
                <th className="px-6 py-4 text-left text-sm font-semibold text-primary-900">Timestamp</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-primary-900">Model</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-primary-900">Type</th>
                <th className="px-6 py-4 text-right text-sm font-semibold text-primary-900">Tokens</th>
                <th className="px-6 py-4 text-right text-sm font-semibold text-primary-900">Cost</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-primary-100">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-primary-50/50 transition-colors">
                  <td className="px-6 py-4 text-sm text-primary-700">{log.timestamp}</td>
                  <td className="px-6 py-4 text-sm text-primary-700">{log.model}</td>
                  <td className="px-6 py-4 text-sm text-primary-700">{log.type}</td>
                  <td className="px-6 py-4 text-sm text-primary-700 text-right">{log.tokens.toLocaleString()}</td>
                  <td className="px-6 py-4 text-sm text-primary-700 text-right">${log.cost.toFixed(3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

export default Logs; 