import React from 'react';
import { useJanSetu } from '../../context/JanSetuContext';
import { CheckCircle2, Clock } from 'lucide-react';

export const LifecycleProgressBar = ({
  statusKey = "SUBMITTED",
  title = null,
  district = null,
  affected = null,
  compact = false
}) => {
  const { stages } = useJanSetu();

  const currentIndex = Math.max(0, stages.findIndex(s => s.key === statusKey));
  const currentStageObj = stages[currentIndex] || stages[0];
  const percentage = Math.round(((currentIndex + 1) / stages.length) * 100);

  if (compact) {
    return (
      <div className="w-full bg-navy-850 border border-navy-700 rounded-xl p-3">
        <div className="flex items-center justify-between text-xs mb-1.5">
          <span className="text-slate-400 font-medium">Innovation Pipeline Progress</span>
          <span className="font-bold text-blue-400 font-mono">{percentage}% ({currentIndex + 1}/10 Stages)</span>
        </div>
        <div className="w-full bg-navy-950 rounded-full h-2 overflow-hidden border border-navy-800">
          <div 
            className="h-full bg-gradient-to-r from-blue-600 via-teal-400 to-emerald-500 rounded-full transition-all duration-500 shadow-glow-sm"
            style={{ width: `${percentage}%` }}
          />
        </div>
        <div className="flex items-center justify-between text-[10px] text-slate-400 mt-1">
          <span>Current: <strong className="text-white">{currentStageObj.label}</strong></span>
          {title && <span className="truncate max-w-[160px]"><strong className="text-slate-300">{title}</strong></span>}
        </div>
      </div>
    );
  }

  return (
    <div className="glass-panel rounded-2xl p-6 border border-navy-700/80 mb-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-bold uppercase tracking-wider text-brand-primary bg-blue-500/10 border border-blue-500/20 px-2.5 py-0.5 rounded-full">
              End-to-End Problem Lifecycle
            </span>
            <span className="text-xs text-slate-400 font-mono">SIH26043 OS</span>
          </div>
          <h2 className="text-lg font-bold text-white mt-1">
            Challenge Pipeline {title ? <span>: <span className="text-blue-400">{title}</span></span> : null}
          </h2>
          {(district || affected) && (
            <p className="text-xs text-slate-400 mt-0.5">
              {district && <span>District: <span className="text-white">{district}</span></span>}
              {district && affected && <span> • </span>}
              {affected && <span>Affected: <span className="text-amber-400">{affected}</span></span>}
            </p>
          )}
        </div>

        <div className="text-right sm:border-l sm:border-navy-700 sm:pl-6">
          <div className="text-2xl font-black text-white font-display">
            {percentage}%
          </div>
          <div className="text-[11px] text-emerald-400 font-medium flex items-center space-x-1 justify-end">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Active: {currentStageObj.label}</span>
          </div>
        </div>
      </div>

      {/* Progress Line */}
      <div className="w-full bg-navy-950 rounded-full h-2.5 mb-6 overflow-hidden border border-navy-800">
        <div 
          className="h-full bg-gradient-to-r from-blue-600 via-teal-400 to-emerald-500 transition-all duration-700 shadow-glow-sm"
          style={{ width: `${percentage}%` }}
        />
      </div>

      {/* 10 Step Dots */}
      <div className="grid grid-cols-2 sm:grid-cols-5 lg:grid-cols-10 gap-2 text-center">
        {stages.map((st, idx) => {
          const isDone = idx < currentIndex;
          const isCurrent = idx === currentIndex;

          return (
            <div 
              key={st.key}
              className={`p-2 rounded-xl border text-left transition-all ${
                isCurrent 
                  ? 'bg-blue-600/20 border-blue-500 shadow-glow-sm' 
                  : isDone
                  ? 'bg-navy-800/60 border-emerald-500/30 text-slate-300'
                  : 'bg-navy-950/40 border-navy-800 text-slate-400'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] font-mono font-bold">{idx + 1}</span>
                {isDone ? (
                  <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                ) : isCurrent ? (
                  <span className="w-2 h-2 rounded-full bg-blue-400 animate-ping" />
                ) : (
                  <Clock className="w-2.5 h-2.5 text-slate-400" />
                )}
              </div>
              <p className="text-[11px] font-bold leading-tight truncate text-slate-200" title={st.label}>
                {st.label}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
};
