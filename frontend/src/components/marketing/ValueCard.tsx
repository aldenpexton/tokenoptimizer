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
    <div className="group bg-white/40 backdrop-blur-sm rounded-2xl p-6 shadow-sm hover:shadow-lg hover:scale-[1.02] transition-all duration-300 flex flex-col items-center text-center border border-white/50">
      <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${colorClass} flex items-center justify-center mb-4 group-hover:scale-110 group-hover:rotate-3 transition-all`}>
        <Icon className="w-7 h-7 transition-transform group-hover:-rotate-3" />
      </div>
      <h3 className="text-lg font-semibold text-primary-900 mb-2 group-hover:text-primary-600 transition-colors">
        {title}
      </h3>
      <p className="text-primary-600/80 text-sm leading-relaxed">
        {description}
      </p>
    </div>
  );
};

export default ValueCard; 