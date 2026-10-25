import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { 
  ShieldAlert, 
  Lock, 
  ArrowRight, 
  Layers, 
  Send, 
  Sparkles, 
  CheckCircle2, 
  Building2, 
  GraduationCap, 
  Briefcase 
} from 'lucide-react';

export const AccessDenied = ({ deskTitle = "Official Administration Desk" }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { loginPreset, officialPresets } = useAuth();

  const handleQuickUnlock = async (presetId) => {
    try {
      await loginPreset(presetId);
      // Stay on the current route or refresh view
      window.location.reload();
    } catch (err) {
      navigate(`/login?redirect=${encodeURIComponent(location.pathname)}`);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-8 animate-in fade-in duration-300">
      
      {/* Security Header Banner */}
      <div className="rounded-3xl saas-panel border border-white/[0.12] p-8 sm:p-10 shadow-2xl relative overflow-hidden">
        {/* Specular rose accent line */}
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-rose-500 via-red-500 to-amber-500" />
        
        {/* Ambient background glow */}
        <div className="absolute top-0 right-0 w-80 h-80 bg-rose-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 space-y-6">
          
          {/* Badge & Lock Icon */}
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="saas-badge bg-rose-500/10 border-rose-500/30 text-rose-300">
              <span className="w-1.5 h-1.5 rounded-full bg-rose-400 animate-pulse"></span>
              <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
              <span>RESTRICTED OFFICIAL CLEARANCE REQUIRED</span>
            </div>

            <span className="text-xs font-mono text-slate-500">
              Protocol: SIH26043-RBAC-01
            </span>
          </div>

          {/* Heading */}
          <div className="space-y-2">
            <h1 className="text-2xl sm:text-3xl font-black text-white font-display tracking-tight flex items-center space-x-3">
              <span className="p-2.5 rounded-xl bg-white/[0.05] border border-white/[0.1] text-rose-400 inline-block shadow-sm">
                <Lock className="w-6 h-6" />
              </span>
              <span>{deskTitle} Is Not Publicly Visible</span>
            </h1>
            <p className="text-sm text-slate-300 max-w-2xl leading-relaxed font-normal">
              In accordance with state governance protocols, validation queues, AI triaging models, 
              and university R&D submissions are reserved exclusively for authorized nodal officers, 
              accredited academic researchers, and verified CSR sponsors.
            </p>
          </div>

          {/* Division of Access Comparison Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            
            {/* Public Rights */}
            <div className="p-5 rounded-2xl saas-card space-y-2.5">
              <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-teal-300">
                <CheckCircle2 className="w-4 h-4 text-teal-400" />
                <span>Public Citizen Access</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed font-normal">
                As a member of the public, you have full authorization to report grassroots community problems 
                and browse the transparent registry of all uploaded problem statements.
              </p>
              <div className="pt-2 flex flex-wrap gap-2">
                <button
                  onClick={() => navigate('/problems')}
                  className="px-3.5 py-2 rounded-xl btn-saas-secondary text-xs font-semibold flex items-center space-x-1.5"
                >
                  <Layers className="w-3.5 h-3.5 text-blue-400" />
                  <span>Browse Problems</span>
                </button>
                <button
                  onClick={() => navigate('/citizen-portal')}
                  className="px-3.5 py-2 rounded-xl btn-saas-primary text-xs font-semibold flex items-center space-x-1.5"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Report Challenge</span>
                </button>
              </div>
            </div>

            {/* Official Rights */}
            <div className="p-5 rounded-2xl saas-card space-y-2.5">
              <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-blue-300">
                <Lock className="w-4 h-4 text-blue-400" />
                <span>Official Nodal Desks</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed font-normal">
                State administration, semantic duplicate triaging, explainable HEI matching, 
                and project grant allocation require verified official ID credentials.
              </p>
              <div className="pt-2">
                <button
                  onClick={() => navigate(`/login?redirect=${encodeURIComponent(location.pathname)}`)}
                  className="w-full px-4 py-2.5 rounded-xl btn-saas-primary text-xs font-bold flex items-center justify-center space-x-2"
                >
                  <span>Sign In with Official ID</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

          </div>

          {/* Quick Evaluator Access Section */}
          <div className="pt-5 border-t border-white/[0.08]">
            <div className="flex items-center justify-between pb-3">
              <span className="text-xs font-semibold text-slate-300 flex items-center space-x-1.5">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                <span>Evaluator & Judge 1-Click Official Clearance (Hackathon Testing):</span>
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {officialPresets.map((preset) => (
                <button
                  key={preset.id}
                  onClick={() => handleQuickUnlock(preset.id)}
                  className="p-3.5 rounded-xl saas-card text-left transition-all group flex flex-col justify-between hover:border-blue-500/50"
                >
                  <div>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-base">{preset.icon}</span>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-300 border border-blue-500/20 font-bold">
                        Official
                      </span>
                    </div>
                    <p className="text-xs font-bold text-white group-hover:text-blue-300 transition-colors line-clamp-1">
                      {preset.title.split('(')[0]}
                    </p>
                    <p className="text-[10px] text-slate-400 line-clamp-1 mt-0.5">
                      {preset.department}
                    </p>
                  </div>
                  <span className="text-[10px] text-blue-400 font-semibold mt-2.5 group-hover:underline">
                    Unlock as Official →
                  </span>
                </button>
              ))}
            </div>
          </div>

        </div>
      </div>

    </div>
  );
};
