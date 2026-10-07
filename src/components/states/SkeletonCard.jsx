import React from 'react';

export const SkeletonCard = ({ count = 1, className = "" }) => {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div 
          key={i} 
          className={`glass-card rounded-2xl p-5 border border-navy-750/80 animate-pulse space-y-3 ${className}`}
        >
          <div className="flex items-center justify-between">
            <div className="h-4 bg-navy-750 rounded-md w-24" />
            <div className="h-4 bg-navy-750 rounded-full w-16" />
          </div>
          <div className="h-6 bg-navy-700 rounded-md w-3/4" />
          <div className="space-y-1.5 pt-1">
            <div className="h-3 bg-navy-800 rounded w-full" />
            <div className="h-3 bg-navy-800 rounded w-5/6" />
          </div>
          <div className="flex items-center justify-between pt-2 border-t border-navy-800">
            <div className="h-3 bg-navy-750 rounded w-20" />
            <div className="h-6 bg-navy-750 rounded-lg w-28" />
          </div>
        </div>
      ))}
    </>
  );
};
