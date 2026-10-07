import React from 'react';
import { WifiOff, RotateCcw } from 'lucide-react';

export const OfflineState = ({ onRetry = null }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center min-h-[220px] glass-card rounded-2xl border border-navy-700">
      <div className="w-12 h-12 rounded-2xl bg-navy-850 border border-navy-700 flex items-center justify-center text-slate-400 mb-3">
        <WifiOff className="w-6 h-6 text-slate-400" />
      </div>
      <h4 className="text-sm font-bold text-white mb-1">Backend Service Unavailable</h4>
      <p className="text-xs text-slate-400 max-w-sm leading-relaxed mb-4">
        Unable to reach the platform API. The server may be restarting or your network connection might be interrupted.
      </p>
      
      {onRetry && (
        <button
          onClick={onRetry}
          type="button"
          className="px-4 py-2 rounded-xl bg-navy-800 hover:bg-navy-750 text-slate-200 border border-navy-600 text-xs font-semibold flex items-center space-x-2"
        >
          <RotateCcw className="w-3.5 h-3.5 text-blue-400" />
          <span>Check Connection</span>
        </button>
      )}
    </div>
  );
};
