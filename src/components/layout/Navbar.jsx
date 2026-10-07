import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Send, Layers } from 'lucide-react';

export const Navbar = () => {
  const location = useLocation();
  const isCitizenActive = location.pathname === '/citizen-portal';
  const isProblemsActive = location.pathname === '/problems' || location.pathname === '/challenges';

  return (
    <header className="sticky top-0 z-50 w-full border-b border-navy-700/80 bg-navy-900/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Identity / Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-teal-400 flex items-center justify-center shadow-glow-sm group-hover:scale-105 transition-transform">
              <span className="text-xl font-black text-white tracking-tighter">JS</span>
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="text-xl font-bold font-display tracking-tight text-white group-hover:text-brand-primary transition-colors">
                  Jan<span className="text-brand-teal">Setu</span>
                </span>
                <span className="text-[10px] uppercase font-bold tracking-widest px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">
                  Platform
                </span>
              </div>
              <p className="text-[10px] text-slate-400 tracking-tight hidden md:block">
                Problem to Deployable Solutions
              </p>
            </div>
          </Link>

          {/* Nav Actions */}
          <div className="flex items-center space-x-3">
            <Link
              to="/problems"
              className={`flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
                isProblemsActive
                  ? 'bg-blue-600/20 text-blue-300 border border-blue-500/40 shadow-glow-sm'
                  : 'text-slate-300 hover:text-white hover:bg-navy-800/80 border border-transparent'
              }`}
            >
              <Layers className="w-3.5 h-3.5 text-blue-400" />
              <span>Uploaded Problems</span>
            </Link>

            <Link
              to="/citizen-portal"
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                isCitizenActive
                  ? 'bg-blue-600/30 text-blue-300 border border-blue-500/50 shadow-glow-sm'
                  : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-glow-sm hover:scale-105'
              }`}
            >
              <Send className="w-3.5 h-3.5" />
              <span>Citizen Portal</span>
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
};
