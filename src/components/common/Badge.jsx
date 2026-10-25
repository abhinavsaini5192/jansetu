import React from 'react';

export const Badge = ({ children, variant = 'default', size = 'md', dot = false, className = '' }) => {
  const variants = {
    default: 'bg-slate-800/60 text-slate-300 border-slate-700/60',
    primary: 'bg-blue-500/10 text-blue-300 border-blue-500/25 shadow-[0_0_10px_rgba(59,130,246,0.15)]',
    success: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/25 shadow-[0_0_10px_rgba(16,185,129,0.15)]',
    warning: 'bg-amber-500/10 text-amber-300 border-amber-500/25 shadow-[0_0_10px_rgba(245,158,11,0.15)]',
    danger: 'bg-rose-500/10 text-rose-300 border-rose-500/25 shadow-[0_0_10px_rgba(244,63,94,0.15)]',
    teal: 'bg-teal-500/10 text-teal-300 border-teal-500/25 shadow-[0_0_10px_rgba(20,184,166,0.15)]',
    purple: 'bg-indigo-500/10 text-indigo-300 border-indigo-500/25 shadow-[0_0_10px_rgba(99,102,241,0.15)]',
    secondary: 'bg-slate-800/40 text-slate-400 border-slate-700/40',
  };

  const dotColors = {
    default: 'bg-slate-400',
    primary: 'bg-blue-400',
    success: 'bg-emerald-400',
    warning: 'bg-amber-400',
    danger: 'bg-rose-400',
    teal: 'bg-teal-400',
    purple: 'bg-indigo-400',
    secondary: 'bg-slate-400',
  };

  const sizes = {
    sm: 'text-[10px] px-2 py-0.5 font-medium tracking-tight',
    md: 'text-[11px] px-2.5 py-0.5 font-semibold tracking-tight',
    lg: 'text-xs px-3 py-1 font-semibold tracking-normal',
  };

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border backdrop-blur-md ${variants[variant] || variants.default} ${sizes[size]} ${className}`}>
      {dot && (
        <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${dotColors[variant] || 'bg-blue-400'} animate-pulse`} />
      )}
      <span>{children}</span>
    </span>
  );
};
