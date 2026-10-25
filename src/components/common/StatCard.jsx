import React from 'react';

export const StatCard = ({ title, value, subtitle, icon: Icon, trend, color = 'blue' }) => {
  const colorAccents = {
    blue: {
      line: 'from-blue-500 via-indigo-500 to-transparent',
      iconBg: 'bg-blue-500/10 text-blue-400 border-blue-500/20 shadow-[0_0_12px_rgba(59,130,246,0.15)]',
      valueHover: 'group-hover:text-blue-300',
    },
    emerald: {
      line: 'from-emerald-500 via-teal-500 to-transparent',
      iconBg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 shadow-[0_0_12px_rgba(16,185,129,0.15)]',
      valueHover: 'group-hover:text-emerald-300',
    },
    teal: {
      line: 'from-teal-500 via-cyan-500 to-transparent',
      iconBg: 'bg-teal-500/10 text-teal-400 border-teal-500/20 shadow-[0_0_12px_rgba(20,184,166,0.15)]',
      valueHover: 'group-hover:text-teal-300',
    },
    amber: {
      line: 'from-amber-500 via-orange-500 to-transparent',
      iconBg: 'bg-amber-500/10 text-amber-400 border-amber-500/20 shadow-[0_0_12px_rgba(245,158,11,0.15)]',
      valueHover: 'group-hover:text-amber-300',
    },
    purple: {
      line: 'from-indigo-500 via-purple-500 to-transparent',
      iconBg: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20 shadow-[0_0_12px_rgba(99,102,241,0.15)]',
      valueHover: 'group-hover:text-indigo-300',
    },
    rose: {
      line: 'from-rose-500 via-pink-500 to-transparent',
      iconBg: 'bg-rose-500/10 text-rose-400 border-rose-500/20 shadow-[0_0_12px_rgba(244,63,94,0.15)]',
      valueHover: 'group-hover:text-rose-300',
    },
  };

  const accent = colorAccents[color] || colorAccents.blue;

  return (
    <div className="saas-card rounded-2xl p-5 relative overflow-hidden group">
      {/* Specular Top Accent Line */}
      <div className={`absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r ${accent.line}`} />
      
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">{title}</p>
          <h3 className={`text-2xl sm:text-3xl font-black text-white font-display tracking-tight transition-colors ${accent.valueHover}`}>
            {value}
          </h3>
          {subtitle && (
            <p className="text-xs text-slate-400 font-medium">{subtitle}</p>
          )}
          {trend && (
            <div className="inline-flex items-center space-x-1 pt-1 text-[11px] font-semibold text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              <span>{trend}</span>
            </div>
          )}
        </div>
        
        {Icon && (
          <div className={`p-3 rounded-2xl border ${accent.iconBg} group-hover:scale-105 transition-transform shrink-0`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
    </div>
  );
};
