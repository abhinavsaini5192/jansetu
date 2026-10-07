import React, { createContext, useContext, useState } from 'react';
import confetti from 'canvas-confetti';
import { LIFECYCLE_STAGES } from '../config/lifecycleStatuses';

const JanSetuContext = createContext();

export const STAGES = LIFECYCLE_STAGES;

export const JanSetuProvider = ({ children }) => {
  const [language, setLanguage] = useState('en'); // 'en' | 'hi'
  
  // Selected challenge ID across workflow views (null if none selected)
  const [activeChallengeId, setActiveChallengeId] = useState(() => {
    return localStorage.getItem('jansetu_active_challenge_id') || null;
  });

  // Selected project ID across workflow views
  const [activeProjectId, setActiveProjectId] = useState(() => {
    return localStorage.getItem('jansetu_active_project_id') || null;
  });

  // Global toast messages
  const [toasts, setToasts] = useState([]);

  const setChallengeId = (id) => {
    setActiveChallengeId(id);
    if (id) {
      localStorage.setItem('jansetu_active_challenge_id', id);
    } else {
      localStorage.removeItem('jansetu_active_challenge_id');
    }
  };

  const setProjectId = (id) => {
    setActiveProjectId(id);
    if (id) {
      localStorage.setItem('jansetu_active_project_id', id);
    } else {
      localStorage.removeItem('jansetu_active_project_id');
    }
  };

  const showToast = (message, type = "info") => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 4500);
  };

  // Celebration confetti effect for milestone or verification success
  const triggerConfetti = () => {
    try {
      confetti({
        particleCount: 120,
        spread: 80,
        origin: { y: 0.6 },
        colors: ['#10B981', '#3B82F6', '#6366F1', '#F59E0B']
      });
    } catch (e) {
      console.warn("Confetti effect skipped", e);
    }
  };

  return (
    <JanSetuContext.Provider value={{
      language,
      setLanguage,
      activeChallengeId,
      setActiveChallengeId: setChallengeId,
      activeProjectId,
      setActiveProjectId: setProjectId,
      stages: LIFECYCLE_STAGES,
      toasts,
      showToast,
      triggerConfetti,
    }}>
      {children}
      
      {/* Toast Alert Container */}
      {toasts.length > 0 && (
        <div className="fixed top-20 right-4 z-50 space-y-2 max-w-sm pointer-events-none">
          {toasts.map(toast => (
            <div
              key={toast.id}
              className={`p-3 rounded-xl border text-xs shadow-2xl backdrop-blur-md pointer-events-auto transition-all animate-in fade-in slide-in-from-right-2 ${
                toast.type === 'success'
                  ? 'bg-emerald-950/90 border-emerald-500/40 text-emerald-200'
                  : toast.type === 'error'
                  ? 'bg-rose-950/90 border-rose-500/40 text-rose-200'
                  : 'bg-navy-900/90 border-blue-500/40 text-blue-200'
              }`}
            >
              {toast.message}
            </div>
          ))}
        </div>
      )}
    </JanSetuContext.Provider>
  );
};

export const useJanSetu = () => {
  const context = useContext(JanSetuContext);
  if (!context) {
    throw new Error("useJanSetu must be used within a JanSetuProvider");
  }
  return context;
};
