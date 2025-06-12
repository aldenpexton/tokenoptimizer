import React from 'react';
import { Link } from 'react-router-dom';
import { Eye, Scale, DollarSign } from 'lucide-react';
import FlowDiagram from '../components/marketing/FlowDiagram';
import ValueCard from '../components/marketing/ValueCard';

const LandingPage: React.FC = () => {
  const valueProps = [
    {
      icon: Eye,
      title: 'Full Visibility',
      description: 'Every prompt & completion logged in real time.',
      colorClass: 'from-blue-500/10 to-blue-600/10 text-blue-600'
    },
    {
      icon: Scale,
      title: 'Model Benchmarking',
      description: 'Compare GPT-4, Claude, Gemini on cost, latency, and token usage.',
      colorClass: 'from-purple-500/10 to-purple-600/10 text-purple-600'
    },
    {
      icon: DollarSign,
      title: 'Actionable Savings',
      description: 'Get cheaper model suggestions automatically.',
      colorClass: 'from-emerald-500/10 to-emerald-600/10 text-emerald-600'
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 overflow-hidden">
      {/* Hero Section */}
      <div className="relative">
        {/* Background Elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-32 w-96 h-96 bg-gradient-to-br from-primary-200/30 to-primary-400/30 rounded-full blur-3xl" />
          <div className="absolute top-20 -left-32 w-96 h-96 bg-gradient-to-tr from-purple-200/30 to-purple-400/30 rounded-full blur-3xl" />
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-36">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-600 to-purple-600 mb-8 leading-[1.2] tracking-tight">
              Make your LLM API spend go farther.
            </h1>
            <p className="text-xl md:text-2xl text-primary-800 mb-12 max-w-3xl mx-auto">
              Track token usage, benchmark models, and uncover cost-savings in minutes.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
              <Link
                to="/dashboard"
                className="px-8 py-4 bg-gradient-to-r from-primary-600 to-purple-600 text-white rounded-lg font-medium text-lg transition-all hover:scale-105 hover:shadow-lg shadow-md"
              >
                Open Live Dashboard
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Flow Diagram */}
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-white/80 to-white" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <FlowDiagram />
        </div>
      </div>

      {/* Value Props */}
      <div className="relative bg-white/80 backdrop-blur-sm py-24">
        <div className="absolute inset-0 bg-gradient-to-t from-primary-50/50 to-transparent" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {valueProps.map((prop) => (
              <ValueCard
                key={prop.title}
                icon={prop.icon}
                title={prop.title}
                description={prop.description}
                colorClass={prop.colorClass}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="relative bg-white/90 backdrop-blur-sm">
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

export default LandingPage; 