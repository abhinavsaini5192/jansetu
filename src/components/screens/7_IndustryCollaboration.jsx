import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useJanSetu } from '../../context/JanSetuContext';
import { useIndustryPartners } from '../../hooks/useIndustryPartners';
import { Badge } from '../common/Badge';
import { SkeletonCard } from '../states/SkeletonCard';
import { EmptyState } from '../states/EmptyState';
import { ErrorState } from '../states/ErrorState';
import { 
  Briefcase, 
  Handshake, 
  CheckCircle2, 
  ArrowRight, 
  UserCheck,
  Inbox,
  Loader2
} from 'lucide-react';

export const IndustryCollaboration = () => {
  const { activeProjectId, showToast } = useJanSetu();
  const { partners, loading, error, attachPartner, refetch } = useIndustryPartners();
  const navigate = useNavigate();

  const [attachingId, setAttachingId] = useState(null);

  const handleAttach = async (partner) => {
    if (!activeProjectId) {
      showToast("Please select an active project first from University Workspace.", "error");
      return;
    }

    setAttachingId(partner.id);
    try {
      await attachPartner(activeProjectId, partner.id, "CSR_GRANT_AND_MENTORSHIP");
      showToast(`Partnership agreement initiated with ${partner.name}.`, "success");
    } catch (err) {
      showToast(err.message || "Failed to initiate partnership.", "error");
    } finally {
      setAttachingId(null);
    }
  };

  const handleProceedToLifecycle = () => {
    navigate('/project-lifecycle');
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-panel p-6 rounded-3xl border border-purple-500/30">
        <div>
          <div className="flex items-center space-x-2">
            <Badge variant="purple">Screen 07 • Industry & CSR Collaboration</Badge>
            <span className="text-xs text-slate-400">Public-Private-Academic Alliance</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white mt-1 font-display">
            Industry Co-Funding, Hardware & Field Testing
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-xl">
            Bridge academic prototypes with corporate CSR grants, specialized edge hardware, and commercial scale-up networks.
          </p>
        </div>

        <button
          onClick={handleProceedToLifecycle}
          className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs flex items-center space-x-2 shadow-glow-sm"
        >
          <span>Track Lifecycle Milestones</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {loading ? (
        <div className="space-y-4">
          <SkeletonCard count={3} />
        </div>
      ) : error ? (
        <ErrorState
          title="Failed to Load Industry Partners"
          message={error}
          onRetry={refetch}
        />
      ) : partners.length === 0 ? (
        <EmptyState
          icon={Inbox}
          title="No Industry Partners Registered"
          description="There are currently no active corporate or CSR partners registered in this innovation category."
          actionLabel="View Platform Overview"
          actionTo="/"
        />
      ) : (
        <div className="space-y-6">
          {partners.map((ind) => (
            <div 
              key={ind.id}
              className="glass-card rounded-3xl p-6 sm:p-8 border border-navy-750 bg-navy-900/80 hover:border-purple-500/40 transition-all"
            >
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                
                <div className="space-y-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant="purple">CSR / Industry Partner</Badge>
                    {ind.headquarters && (
                      <span className="text-xs text-slate-400 font-mono">HQ: {ind.headquarters}</span>
                    )}
                    {ind.matchScore !== undefined && (
                      <span className="text-xs text-emerald-400 font-bold">{ind.matchScore}% Domain Fit</span>
                    )}
                  </div>

                  <h3 className="text-xl font-bold text-white font-display">
                    {ind.name}
                  </h3>

                  {Array.isArray(ind.focusAreas) && ind.focusAreas.length > 0 && (
                    <div className="flex flex-wrap gap-1.5">
                      {ind.focusAreas.map((f, idx) => (
                        <span key={idx} className="text-[11px] px-2.5 py-0.5 rounded-full bg-navy-800 text-slate-300 border border-navy-700">
                          {f}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Offered Support Chips */}
                  {Array.isArray(ind.offeredSupport) && ind.offeredSupport.length > 0 && (
                    <div className="pt-2 space-y-2">
                      <span className="text-xs font-semibold text-slate-300 block">Committed Support Offerings:</span>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                        {ind.offeredSupport.map((sup, idx) => (
                          <div key={idx} className="p-3 rounded-xl bg-navy-850 border border-navy-750 space-y-1">
                            <strong className="text-purple-400 block text-[11px] uppercase tracking-wider">{sup.type || "Support"}</strong>
                            <p className="text-slate-300 text-[11px]">{sup.details || sup}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Mentor details */}
                  {ind.mentor && (
                    <div className="p-3.5 rounded-xl bg-navy-850/80 border border-navy-700 flex items-center space-x-3 text-xs">
                      <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
                        <UserCheck className="w-5 h-5" />
                      </div>
                      <div>
                        <p className="text-slate-200 font-semibold">Assigned Mentor: {ind.mentor.name}</p>
                        <p className="text-slate-400 text-[11px]">{ind.mentor.title} {ind.mentor.organization ? `• ${ind.mentor.organization}` : ""}</p>
                      </div>
                    </div>
                  )}

                </div>

                {/* Right Action Column */}
                <div className="flex flex-col items-start lg:items-end justify-between gap-4 shrink-0 pt-4 lg:pt-0 border-t lg:border-t-0 border-navy-800">
                  <button
                    onClick={() => handleAttach(ind)}
                    disabled={attachingId === ind.id}
                    className="w-full sm:w-auto px-6 py-3 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs flex items-center justify-center space-x-2 shadow-glow-sm transition-transform hover:scale-105 disabled:opacity-50"
                  >
                    {attachingId === ind.id ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Connecting...</span>
                      </>
                    ) : (
                      <>
                        <Handshake className="w-4 h-4" />
                        <span>Request Partnership</span>
                      </>
                    )}
                  </button>
                </div>

              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
};
