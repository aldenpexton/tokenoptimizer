import React from 'react';
import { LucideIcon } from 'lucide-react';

interface ValueCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  colorClass?: string;
}

const ValueCard: React.FC<ValueCardProps> = ({ 
  icon: Icon, 
  title, 
  description,
  colorClass = "from-primary-500/10 to-primary-600/10 text-primary-600"
}) => {
  return (
    <div className="group bg-white/50 backdrop-blur-sm rounded-2xl p-8 shadow-sm border border-primary-100/50 hover:shadow-lg hover:scale-[1.02] transition-all duration-300 flex flex-col items-center text-center">
      <div className={`w-16 h-16 rounded-xl bg-gradient-to-br ${colorClass} flex items-center justify-center mb-6 group-hover:scale-110 group-hover:rotate-3 transition-all`}>
        <Icon className="w-8 h-8 transition-transform group-hover:-rotate-3" />
      </div>
      <h3 className="text-xl font-semibold text-primary-900 mb-3 group-hover:text-primary-600 transition-colors">
        {title}
      </h3>
      <p className="text-primary-600/90 leading-relaxed max-w-sm">
        {description}
      </p>
    </div>
  );
};

export default ValueCard; 