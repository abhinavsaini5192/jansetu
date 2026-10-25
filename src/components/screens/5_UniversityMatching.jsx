import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useJanSetu } from '../../context/JanSetuContext';
import { useAuth } from '../../context/AuthContext';
import { useChallenge } from '../../hooks/useChallenge';
import { useUniversityMatches } from '../../hooks/useUniversityMatches';
import { universityService } from '../../services/universityService';
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
  Loader2,
  CheckCircle2,
  Send,
  Building2,
  Sparkles,
  Users,
  BookOpen,
  X,
  FileCheck2,
  ExternalLink
} from 'lucide-react';

export const UniversityMatching = () => {
  const { activeChallengeId, setActiveChallengeId, setActiveProjectId, showToast } = useJanSetu();
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const challengeId = searchParams.get('id') || activeChallengeId || 'c-arsenic-ranchi';
  const { challenge } = useChallenge(challengeId);
  const { matches, adoptedBy, loading, error, adoptChallenge, sendRecommendationInvite, refetch } = useUniversityMatches(challengeId);

  // University Affiliation Discovery
  const userUniversityId = user?.universityId || (user?.email?.includes("bit") ? "uni-bit-mesra" : "uni-bit-mesra");
  const userUniversityName = user?.universityName || "Birla Institute of Technology (BIT) Mesra";
  const isUniversityPersona = user?.role === 'FACULTY' || user?.role === 'UNIVERSITY' || user?.role === 'RESEARCHER' || Boolean(user?.universityId);

  const [activeTab, setActiveTab] = useState(isUniversityPersona ? 'recommended_for_you' : 'challenge_matches');
  const [expandedId, setExpandedId] = useState(null);
  
  // Recommendations feed for university users
  const [universityRecommendations, setUniversityRecommendations] = useState([]);
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);

  // Adoption modal state
  const [adoptingChallenge, setAdoptingChallenge] = useState(null);
  const [targetUniId, setTargetUniId] = useState(userUniversityId);
  const [adoptForm, setAdoptForm] = useState({
    name: "",
    leadFaculty: user?.full_name || "Dr. Alok Kumar",
    studentLead: "Rahul Sharma (Lead Student Researcher)",
    summary: ""
  });
  const [isSubmittingAdoption, setIsSubmittingAdoption] = useState(false);
  const [invitingId, setInvitingId] = useState(null);

  // Load recommendations for user's university
  useEffect(() => {
    const loadUniRecs = async () => {
      if (!userUniversityId) return;
      setLoadingRecommendations(true);
      try {
        const recs = await universityService.getRecommendedChallengesForUniversity(userUniversityId);
        setUniversityRecommendations(recs);
      } catch (e) {
        console.warn("Failed loading university recommendations:", e);
      } finally {
        setLoadingRecommendations(false);
      }
    };

    loadUniRecs();
  }, [userUniversityId]);

  const handleOpenAdoptionModal = (ch, uniId = userUniversityId) => {
    setAdoptingChallenge(ch);
    setTargetUniId(uniId);
    setAdoptForm({
      name: `${userUniversityName} - ${ch.title || 'Civic Research Prototype'}`,
      leadFaculty: user?.full_name || "Dr. Alok Kumar",
      studentLead: "Rahul Sharma (Lead Student Researcher)",
      summary: `Autonomous university research initiative to address '${ch.title}' utilizing accredited laboratory facilities and multidisciplinary student innovators.`
    });
  };

  const handleConfirmAdoption = async (e) => {
    e.preventDefault();
    if (!adoptingChallenge || !targetUniId) return;

    setIsSubmittingAdoption(true);
    try {
      const res = await adoptChallenge(targetUniId, adoptForm, user);
      showToast(res?.message || "Challenge successfully adopted by your university!", "success");
      
      const chId = adoptingChallenge.id || adoptingChallenge.challengeId;
      setActiveChallengeId(chId);
      if (res?.project?.id) {
        setActiveProjectId(res.project.id);
      }

      setAdoptingChallenge(null);
      await refetch();
      // Route directly into active University Workspace
      navigate('/university-workspace');
    } catch (err) {
      showToast(err.message || "Failed to record challenge adoption.", "error");
    } finally {
      setIsSubmittingAdoption(false);
    }
  };

  const handleSendInvite = async (uni) => {
    const uniId = uni.id || uni.universityId;
    setInvitingId(uniId);
    try {
      const res = await sendRecommendationInvite(uniId, `Government Nodal Outreach for ${challenge?.title}`);
      showToast(res.message, "success");
      await refetch();
    } catch (err) {
      showToast(err.message || "Failed to dispatch recommendation.", "error");
    } finally {
      setInvitingId(null);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-in fade-in">
      
      {/* Top Header */}
      <div className="saas-panel p-6 sm:p-8 rounded-3xl relative overflow-hidden space-y-4">
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-teal-500 via-cyan-400 to-blue-500" />
        
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center space-x-2">
              <Badge variant="teal" dot={true}>
                AUTONOMOUS UNIVERSITY ADOPTION ENGINE
              </Badge>
              <span className="text-xs text-slate-400 font-mono">No Forced Mandates • Pure Academic Freedom</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-white font-display tracking-tight">
              University Recommendations & Adoption
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 max-w-3xl leading-relaxed">
              Higher Education Institutions are autonomous research centers. JanSetu AI recommends validated grassroots problems based on faculty research, accredited laboratories, and domain track record. Faculty and student teams review recommendations and voluntarily adopt challenges they wish to solve.
            </p>
          </div>

          {/* Affiliated University Badge */}
          <div className="p-3.5 rounded-2xl bg-saas-card/70 border border-white/[0.08] text-right shrink-0">
            <p className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Your Institution</p>
            <p className="text-xs font-bold text-teal-300">{userUniversityName}</p>
            <p className="text-[11px] text-slate-400">{user?.full_name || "Autonomous Researcher"}</p>
          </div>
        </div>

        {/* View Switcher Tabs */}
        <div className="flex items-center space-x-2 pt-2 border-t border-white/[0.07]">
          <button
            onClick={() => setActiveTab('recommended_for_you')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center space-x-2 transition-all ${
              activeTab === 'recommended_for_you'
                ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40 shadow-glow-sm'
                : 'text-slate-400 hover:text-white bg-saas-card/40 border border-white/[0.06]'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-teal-400" />
            <span>Recommended for Your University ({universityRecommendations.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('challenge_matches')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center space-x-2 transition-all ${
              activeTab === 'challenge_matches'
                ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40 shadow-glow-sm'
                : 'text-slate-400 hover:text-white bg-saas-card/40 border border-white/[0.06]'
            }`}
          >
            <Building2 className="w-3.5 h-3.5 text-indigo-400" />
            <span>Browse All Institution Matches for Current Challenge</span>
          </button>
        </div>
      </div>

      {/* TAB 1: RECOMMENDED FOR YOUR UNIVERSITY */}
      {activeTab === 'recommended_for_you' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-white flex items-center space-x-2">
                <span>Tailored Recommendations for</span>
                <span className="text-teal-400 underline decoration-teal-500/40 underline-offset-4">{userUniversityName}</span>
              </h2>
              <p className="text-xs text-slate-400">
                Ranked by AI capability alignment with your accredited NABL testing labs and faculty publications.
              </p>
            </div>
            <span className="text-[11px] font-mono text-slate-500">Autonomous Adoption Enabled</span>
          </div>

          {loadingRecommendations ? (
            <SkeletonCard count={3} />
          ) : universityRecommendations.length === 0 ? (
            <EmptyState
              icon={GraduationCap}
              title="No Recommendations Currently Available"
              description="Check back shortly as new grassroots challenges are verified by district authorities."
              actionLabel="View All Challenges"
              actionTo="/problems"
            />
          ) : (
            <div className="grid grid-cols-1 gap-5">
              {universityRecommendations.map((rec, idx) => {
                const ch = rec.challenge;
                const chId = ch.id || ch.challengeId;
                const isAdoptedByYou = rec.isAdoptedByYou;
                const isAdoptedByOther = rec.isAdoptedByOther;

                return (
                  <div 
                    key={chId || idx}
                    className="saas-card rounded-2xl border border-white/[0.08] p-6 space-y-5 hover:border-teal-500/30 transition-all relative overflow-hidden group"
                  >
                    {/* Top Specular Line */}
                    <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-teal-500/60 via-cyan-400/40 to-transparent" />

                    <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-5">
                      <div className="space-y-2.5 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="text-[11px] font-mono font-bold text-teal-400 bg-teal-500/10 px-2.5 py-0.5 rounded-full border border-teal-500/30">
                            {rec.matchScore}% Match Index
                          </span>
                          <span className="text-xs text-slate-400 flex items-center space-x-1">
                            <MapPin className="w-3.5 h-3.5 text-rose-400" />
                            <span>{ch.location?.district || "Jharkhand"}</span>
                          </span>
                          <Badge variant="blue" dot={true}>
                            {ch.domain || "General Domain"}
                          </Badge>
                          {isAdoptedByYou && (
                            <span className="text-[11px] font-semibold text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/30 flex items-center space-x-1">
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              <span>Adopted by Your University</span>
                            </span>
                          )}
                          {isAdoptedByOther && (
                            <span className="text-[11px] text-slate-400 bg-white/[0.04] px-2.5 py-0.5 rounded-full border border-white/[0.08]">
                              Adopted by {rec.adoptionDetails?.universityName || "Other HEI"}
                            </span>
                          )}
                        </div>

                        <h3 className="text-lg font-bold text-white group-hover:text-teal-300 transition-colors font-display">
                          {ch.title}
                        </h3>

                        <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">
                          {ch.description}
                        </p>

                        {/* Explainable Match Reason */}
                        <div className="p-3 rounded-xl bg-saas-dark/60 border border-white/[0.06] text-xs text-slate-300 space-y-1">
                          <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-teal-400 block">
                            Why JanSetu AI Recommends this to {userUniversityName}:
                          </span>
                          <p className="text-[11px] text-slate-300">
                            High alignment with your environmental engineering facilities, chemical chromatography testing capacity, and proximity to {ch.location?.district || "the field"}.
                          </p>
                        </div>
                      </div>

                      {/* Action Box */}
                      <div className="flex flex-col sm:flex-row lg:flex-col items-stretch sm:items-center lg:items-end justify-center gap-3 shrink-0">
                        {isAdoptedByYou ? (
                          <button
                            onClick={() => {
                              setActiveChallengeId(chId);
                              navigate('/university-workspace');
                            }}
                            className="btn-saas-teal text-xs py-2.5 px-5 flex items-center justify-center space-x-2"
                          >
                            <BookOpen className="w-4 h-4" />
                            <span>Open Active Workspace</span>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </button>
                        ) : isAdoptedByOther ? (
                          <div className="text-center sm:text-right">
                            <span className="text-xs text-slate-500 block">Adopted by Peer HEI</span>
                            <button
                              onClick={() => navigate(`/problems?id=${chId}`)}
                              className="btn-saas-secondary text-xs mt-1 px-3 py-1.5 rounded-lg inline-flex items-center space-x-1"
                            >
                              <span>View Dossier</span>
                            </button>
                          </div>
                        ) : (
                          <div className="space-y-2 w-full sm:w-auto">
                            <button
                              onClick={() => handleOpenAdoptionModal(ch, userUniversityId)}
                              className="btn-saas-primary text-xs py-2.5 px-5 w-full flex items-center justify-center space-x-2 rounded-xl"
                            >
                              <FileCheck2 className="w-4 h-4 text-emerald-300" />
                              <span>Adopt Problem Statement</span>
                              <ArrowRight className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => navigate(`/problems?id=${chId}`)}
                              className="btn-saas-secondary text-xs w-full py-2 px-3 rounded-xl flex items-center justify-center space-x-1 text-slate-300 hover:text-white"
                            >
                              <span>Inspect Field Details</span>
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: ALL INSTITUTION MATCHES FOR CURRENT CHALLENGE */}
      {activeTab === 'challenge_matches' && (
        <div className="space-y-6">
          {/* Target Challenge Summary */}
          {challenge && (
            <div className="saas-card rounded-2xl p-5 border border-white/[0.08] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="space-y-1">
                <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Inspecting Civic Challenge</span>
                <h3 className="text-base font-bold text-white">{challenge.title}</h3>
                <p className="text-xs text-slate-400">
                  Location: <span className="text-slate-200">{challenge.location?.district || "Jharkhand"}</span> • Domain: <span className="text-teal-400 font-medium">{challenge.domain}</span>
                </p>
              </div>
              <div className="flex items-center space-x-2">
                {adoptedBy ? (
                  <span className="text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/30 flex items-center space-x-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Adopted by {adoptedBy}</span>
                  </span>
                ) : (
                  <Badge variant="teal" dot={true}>Open for University Adoption</Badge>
                )}
              </div>
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
            <div className="space-y-5">
              {matches.map((uni, index) => {
                const isExpanded = expandedId === (uni.id || uni.universityId);
                const uniId = uni.id || uni.universityId;
                const isAdoptedByThis = uni.isAdopted;
                const isInvited = uni.isInvited;

                return (
                  <div 
                    key={uniId || index}
                    className={`saas-card rounded-2xl border transition-all group ${
                      isAdoptedByThis 
                        ? 'border-emerald-500/40 bg-emerald-500/[0.02]' 
                        : 'border-white/[0.08]'
                    }`}
                  >
                    <div className="p-6 flex flex-col lg:flex-row lg:items-center justify-between gap-5">
                      
                      <div className="space-y-2.5">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="text-[11px] font-mono font-bold text-slate-400 bg-black/40 px-2 py-0.5 rounded-lg border border-white/[0.08]">
                            AI Rank #{index + 1}
                          </span>
                          {uni.badge && <Badge variant="teal" dot={true}>{uni.badge}</Badge>}
                          {isAdoptedByThis && (
                            <span className="text-[11px] font-bold text-emerald-400 bg-emerald-500/15 px-2.5 py-0.5 rounded-full border border-emerald-500/30 flex items-center space-x-1">
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              <span>Voluntarily Adopted</span>
                            </span>
                          )}
                          {isInvited && !isAdoptedByThis && (
                            <span className="text-[11px] text-indigo-300 bg-indigo-500/15 px-2.5 py-0.5 rounded-full border border-indigo-500/30">
                              Recommendation Dispatched
                            </span>
                          )}
                          {uni.location && (
                            <span className="text-xs text-slate-400 flex items-center space-x-1">
                              <MapPin className="w-3.5 h-3.5 text-slate-400" />
                              <span>{uni.location} {uni.distanceKm ? `(${uni.distanceKm} km away)` : ""}</span>
                            </span>
                          )}
                        </div>

                        <h3 className="text-xl font-bold text-white group-hover:text-teal-300 transition-colors font-display">
                          {uni.name}
                        </h3>
                        
                        <p className="text-xs text-slate-400">
                          {uni.type || "Higher Education Institution"} 
                          {uni.accreditation && <span> • Accreditation: <strong className="text-slate-300 font-semibold">{uni.accreditation}</strong></span>}
                        </p>

                        {Array.isArray(uni.strengths) && uni.strengths.length > 0 && (
                          <div className="flex flex-wrap gap-1.5 pt-1">
                            {uni.strengths.map((str, i) => (
                              <span key={i} className="text-[11px] px-2.5 py-0.5 rounded-full bg-white/[0.04] text-slate-300 border border-white/[0.06]">
                                {str}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Match Score & Action */}
                      <div className="flex items-center lg:flex-col lg:items-end justify-between gap-4 pt-4 lg:pt-0 border-t lg:border-t-0 border-white/[0.08]">
                        <div className="text-left lg:text-right">
                          <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block font-mono">AI Capability Match</span>
                          <span className="text-3xl font-black font-mono text-teal-400 tracking-tight">
                            {uni.overallMatch !== undefined ? `${uni.overallMatch}%` : "—"}
                          </span>
                        </div>

                        <div className="flex items-center space-x-2">
                          {uni.explainableFactors && (
                            <button
                              onClick={() => setExpandedId(isExpanded ? null : uniId)}
                              className="px-3.5 py-2 rounded-xl btn-saas-secondary text-xs font-semibold flex items-center space-x-1"
                            >
                              <span>Explainability</span>
                              {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                            </button>
                          )}

                          {isAdoptedByThis ? (
                            <button
                              onClick={() => {
                                setActiveChallengeId(challengeId);
                                navigate('/university-workspace');
                              }}
                              className="btn-saas-teal text-xs py-2 px-4 flex items-center space-x-1.5"
                            >
                              <BookOpen className="w-3.5 h-3.5" />
                              <span>View Workspace</span>
                            </button>
                          ) : (
                            <div className="flex items-center space-x-2">
                              {/* Send Official Recommendation Invitation (Govt) */}
                              <button
                                onClick={() => handleSendInvite(uni)}
                                disabled={invitingId === uniId}
                                title="Send official recommendation notice inviting this university to evaluate and adopt"
                                className="btn-saas-secondary text-xs py-2 px-3 flex items-center space-x-1"
                              >
                                {invitingId === uniId ? (
                                  <Loader2 className="w-3 h-3 animate-spin text-teal-400" />
                                ) : (
                                  <Send className="w-3 h-3 text-indigo-400" />
                                )}
                                <span>{isInvited ? "Re-invite" : "Invite to Adopt"}</span>
                              </button>

                              {/* University Autonomous Adoption Button */}
                              <button
                                onClick={() => handleOpenAdoptionModal(challenge, uniId)}
                                className="btn-saas-primary text-xs py-2 px-4 flex items-center space-x-1.5"
                              >
                                <FileCheck2 className="w-3.5 h-3.5 text-emerald-300" />
                                <span>Adopt Challenge</span>
                              </button>
                            </div>
                          )}
                        </div>
                      </div>

                    </div>

                    {/* Explainable Factor Details */}
                    {isExpanded && uni.explainableFactors && (
                      <div className="p-6 bg-black/40 border-t border-white/[0.08] space-y-4">
                        <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center space-x-1.5">
                          <Sliders className="w-3.5 h-3.5 text-teal-400" />
                          <span>Explainable Matching Rationale</span>
                        </h4>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                          {Object.entries(uni.explainableFactors).map(([k, factor]) => {
                            if (!factor || typeof factor !== 'object') return null;
                            return (
                              <div key={k} className="p-4 rounded-xl saas-card space-y-2">
                                <div className="flex items-center justify-between text-xs">
                                  <span className="font-semibold text-slate-200">{factor.label || k}</span>
                                  {factor.score !== undefined && (
                                    <span className="font-bold text-teal-400 font-mono">{factor.score}%</span>
                                  )}
                                </div>
                                {factor.score !== undefined && (
                                  <div className="w-full h-1.5 rounded-full bg-white/[0.06] overflow-hidden">
                                    <div 
                                      className="h-full bg-gradient-to-r from-teal-500 to-cyan-400 rounded-full" 
                                      style={{ width: `${Math.min(100, Math.max(0, factor.score))}%` }} 
                                    />
                                  </div>
                                )}
                                {factor.reason && (
                                  <p className="text-[11px] text-slate-400 leading-relaxed font-normal">
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
      )}

      {/* ADOPTION MODAL: VOLUNTARY COMMITMENT BY UNIVERSITY */}
      {adoptingChallenge && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in">
          <div className="saas-panel max-w-xl w-full p-6 sm:p-8 rounded-3xl border border-teal-500/40 space-y-6 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-teal-500 via-emerald-400 to-cyan-500" />
            
            <div className="flex items-center justify-between border-b border-white/[0.08] pb-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-teal-500/20 border border-teal-500/40 flex items-center justify-center text-teal-300">
                  <FileCheck2 className="w-5 h-5" />
                </div>
                <div>
                  <span className="text-[10px] font-mono uppercase tracking-wider text-teal-400 font-bold block">
                    VOLUNTARY INSTITUTIONAL ADOPTION
                  </span>
                  <h3 className="text-base font-bold text-white">
                    Adopt Problem Statement & Start Project
                  </h3>
                </div>
              </div>
              <button
                onClick={() => setAdoptingChallenge(null)}
                className="w-8 h-8 rounded-lg hover:bg-white/[0.08] text-slate-400 hover:text-white flex items-center justify-center transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleConfirmAdoption} className="space-y-4">
              <div className="p-3.5 rounded-xl bg-saas-dark/70 border border-white/[0.06] text-xs space-y-1">
                <span className="text-slate-400 text-[10px] font-mono uppercase block">Target Grassroots Challenge</span>
                <p className="font-bold text-white text-sm">{adoptingChallenge.title}</p>
                <p className="text-slate-400 text-[11px]">
                  District: {adoptingChallenge.location?.district || "Jharkhand"} • Beneficiaries: {adoptingChallenge.affectedPopulation || "~4,500 residents"}
                </p>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300 block">
                  Project Workspace Title *
                </label>
                <input
                  type="text"
                  required
                  value={adoptForm.name}
                  onChange={e => setAdoptForm({ ...adoptForm, name: e.target.value })}
                  className="saas-input text-xs"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-300 block">
                    Lead Faculty / Principal Investigator *
                  </label>
                  <input
                    type="text"
                    required
                    value={adoptForm.leadFaculty}
                    onChange={e => setAdoptForm({ ...adoptForm, leadFaculty: e.target.value })}
                    className="saas-input text-xs"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-300 block">
                    Student Research Lead *
                  </label>
                  <input
                    type="text"
                    required
                    value={adoptForm.studentLead}
                    onChange={e => setAdoptForm({ ...adoptForm, studentLead: e.target.value })}
                    className="saas-input text-xs"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300 block">
                  Proposed Solution & Methodology Outline
                </label>
                <textarea
                  rows={3}
                  value={adoptForm.summary}
                  onChange={e => setAdoptForm({ ...adoptForm, summary: e.target.value })}
                  placeholder="Outline the planned lab experiments, prototype development, or field trials..."
                  className="saas-input text-xs leading-relaxed"
                />
              </div>

              <div className="flex items-center justify-end space-x-3 pt-3 border-t border-white/[0.08]">
                <button
                  type="button"
                  onClick={() => setAdoptingChallenge(null)}
                  className="btn-saas-secondary text-xs px-4 py-2 rounded-xl font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingAdoption}
                  className="btn-saas-teal text-xs py-2 px-5 flex items-center space-x-2"
                >
                  {isSubmittingAdoption ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      <span>Initializing Project Workspace...</span>
                    </>
                  ) : (
                    <>
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Confirm Adoption & Launch Project</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};
