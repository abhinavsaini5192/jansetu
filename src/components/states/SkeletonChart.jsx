import React from 'react';

export const SkeletonChart = ({ height = "h-60" }) => {
  return (
    <div className={`w-full ${height} rounded-2xl glass-card border border-navy-750/80 p-6 flex flex-col justify-between animate-pulse`}>
      <div className="flex items-center justify-between">
        <div className="h-4 bg-navy-750 rounded w-36" />
        <div className="h-4 bg-navy-750 rounded w-16" />
      </div>
      <div className="flex items-end justify-between gap-3 h-36 pt-4">
        {[40, 65, 30, 85, 55, 75, 45].map((h, i) => (
          <div key={i} className="flex-1 flex flex-col items-center gap-2">
            <div 
              className="w-full bg-navy-800 rounded-t-md" 
              style={{ height: `${h}%` }} 
            />
            <div className="w-8 h-2.5 bg-navy-750 rounded" />
          </div>
        ))}
      </div>
    </div>
  );
};
