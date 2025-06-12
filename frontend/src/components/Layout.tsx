import React from 'react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';

const Layout: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const isLandingPage = location.pathname === '/';
  
  const handleNavigation = (path: string) => (e: React.MouseEvent) => {
    e.preventDefault();
    navigate(path);
  };
  
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-sm shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo/Brand */}
            <div className="flex items-center">
              <Link 
                to="/" 
                className="flex-shrink-0"
                onClick={handleNavigation('/')}
              >
                <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-600 to-purple-600">
                  TokenOptimizer
                </h1>
              </Link>
            </div>

            {/* Center Navigation */}
            {!isLandingPage && (
              <div className="flex items-center space-x-1">
                <Link
                  to="/dashboard"
                  onClick={handleNavigation('/dashboard')}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-all ${
                    location.pathname === '/dashboard'
                      ? 'text-white bg-gradient-to-r from-primary-600 to-purple-600 shadow-sm'
                      : 'text-primary-600 hover:text-primary-700 hover:bg-primary-50'
                  }`}
                >
                  Dashboard
                </Link>
                <Link
                  to="/logs"
                  onClick={handleNavigation('/logs')}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-all ${
                    location.pathname === '/logs'
                      ? 'text-white bg-gradient-to-r from-primary-600 to-purple-600 shadow-sm'
                      : 'text-primary-600 hover:text-primary-700 hover:bg-primary-50'
                  }`}
                >
                  Logs
                </Link>
              </div>
            )}

            {/* Right side navigation */}
            <div className="flex items-center">
              {isLandingPage ? (
                <Link
                  to="/dashboard"
                  onClick={handleNavigation('/dashboard')}
                  className="px-4 py-2 bg-gradient-to-r from-primary-600 to-purple-600 text-white rounded-lg text-sm font-medium transition-all hover:shadow-md"
                >
                  Open Dashboard
                </Link>
              ) : (
                <Link
                  to="/"
                  onClick={handleNavigation('/')}
                  className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                >
                  ← Back to Home
                </Link>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 bg-gradient-to-br from-indigo-50 via-white to-purple-50">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white/90 backdrop-blur-sm border-t border-primary-100/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex gap-6">
              <a
                href="https://github.com/yourusername/tokenoptimizer"
                className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                target="_blank"
                rel="noopener noreferrer"
              >
                GitHub
              </a>
              <Link
                to="/privacy"
                className="text-primary-600 hover:text-primary-700 text-sm font-medium"
              >
                Privacy
              </Link>
              <a
                href="mailto:contact@example.com"
                className="text-primary-600 hover:text-primary-700 text-sm font-medium"
              >
                Contact
              </a>
            </div>
            <p className="text-sm text-primary-500">
              Dashboard is in private beta; data shown may be synthetic.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout; 