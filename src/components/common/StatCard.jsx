import React from 'react';

export const StatCard = ({ title, value, subtitle, icon: Icon, trend, color = 'blue' }) => {
  const colorGradients = {
    blue: 'from-blue-600/20 to-blue-400/5 text-blue-400 border-blue-500/20',
    emerald: 'from-emerald-600/20 to-emerald-400/5 text-emerald-400 border-emerald-500/20',
    teal: 'from-teal-600/20 to-teal-400/5 text-teal-400 border-teal-500/20',
    amber: 'from-amber-600/20 to-amber-400/5 text-amber-400 border-amber-500/20',
    purple: 'from-purple-600/20 to-purple-400/5 text-purple-400 border-purple-500/20',
    rose: 'from-rose-600/20 to-rose-400/5 text-rose-400 border-rose-500/20',
  };

  return (
    <div className={`glass-card glass-card-hover rounded-2xl p-5 border relative overflow-hidden group`}>
      {/* Subtle top glow line */}
      <div className={`absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r ${colorGradients[color] || colorGradients.blue}`} />
      
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-slate-400">{title}</p>
          <h3 className="text-2xl font-bold text-white mt-1 font-display tracking-tight group-hover:text-blue-300 transition-colors">
            {value}
          </h3>
          {subtitle && (
            <p className="text-xs text-slate-400 mt-1">{subtitle}</p>
          )}
          {trend && (
            <div className="flex items-center space-x-1 mt-2 text-[11px] font-semibold text-emerald-400">
              <span>↑ {trend}</span>
            </div>
          )}
        </div>
        
        {Icon && (
          <div className={`p-3 rounded-xl bg-navy-800/80 border border-white/5 ${colorGradients[color]?.split(' ')[2] || 'text-blue-400'} group-hover:scale-110 transition-transform`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
    </div>
  );
};
