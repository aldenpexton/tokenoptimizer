import React from 'react';
import { MessageCircle, Code, Database, BarChart3 } from 'lucide-react';

const FlowDiagram: React.FC = () => {
  const steps = [
    { 
      Icon: MessageCircle, 
      label: 'Your AI App',
      sublabel: 'Chatbots, Content Gen, Search'
    },
    { 
      Icon: Code, 
      label: 'TokenOptimizer SDK',
      sublabel: 'Drop-in monitoring'
    },
    { 
      Icon: Database, 
      label: 'Secure DB',
      sublabel: 'Real-time logging'
    },
    { 
      Icon: BarChart3, 
      label: 'Cost Dashboard',
      sublabel: 'Instant insights'
    },
  ];

  return (
    <div className="w-full py-16">
      <div className="flex flex-col md:flex-row items-center justify-center gap-6 md:gap-12">
        {steps.map((Step, index) => (
          <React.Fragment key={Step.label}>
            <div className="flex flex-col items-center text-center group">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center mb-4 shadow-md transition-all group-hover:scale-110 group-hover:shadow-lg group-hover:rotate-3">
                <Step.Icon className="w-10 h-10 text-primary-600 transition-transform group-hover:-rotate-3" />
              </div>
              <span className="text-base font-medium text-primary-900 transition-colors group-hover:text-primary-600">
                {Step.label}
              </span>
              <span className="text-sm text-primary-500 mt-1">
                {Step.sublabel}
              </span>
            </div>
            {index < steps.length - 1 && (
              <div className="hidden md:flex items-center space-x-1">
                <div className="w-3 h-3 rounded-full bg-primary-200" />
                <div className="w-16 h-0.5 bg-gradient-to-r from-primary-200 to-primary-300" />
                <div className="w-3 h-3 rounded-full bg-primary-300" />
                <div className="w-16 h-0.5 bg-gradient-to-r from-primary-300 to-primary-400" />
                <div className="w-3 h-3 rounded-full bg-primary-400" />
              </div>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};

export default FlowDiagram; 