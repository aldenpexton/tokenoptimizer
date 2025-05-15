import { Outlet } from 'react-router-dom';
import { BarChart3, Home, Settings, List, PieChart } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useState } from 'react';

const Layout = () => {
  const [dateRange, setDateRange] = useState('Last 30 days');

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside className="w-64 bg-card border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h1 className="text-xl font-bold text-accent">TokenOptimizer</h1>
        </div>
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            <li>
              <Link 
                to="/" 
                className="flex items-center gap-3 p-2 rounded-md hover:bg-gray-100 text-primary-text"
              >
                <Home size={18} />
                <span>Dashboard</span>
              </Link>
            </li>
            <li>
              <Link 
                to="/usage" 
                className="flex items-center gap-3 p-2 rounded-md hover:bg-gray-100 text-primary-text"
              >
                <BarChart3 size={18} />
                <span>Usage</span>
              </Link>
            </li>
            <li>
              <Link 
                to="/models" 
                className="flex items-center gap-3 p-2 rounded-md hover:bg-gray-100 text-primary-text"
              >
                <PieChart size={18} />
                <span>Models</span>
              </Link>
            </li>
            <li>
              <Link 
                to="/logs" 
                className="flex items-center gap-3 p-2 rounded-md hover:bg-gray-100 text-primary-text"
              >
                <List size={18} />
                <span>Logs</span>
              </Link>
            </li>
            <li>
              <Link 
                to="/settings" 
                className="flex items-center gap-3 p-2 rounded-md hover:bg-gray-100 text-primary-text"
              >
                <Settings size={18} />
                <span>Settings</span>
              </Link>
            </li>
          </ul>
        </nav>
        <div className="p-4 border-t border-gray-200">
          <div className="text-sm text-gray-500">TokenOptimizer v1.0</div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        {/* Header */}
        <header className="bg-card border-b border-gray-200 p-4 flex justify-between items-center sticky top-0 z-10">
          <h2 className="text-xl font-semibold">Dashboard</h2>
          <div className="flex items-center gap-4">
            <div className="relative">
              <select 
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
                className="appearance-none bg-gray-50 border border-gray-200 rounded-md px-4 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-accent"
              >
                <option>Last 7 days</option>
                <option>Last 30 days</option>
                <option>Last 90 days</option>
                <option>This year</option>
              </select>
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </div>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout; 