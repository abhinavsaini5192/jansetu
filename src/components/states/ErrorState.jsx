import React from 'react';
import { AlertCircle, RotateCcw } from 'lucide-react';

export const ErrorState = ({
  title = "Failed to Load Information",
  message = "A communication error occurred while contacting the server.",
  onRetry = null,
  minHeight = "min-h-[220px]",
  className = ""
}) => {
  return (
    <div className={`flex flex-col items-center justify-center p-8 text-center glass-card rounded-2xl border border-rose-500/30 bg-rose-500/5 ${minHeight} ${className}`}>
      <div className="w-12 h-12 rounded-2xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400 mb-3 shadow-sm">
        <AlertCircle className="w-6 h-6" />
      </div>
      <h4 className="text-sm font-bold text-white mb-1">{title}</h4>
      <p className="text-xs text-rose-200/80 max-w-sm leading-relaxed mb-4">{message}</p>
      
      {onRetry && (
        <button
          onClick={onRetry}
          type="button"
          className="px-4 py-2 rounded-xl bg-navy-800 hover:bg-navy-750 text-slate-200 border border-navy-600 hover:border-navy-500 text-xs font-semibold flex items-center space-x-2 transition-colors shadow-sm"
        >
          <RotateCcw className="w-3.5 h-3.5 text-rose-400" />
          <span>Retry Request</span>
        </button>
      )}
    </div>
  );
};
