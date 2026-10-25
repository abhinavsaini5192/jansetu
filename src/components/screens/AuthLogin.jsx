import React, { useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { JHARKHAND_DISTRICTS } from '../../config/constants';
import { isOfficialUser } from '../../utils/roleUtils';
import { 
  Lock, 
  Mail, 
  KeyRound, 
  ArrowRight, 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  Sparkles, 
  UserCheck, 
  UserPlus, 
  ShieldCheck,
  Building2,
  GraduationCap
} from 'lucide-react';

export const AuthLogin = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login, register, loginPreset, demoPresets } = useAuth();

  const redirectPath = searchParams.get('redirect');

  // Form states
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [district, setDistrict] = useState(JHARKHAND_DISTRICTS[0]);

  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Handle single unified login submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage('');
    setSuccessMessage('');

    try {
      if (isRegisterMode) {
        // Register new citizen
        const result = await register({
          email,
          password,
          fullName: fullName || 'Citizen User',
          district,
        });
        setSuccessMessage(`Account registered successfully. Welcome, ${result.user.full_name}!`);
        setTimeout(() => {
          navigate(redirectPath || '/problems?tab=my_problems');
        }, 600);
      } else {
        // Unified Login
        const result = await login({ email, password });
        const user = result.user;
        const isOfficial = isOfficialUser(user);

        if (isOfficial) {
          setSuccessMessage(`Official clearance verified: ${user.full_name || 'Official'}. Redirecting to desk...`);
          setTimeout(() => {
            navigate(redirectPath || '/government-dashboard');
          }, 600);
        } else {
          setSuccessMessage(`Citizen account verified: ${user.full_name || 'Citizen'}. Redirecting to portal...`);
          setTimeout(() => {
            navigate(redirectPath || '/problems?tab=my_problems');
          }, 600);
        }
      }
    } catch (err) {
      setErrorMessage(err.message || 'Authentication failed. Please verify your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle 1-click test login for evaluators
  const handlePresetLogin = async (preset) => {
    setIsLoading(true);
    setErrorMessage('');
    setSuccessMessage('');

    try {
      const result = await loginPreset(preset.id);
      const isOfficial = isOfficialUser(result.user);

      if (isOfficial) {
        setSuccessMessage(`Logged in as ${preset.title} (${preset.badge}). Redirecting to official desk...`);
        setTimeout(() => {
          navigate(redirectPath || preset.defaultRoute || '/government-dashboard');
        }, 500);
      } else {
        setSuccessMessage(`Logged in as ${preset.title}. Opening citizen portal...`);
        setTimeout(() => {
          navigate(redirectPath || '/problems?tab=my_problems');
        }, 500);
      }
    } catch (err) {
      setErrorMessage(err.message || 'Preset authentication failed.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto px-4 sm:px-6 py-12 space-y-8 animate-in fade-in">
      
      {/* Header */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-300 text-xs font-mono">
          <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse"></span>
          <span>JANSETU UNIFIED GATEWAY</span>
          <span>•</span>
          <span>ROLE DISCOVERY</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-white font-display tracking-tight">
          Single Portal Sign In
        </h1>
        <p className="text-xs sm:text-sm text-slate-300 max-w-md mx-auto leading-relaxed">
          One unified identity portal for both Citizens and Officials. The system automatically routes you to your authorized features based on your credentials.
        </p>
      </div>

      {/* Main Login Card */}
      <div className="rounded-3xl saas-panel border border-white/[0.12] p-6 sm:p-8 space-y-6 shadow-2xl relative overflow-hidden">
        {/* Specular blue top border */}
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-blue-500 via-indigo-500 to-cyan-400" />

        {/* Card Header & Mode Switcher */}
        <div className="flex items-center justify-between border-b border-white/[0.08] pb-4">
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-blue-400"></span>
            <h2 className="text-xs font-bold text-white uppercase tracking-wider">
              {isRegisterMode ? "Citizen Registration" : "Account Authentication"}
            </h2>
          </div>

          <button
            type="button"
            onClick={() => {
              setIsRegisterMode(!isRegisterMode);
              setErrorMessage('');
              setSuccessMessage('');
            }}
            className="text-xs font-semibold text-blue-400 hover:text-blue-300 transition-colors"
          >
            {isRegisterMode ? "Already have an account? Sign In" : "New Citizen? Register Here"}
          </button>
        </div>

        {/* Feedback Messages */}
        {errorMessage && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-start space-x-3 text-xs text-rose-300 animate-in fade-in">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
            <span>{errorMessage}</span>
          </div>
        )}

        {successMessage && (
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-start space-x-3 text-xs text-emerald-300 animate-in fade-in">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <span>{successMessage}</span>
          </div>
        )}

        {/* Single Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          
          {isRegisterMode && (
            <>
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">
                  Full Name / Community Title *
                </label>
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Ramesh Mahto"
                  className="w-full px-3.5 py-2.5 rounded-xl saas-input text-xs"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">
                  District in Jharkhand
                </label>
                <select
                  value={district}
                  onChange={(e) => setDistrict(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl saas-input text-xs cursor-pointer"
                >
                  {JHARKHAND_DISTRICTS.map((d) => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>
            </>
          )}

          {/* Email or ID */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300 flex items-center space-x-1.5">
              <Mail className="w-3.5 h-3.5 text-blue-400" />
              <span>Registered Email or ID *</span>
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="e.g. citizen@jansetu.gov.in or nodal.officer@jharkhand.gov.in"
              className="w-full px-3.5 py-2.5 rounded-xl saas-input text-xs"
            />
          </div>

          {/* Password */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300 flex items-center space-x-1.5">
              <KeyRound className="w-3.5 h-3.5 text-amber-400" />
              <span>Password *</span>
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              className="w-full px-3.5 py-2.5 rounded-xl saas-input text-xs"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 px-4 rounded-xl btn-saas-primary text-xs font-bold flex items-center justify-center space-x-2 disabled:opacity-50 mt-2"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : isRegisterMode ? (
              <>
                <UserPlus className="w-4 h-4" />
                <span>Create Citizen Account & Enter</span>
                <ArrowRight className="w-4 h-4" />
              </>
            ) : (
              <>
                <UserCheck className="w-4 h-4" />
                <span>Sign In & Auto-Route</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        {/* Divider */}
        <div className="relative flex items-center justify-center pt-2">
          <div className="border-t border-white/[0.08] w-full" />
          <span className="bg-saas-dark px-3 text-[10px] font-mono uppercase text-slate-500 shrink-0">
            Or test instantly with 1-click accounts
          </span>
          <div className="border-t border-white/[0.08] w-full" />
        </div>

        {/* Quick Demo Preset Accounts */}
        <div className="space-y-2">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {demoPresets.map((preset) => (
              <button
                key={preset.id}
                type="button"
                onClick={() => handlePresetLogin(preset)}
                disabled={isLoading}
                className="p-3 rounded-xl saas-card text-left transition-all group flex items-start space-x-2.5 hover:border-blue-500/50"
              >
                <span className="text-lg mt-0.5">{preset.icon}</span>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-1">
                    <p className="text-xs font-bold text-white group-hover:text-blue-300 transition-colors truncate">
                      {preset.badge}
                    </p>
                    <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded font-bold border ${
                      preset.isOfficial 
                        ? 'bg-amber-500/10 text-amber-300 border-amber-500/20' 
                        : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20'
                    }`}>
                      {preset.isOfficial ? 'Official' : 'Citizen'}
                    </span>
                  </div>
                  <p className="text-[10px] text-slate-400 truncate mt-0.5">
                    {preset.title.split('(')[0]}
                  </p>
                  <span className="text-[9px] text-blue-400 font-semibold block mt-1 group-hover:underline">
                    Click to Login →
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
};
