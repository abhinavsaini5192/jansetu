import React, { useState, useRef, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import logoImg from '../../assets/logo-white.png';
import { 
  Send, 
  Layers, 
  Lock, 
  ShieldCheck, 
  ChevronDown, 
  LogOut, 
  Building2, 
  Sparkles, 
  GraduationCap, 
  Briefcase, 
  TrendingUp, 
  Award,
  User,
  UserCheck,
  LogIn
} from 'lucide-react';

export const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, isOfficial, activeRole, logout } = useAuth();
  const [isOfficialMenuOpen, setIsOfficialMenuOpen] = useState(false);
  const dropdownRef = useRef(null);

  const isCitizenActive = location.pathname === '/citizen-portal';
  const isProblemsActive = location.pathname === '/problems' || location.pathname === '/challenges';
  const isLoginActive = location.pathname === '/login';

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOfficialMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSignOut = async () => {
    setIsOfficialMenuOpen(false);
    await logout();
    navigate('/');
  };

  const officialDesks = [
    { title: "Validation Queue & Outreach", path: "/government-dashboard", icon: Building2, desc: "State Department Triaging" },
    { title: "AI Semantic Intelligence", path: "/ai-intelligence", icon: Sparkles, desc: "Clustering & Risk Scoring" },
    { title: "University Recommendations", path: "/university-matching", icon: GraduationCap, desc: "Autonomous HEI Adoption" },
    { title: "University R&D Workspace", path: "/university-workspace", icon: GraduationCap, desc: "Faculty & Student Projects" },
    { title: "Industry CSR Tech Transfer", path: "/industry-collaboration", icon: Briefcase, desc: "Co-Funding & Sponsorship" },
    { title: "Project Lifecycle Engine", path: "/project-lifecycle", icon: TrendingUp, desc: "Milestones & Delays" },
    { title: "Verified Societal Impact", path: "/impact-dashboard", icon: Award, desc: "Evidence Auditing" },
  ];

  return (
    <header className="fixed top-3 sm:top-4 inset-x-0 z-50 flex justify-center pointer-events-none px-3 sm:px-6">
      <div className="w-full max-w-6xl pointer-events-auto rounded-2xl sm:rounded-full bg-[#0D1424]/90 backdrop-blur-2xl border border-white/[0.12] border-t-white/[0.22] shadow-[0_20px_50px_rgba(0,0,0,0.7),0_0_25px_rgba(59,130,246,0.15)] px-4 sm:px-6 py-2.5 transition-all flex items-center justify-between">
        
        {/* Brand Identity / Logo */}
        <Link to="/" className="flex items-center space-x-3 group">
          <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-saas-card/90 border border-white/[0.12] p-1.5 shadow-[0_0_18px_rgba(255,255,255,0.15)] flex items-center justify-center group-hover:scale-105 group-hover:border-teal-400/40 transition-all shrink-0">
            <img 
              src={logoImg} 
              alt="JanSetu Logo" 
              className="w-full h-full object-contain filter drop-shadow-[0_0_6px_rgba(255,255,255,0.5)]" 
            />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-lg sm:text-xl font-black font-display tracking-tight text-white group-hover:text-teal-300 transition-colors">
                Jan<span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-400 via-cyan-400 to-blue-400">Setu</span>
              </span>
              {isAuthenticated ? (
                isOfficial ? (
                  <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/35 flex items-center space-x-1.5 shadow-[0_0_10px_rgba(245,158,11,0.2)]">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse"></span>
                    <span>Official</span>
                  </span>
                ) : (
                  <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/35 flex items-center space-x-1.5 shadow-[0_0_10px_rgba(16,185,129,0.2)]">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                    <span>Citizen</span>
                  </span>
                )
              ) : (
                <span className="text-[9px] uppercase font-mono font-bold tracking-widest px-1.5 py-0.5 rounded bg-white/[0.05] text-slate-400 border border-white/[0.08]">
                  Platform
                </span>
              )}
            </div>
            <p className="text-[9px] text-slate-400 tracking-tight hidden lg:block font-mono">
              Problem to Deployable Solutions • SIH26043
            </p>
          </div>
        </Link>

        {/* Navigation Actions */}
        <div className="flex items-center space-x-1.5 sm:space-x-2.5">
          
          {/* Uploaded Problems */}
          <Link
            to="/problems"
            className={`flex items-center space-x-1.5 px-3.5 py-1.5 sm:py-2 rounded-xl text-xs font-semibold transition-all ${
              isProblemsActive
                ? 'bg-blue-600/20 text-blue-300 border border-blue-500/40 shadow-glow-sm'
                : 'text-slate-300 hover:text-white hover:bg-white/[0.06] border border-transparent'
            }`}
          >
            <Layers className="w-3.5 h-3.5 text-blue-400" />
            <span>Problems</span>
          </Link>

          {/* Citizen Submission Portal */}
          <Link
            to="/citizen-portal"
            className={`flex items-center space-x-1.5 px-3.5 py-1.5 sm:py-2 rounded-xl text-xs font-semibold transition-all ${
              isCitizenActive
                ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40 shadow-glow-sm'
                : 'bg-white/[0.04] hover:bg-white/[0.08] text-slate-200 border border-white/[0.08] hover:border-white/[0.15]'
            }`}
          >
            <Send className="w-3.5 h-3.5 text-teal-400" />
            <span>Report Challenge</span>
          </Link>

          {/* Authenticated View: Official vs Citizen */}
          {isAuthenticated ? (
            isOfficial ? (
              /* Official Workspace Dropdown */
              <div className="relative" ref={dropdownRef}>
                <button
                  type="button"
                  onClick={() => setIsOfficialMenuOpen(!isOfficialMenuOpen)}
                  className="flex items-center space-x-1.5 px-3.5 py-1.5 sm:py-2 rounded-xl btn-saas-primary text-xs font-bold transition-all shadow-glow-sm"
                >
                  <ShieldCheck className="w-3.5 h-3.5 text-white" />
                  <span>Official Desks</span>
                  <ChevronDown className="w-3.5 h-3.5 ml-0.5 opacity-80" />
                </button>

                {/* Dropdown Menu */}
                {isOfficialMenuOpen && (
                  <div className="absolute right-0 mt-3 w-72 rounded-2xl saas-panel border border-white/[0.12] shadow-saas-dropdown p-2 space-y-1 z-50 animate-in fade-in slide-in-from-top-2">
                    <div className="px-3 py-2 border-b border-white/[0.08] text-[11px]">
                      <p className="font-bold text-white truncate">{user?.full_name || "Official Account"}</p>
                      <p className="text-teal-300 text-[10px] truncate">{user?.department || user?.email}</p>
                    </div>

                    <div className="py-1">
                      {officialDesks.map((desk, idx) => {
                        const Icon = desk.icon;
                        const isActive = location.pathname === desk.path;
                        return (
                          <Link
                            key={idx}
                            to={desk.path}
                            onClick={() => setIsOfficialMenuOpen(false)}
                            className={`flex items-start space-x-2.5 p-2 rounded-xl text-xs transition-colors ${
                              isActive
                                ? 'bg-blue-600/20 text-blue-300 font-semibold'
                                : 'text-slate-300 hover:text-white hover:bg-white/[0.06]'
                            }`}
                          >
                            <Icon className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                            <div className="min-w-0">
                              <p className="font-medium truncate">{desk.title}</p>
                              <p className="text-[10px] text-slate-400 truncate">{desk.desc}</p>
                            </div>
                          </Link>
                        );
                      })}
                    </div>

                    <div className="pt-1 border-t border-white/[0.08]">
                      <button
                        onClick={handleSignOut}
                        className="w-full flex items-center space-x-2 p-2 rounded-xl text-xs text-rose-300 hover:text-rose-200 hover:bg-rose-500/10 transition-colors font-medium"
                      >
                        <LogOut className="w-3.5 h-3.5" />
                        <span>Sign Out</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              /* Citizen Logged In Controls */
              <div className="flex items-center space-x-1.5 sm:space-x-2">
                <Link
                  to="/problems?tab=my_problems"
                  className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 sm:py-2 rounded-xl bg-saas-card/80 hover:bg-saas-card border border-emerald-500/30 text-xs font-semibold text-emerald-300 hover:border-emerald-500/50 transition-colors shadow-sm"
                >
                  <UserCheck className="w-3.5 h-3.5 text-emerald-400" />
                  <span>My Problems</span>
                </Link>

                <div className="flex items-center space-x-1.5 sm:space-x-2 px-2.5 sm:px-3 py-1.5 rounded-xl bg-saas-card/80 border border-white/[0.08] text-xs">
                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  <span className="font-semibold text-white max-w-[90px] sm:max-w-[110px] truncate">
                    {user?.full_name?.split(' ')[0] || "Citizen"}
                  </span>
                  <button
                    onClick={handleSignOut}
                    title="Sign Out"
                    className="p-1 rounded text-slate-400 hover:text-rose-400 transition-colors"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            )
          ) : (
            /* Unauthenticated View: Single Unified Sign In Button */
            <Link
              to="/login"
              className={`flex items-center space-x-1.5 px-4 py-1.5 sm:py-2 rounded-xl text-xs font-bold transition-all btn-saas-primary shadow-glow-sm`}
            >
              <LogIn className="w-3.5 h-3.5" />
              <span>Sign In</span>
            </Link>
          )}

        </div>

      </div>
    </header>
  );
};
