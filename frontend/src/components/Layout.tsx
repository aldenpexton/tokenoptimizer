import { Outlet } from 'react-router-dom';
import { BarChart3, Home, Settings, List, PieChart } from 'lucide-react';
import { Link } from 'react-router-dom';

const Layout = () => {
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