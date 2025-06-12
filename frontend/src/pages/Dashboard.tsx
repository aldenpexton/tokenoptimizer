import React from 'react';
import { Card } from '../components/ui/Card';

const Dashboard: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-600 to-purple-600">
          LLM API Cost Dashboard
        </h1>
        <p className="mt-2 text-lg text-primary-600">
          Monitor and optimize your token usage in real-time
        </p>
      </div>

      {/* Dashboard Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Cost Overview Card */}
        <Card className="p-6 bg-white/80 backdrop-blur-sm border border-primary-100/20 shadow-sm hover:shadow-md transition-shadow">
          <h2 className="text-xl font-semibold text-primary-900 mb-4">Cost Overview</h2>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-primary-500">Total API Spend (30d)</p>
              <p className="text-2xl font-bold text-primary-700">$1,234.56</p>
            </div>
            <div>
              <p className="text-sm text-primary-500">Projected Monthly</p>
              <p className="text-lg font-semibold text-primary-600">$1,500.00</p>
            </div>
          </div>
        </Card>

        {/* Token Usage Card */}
        <Card className="p-6 bg-white/80 backdrop-blur-sm border border-primary-100/20 shadow-sm hover:shadow-md transition-shadow">
          <h2 className="text-xl font-semibold text-primary-900 mb-4">Token Usage</h2>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-primary-500">Total Tokens (30d)</p>
              <p className="text-2xl font-bold text-primary-700">2.5M</p>
            </div>
            <div>
              <p className="text-sm text-primary-500">Avg Cost per 1K tokens</p>
              <p className="text-lg font-semibold text-primary-600">$0.49</p>
            </div>
          </div>
        </Card>

        {/* Model Distribution Card */}
        <Card className="p-6 bg-white/80 backdrop-blur-sm border border-primary-100/20 shadow-sm hover:shadow-md transition-shadow">
          <h2 className="text-xl font-semibold text-primary-900 mb-4">Model Distribution</h2>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-primary-500">Most Used Model</p>
              <p className="text-lg font-semibold text-primary-600">GPT-4</p>
              <div className="w-full bg-primary-100 rounded-full h-2 mt-2">
                <div className="bg-gradient-to-r from-primary-500 to-purple-500 h-2 rounded-full" style={{ width: '65%' }} />
              </div>
            </div>
            <div>
              <p className="text-sm text-primary-500">Potential Monthly Savings</p>
              <p className="text-lg font-semibold text-emerald-600">$320.00</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard; 