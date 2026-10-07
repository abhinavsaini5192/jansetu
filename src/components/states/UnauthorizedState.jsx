import React from 'react';
import { ShieldAlert, LogIn } from 'lucide-react';
import { Link } from 'react-router-dom';

export const UnauthorizedState = ({
  title = "Authentication Required",
  message = "You must be signed in with the authorized role to access this module.",
  loginPath = "/login"
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center min-h-[260px] glass-card rounded-2xl border border-amber-500/30 bg-amber-500/5">
      <div className="w-12 h-12 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 mb-3 shadow-sm">
        <ShieldAlert className="w-6 h-6" />
      </div>
      <h4 className="text-sm font-bold text-white mb-1">{title}</h4>
      <p className="text-xs text-slate-400 max-w-sm leading-relaxed mb-4">{message}</p>
      
      <Link
        to={loginPath}
        className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs flex items-center space-x-1.5 transition-all shadow-sm"
      >
        <LogIn className="w-3.5 h-3.5" />
        <span>Sign In to Continue</span>
      </Link>
    </div>
  );
};
