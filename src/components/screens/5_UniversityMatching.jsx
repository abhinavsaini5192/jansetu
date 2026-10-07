import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useJanSetu } from '../../context/JanSetuContext';
import { useChallenge } from '../../hooks/useChallenge';
import { useUniversityMatches } from '../../hooks/useUniversityMatches';
import { Badge } from '../common/Badge';
import { SkeletonCard } from '../states/SkeletonCard';
import { EmptyState } from '../states/EmptyState';
import { ErrorState } from '../states/ErrorState';
import { 
  GraduationCap, 
  MapPin, 
  ArrowRight, 
  Sliders,
  ChevronDown,
  ChevronUp,
  Inbox,
  Loader2
} from 'lucide-react';

export const UniversityMatching = () => {
  const { activeChallengeId, showToast } = useJanSetu();
  const [searchParams] = useSearchParams();
  const challengeId = searchParams.get('id') || activeChallengeId;

  const { challenge } = useChallenge(challengeId);
  const { matches, loading, error, assignUniversity, refetch } = useUniversityMatches(challengeId);
  const navigate = useNavigate();

  const [expandedId, setExpandedId] = useState(null);
  const [isAssigning, setIsAssigning] = useState(false);

  if (!challengeId) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16">
        <EmptyState
          icon={GraduationCap}
          title="No Challenge Selected"
          description="Select a validated challenge to inspect institutional matching and research lab recommendations."
          actionLabel="View Validation Queue"
          actionTo="/government-dashboard"
        />
      </div>
    );
  }

  const handleAssign = async (uni) => {
    setIsAssigning(true);
    try {
      await assignUniversity(uni.id || uni.universityId);
      showToast(`Challenge successfully assigned to ${uni.name}.`, "success");
      navigate('/university-workspace');
    } catch (err) {
      showToast(err.message || "Failed to assign challenge to university.", "error");
    } finally {
      setIsAssigning(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-panel p-6 rounded-3xl border border-teal-500/30">
        <div>
          <div className="flex items-center space-x-2">
            <Badge variant="teal">Screen 05 • Explainable AI Matching Engine</Badge>
            <span className="text-xs text-slate-400 font-mono">{challenge?.id || challengeId}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white mt-1 font-display">
            Institutional & Laboratory Matching
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Multi-dimensional matching based on domain expertise, faculty publications, accredited labs, student technical track record, and field proximity.
          </p>
        </div>
      </div>

      {/* Target Challenge Summary */}
      {challenge && (
        <div className="glass-card rounded-2xl p-5 border border-navy-750 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Validated Challenge for Solver Pairing</span>
            <h3 className="text-base font-bold text-white mt-0.5">{challenge.title}</h3>
            <p className="text-xs text-slate-400">
              Location: <span className="text-white">{challenge.location?.district || "Jharkhand"}</span> • Domain: <span className="text-teal-400">{challenge.domain}</span>
            </p>
          </div>
          <Badge variant="primary">{challenge.id}</Badge>
        </div>
      )}

      {/* Matching Results List */}
      {loading ? (
        <div className="space-y-4">
          <SkeletonCard count={3} />
        </div>
      ) : error ? (
        <ErrorState
          title="Failed to Load Institutional Recommendations"
          message={error}
          onRetry={refetch}
        />
      ) : matches.length === 0 ? (
        <EmptyState
          icon={Inbox}
          title="No University Matches Found"
          description="There are currently no registered Higher Education Institutions with capacity matching this specific challenge domain."
          actionLabel="Browse All Universities"
          actionTo="/universities"
        />
      ) : (
        <div className="space-y-6">
          {matches.map((uni, index) => {
            const isExpanded = expandedId === (uni.id || uni.universityId);
            const uniId = uni.id || uni.universityId;

            return (
              <div 
                key={uniId || index}
                className="glass-card rounded-3xl border border-navy-750 bg-navy-900/80 hover:border-teal-500/40 transition-all overflow-hidden"
              >
                <div className="p-6 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                  
                  <div className="space-y-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-xs font-mono font-bold text-slate-400">Rank #{index + 1}</span>
                      {uni.badge && <Badge variant="teal">{uni.badge}</Badge>}
                      {uni.location && (
                        <span className="text-xs text-slate-400 flex items-center space-x-1">
                          <MapPin className="w-3 h-3 text-slate-400" />
                          <span>{uni.location} {uni.distanceKm ? `(${uni.distanceKm} km away)` : ""}</span>
                        </span>
                      )}
                    </div>

                    <h3 className="text-xl font-bold text-white font-display">
                      {uni.name}
                    </h3>
                    
                    <p className="text-xs text-slate-400">
                      {uni.type || "Higher Education Institution"} 
                      {uni.accreditation && <span> • Accreditation: <strong className="text-slate-300">{uni.accreditation}</strong></span>}
                    </p>

                    {Array.isArray(uni.strengths) && uni.strengths.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {uni.strengths.map((str, i) => (
                          <span key={i} className="text-[11px] px-2.5 py-0.5 rounded-full bg-navy-800 text-slate-300 border border-navy-700">
                            {str}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Match Score & Action */}
                  <div className="flex items-center lg:flex-col lg:items-end justify-between gap-3 pt-3 lg:pt-0 border-t lg:border-t-0 border-navy-800">
                    <div className="text-left lg:text-right">
                      <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block">AI Match Index</span>
                      <span className="text-3xl font-black font-display text-teal-400">
                        {uni.overallMatch !== undefined ? `${uni.overallMatch}%` : "—"}
                      </span>
                    </div>

                    <div className="flex items-center space-x-2">
                      {uni.explainableFactors && (
                        <button
                          onClick={() => setExpandedId(isExpanded ? null : uniId)}
                          className="px-3 py-2 rounded-xl bg-navy-800 hover:bg-navy-750 text-slate-300 text-xs font-semibold flex items-center space-x-1"
                        >
                          <span>Explainability</span>
                          {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                        </button>
                      )}

                      <button
                        onClick={() => handleAssign(uni)}
                        disabled={isAssigning}
                        className="px-5 py-2 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs flex items-center space-x-2 transition-all disabled:opacity-50"
                      >
                        {isAssigning ? (
                          <>
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                            <span>Assigning...</span>
                          </>
                        ) : (
                          <>
                            <span>Assign Mandate</span>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </>
                        )}
                      </button>
                    </div>
                  </div>

                </div>

                {/* Explainable Factor Details */}
                {isExpanded && uni.explainableFactors && (
                  <div className="p-6 bg-navy-950/70 border-t border-navy-800 space-y-4">
                    <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center space-x-1.5">
                      <Sliders className="w-3.5 h-3.5 text-teal-400" />
                      <span>Explainable Matching Rationale</span>
                    </h4>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                      {Object.entries(uni.explainableFactors).map(([k, factor]) => {
                        if (!factor || typeof factor !== 'object') return null;
                        return (
                          <div key={k} className="p-3.5 rounded-2xl bg-navy-850/80 border border-navy-700/80 space-y-1.5">
                            <div className="flex items-center justify-between text-xs">
                              <span className="font-semibold text-slate-300">{factor.label || k}</span>
                              {factor.score !== undefined && (
                                <span className="font-bold text-teal-400 font-mono">{factor.score}%</span>
                              )}
                            </div>
                            {factor.reason && (
                              <p className="text-[11px] text-slate-400 leading-relaxed">
                                {factor.reason}
                              </p>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

              </div>
            );
          })}
        </div>
      )}

    </div>
  );
};
