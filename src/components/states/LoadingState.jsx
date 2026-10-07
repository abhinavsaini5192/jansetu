import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingState = ({ message = "Loading data from platform server...", minHeight = "min-h-[220px]" }) => {
  return (
    <div className={`flex flex-col items-center justify-center p-8 text-center ${minHeight} glass-card rounded-2xl border border-navy-700/80`}>
      <Loader2 className="w-8 h-8 text-blue-400 animate-spin mb-3" />
      <p className="text-xs font-medium text-slate-300">{message}</p>
      <span className="text-[10px] text-slate-500 mt-1">Connecting to backend services...</span>
    </div>
  );
};
