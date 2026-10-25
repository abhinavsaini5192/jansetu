import React from 'react';
import { Inbox, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const EmptyState = ({
  icon: Icon = Inbox,
  title = "No Records Found",
  description = "There are currently no items to display for this section.",
  actionLabel = null,
  actionTo = null,
  onAction = null,
  className = "",
  minHeight = "min-h-[240px]"
}) => {
  return (
    <div className={`flex flex-col items-center justify-center p-8 text-center saas-panel rounded-2xl border border-white/[0.08] ${minHeight} ${className}`}>
      <div className="w-12 h-12 rounded-2xl bg-white/[0.04] border border-white/[0.08] flex items-center justify-center text-slate-400 mb-4 shadow-sm">
        <Icon className="w-6 h-6 text-slate-300" />
      </div>
      <h4 className="text-sm font-bold text-white mb-1.5 font-display">{title}</h4>
      <p className="text-xs text-slate-400 max-w-sm leading-relaxed mb-5">{description}</p>
      
      {actionLabel && actionTo && (
        <Link
          to={actionTo}
          className="px-4 py-2 rounded-xl btn-saas-primary text-xs font-semibold flex items-center space-x-1.5 shadow-sm"
        >
          <span>{actionLabel}</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      )}

      {actionLabel && onAction && !actionTo && (
        <button
          onClick={onAction}
          type="button"
          className="px-4 py-2 rounded-xl btn-saas-primary text-xs font-semibold flex items-center space-x-1.5 shadow-sm"
        >
          <span>{actionLabel}</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
};
