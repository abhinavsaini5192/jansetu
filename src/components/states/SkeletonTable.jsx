import React from 'react';

export const SkeletonTable = ({ rows = 4, cols = 4 }) => {
  return (
    <div className="w-full overflow-hidden rounded-2xl glass-card border border-navy-700/80 p-4 animate-pulse">
      <div className="flex items-center justify-between pb-4 border-b border-navy-800">
        <div className="h-4 bg-navy-750 rounded w-32" />
        <div className="h-4 bg-navy-750 rounded w-20" />
      </div>
      <div className="divide-y divide-navy-800/60 mt-3 space-y-3">
        {Array.from({ length: rows }).map((_, r) => (
          <div key={r} className="pt-3 flex items-center justify-between gap-4">
            {Array.from({ length: cols }).map((_, c) => (
              <div 
                key={c} 
                className="h-3.5 bg-navy-800 rounded" 
                style={{ width: `${Math.max(15, 80 / cols)}%` }} 
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};
