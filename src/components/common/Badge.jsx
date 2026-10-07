import React from 'react';

export const Badge = ({ children, variant = 'default', size = 'md', className = '' }) => {
  const variants = {
    default: 'bg-navy-750 text-slate-300 border-navy-600',
    primary: 'bg-blue-500/15 text-blue-300 border-blue-500/30',
    success: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
    warning: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
    danger: 'bg-rose-500/15 text-rose-300 border-rose-500/30',
    teal: 'bg-teal-500/15 text-teal-300 border-teal-500/30',
    purple: 'bg-purple-500/15 text-purple-300 border-purple-500/30',
  };

  const sizes = {
    sm: 'text-[10px] px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
    lg: 'text-sm px-3 py-1.5 font-semibold',
  };

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border font-medium ${variants[variant] || variants.default} ${sizes[size]} ${className}`}>
      {children}
    </span>
  );
};
