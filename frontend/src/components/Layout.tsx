import React from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';

const Layout: React.FC = () => {
  const location = useLocation();
  const isLandingPage = location.pathname === '/';
  
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-sm shadow-sm">
        <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-10">
          <div className="flex justify-between items-center h-20">
            {/* Logo/Brand */}
            <div className="flex items-center space-x-8">
              <Link to="/" className="flex-shrink-0">
                <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-600 to-purple-600">
                  TokenOptimizer
                </h1>
              </Link>
              {!isLandingPage && (
                <div className="hidden sm:flex space-x-6">
                  <Link
                    to="/dashboard"
                    className={`px-4 py-2.5 rounded-md text-base font-medium transition-colors ${
                      location.pathname === '/dashboard'
                        ? 'text-primary-600 bg-primary-50'
                        : 'text-primary-600/80 hover:text-primary-600 hover:bg-primary-50'
                    }`}
                  >
                    Dashboard
                  </Link>
                  <Link
                    to="/logs"
                    className={`px-4 py-2.5 rounded-md text-base font-medium transition-colors ${
                      location.pathname === '/logs'
                        ? 'text-primary-600 bg-primary-50'
                        : 'text-primary-600/80 hover:text-primary-600 hover:bg-primary-50'
                    }`}
                  >
                    Logs
                  </Link>
                </div>
              )}
            </div>

            {/* Right side navigation */}
            <div className="flex items-center space-x-4">
              {isLandingPage ? (
                <Link
                  to="/dashboard"
                  className="px-4 py-2 bg-gradient-to-r from-primary-600 to-purple-600 text-white rounded-lg font-medium transition-all hover:shadow-md"
                >
                  Open Dashboard
                </Link>
              ) : (
                <Link
                  to="/"
                  className="text-primary-600 hover:text-primary-700 font-medium"
                >
                  ← Back to Home
                </Link>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="mt-auto bg-white/90 backdrop-blur-sm border-t border-primary-100/20">
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