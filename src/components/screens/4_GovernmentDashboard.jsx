import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useJanSetu } from '../../context/JanSetuContext';
import { useGovernmentQueue } from '../../hooks/useGovernmentQueue';
import { Badge } from '../common/Badge';
import { StatCard } from '../common/StatCard';
import { LoadingState } from '../states/LoadingState';
import { EmptyState } from '../states/EmptyState';
import { ErrorState } from '../states/ErrorState';
import { SkeletonCard } from '../states/SkeletonCard';
import { 
  ShieldCheck, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  MapPin, 
  Users, 
  Building2, 
  ArrowRight, 
  Filter, 
  FileCheck,
  Inbox,
  Loader2,
  Calendar,
  Sparkles,
  Search,
  CheckCircle,
  FileText
} from 'lucide-react';
import { getStatusDetails } from '../../config/lifecycleStatuses';

export const GovernmentDashboard = () => {
  const { setActiveChallengeId, showToast } = useJanSetu();
  const { queue, loading, error, validate, reject, refetch } = useGovernmentQueue();
  const navigate = useNavigate();

  const [selectedChallengeId, setSelectedChallengeId] = useState(null);
  const [selectedDepartment, setSelectedDepartment] = useState("Dept of Higher & Technical Education");
  const [officialNotes, setOfficialNotes] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [queueFilter, setQueueFilter] = useState("");

  // Active challenge selected for review
  const activeChallenge = queue.find(c => c.id === selectedChallengeId) || queue[0] || null;

  const handleSelectChallenge = (chal) => {
    setSelectedChallengeId(chal.id);
    setActiveChallengeId(chal.id);
  };

  const handleValidate = async () => {
    if (!activeChallenge?.id) return;
    setIsProcessing(true);
    try {
      await validate(activeChallenge.id, {
        remarks: officialNotes || "Validated by Government Nodal Authority.",
        department: selectedDepartment,
      });
      showToast("Challenge officially validated and forwarded to University Matching.", "success");
      setOfficialNotes("");
    } catch (err) {
      showToast(err.message || "Failed to validate challenge.", "error");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReject = async () => {
    if (!activeChallenge?.id) return;
    setIsProcessing(true);
    try {
      await reject(activeChallenge.id, {
        reason: officialNotes || "Out of institutional scope or duplicate report.",
      });
      showToast("Challenge rejected / marked closed.", "info");
      setOfficialNotes("");
    } catch (err) {
      showToast(err.message || "Failed to update challenge.", "error");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleProceedToMatching = (chalId) => {
    setActiveChallengeId(chalId);
    navigate('/university-matching');
  };

  const filteredQueue = queue.filter(item => {
    if (!queueFilter.trim()) return true;
    const q = queueFilter.toLowerCase();
    return (
      (item.title || "").toLowerCase().includes(q) ||
      (item.id || "").toLowerCase().includes(q) ||
      (item.location?.district || "").toLowerCase().includes(q)
    );
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-in fade-in">
      
      {/* Top Header Command Banner */}
      <div className="saas-panel p-6 sm:p-8 rounded-3xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-blue-500 via-indigo-500 to-teal-400" />

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30 flex items-center space-x-1.5 shadow-[0_0_10px_rgba(245,158,11,0.15)]">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse"></span>
                <span>Screen 04 • Government Administration</span>
              </span>
              <span className="text-xs text-slate-400">Govt of Jharkhand Nodal Portal</span>
            </div>

            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-black text-white font-display tracking-tight">
              Validation Queue & University Outreach
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
              Authorize crowdsourced community reports, verify ground truth with district nodal officers, and recommend challenges to accredited Higher Education Institutions (HEIs) for voluntary adoption.
            </p>
          </div>

          {activeChallenge && activeChallenge.status !== 'SUBMITTED' && (
            <button
              onClick={() => handleProceedToMatching(activeChallenge.id)}
              className="btn-saas-teal px-5 py-3 rounded-2xl text-xs font-bold flex items-center space-x-2 shrink-0 self-start md:self-center"
            >
              <Sparkles className="w-4 h-4" />
              <span>Recommend to Universities</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <SkeletonCard count={2} />
          </div>
          <div>
            <SkeletonCard count={3} />
          </div>
        </div>
      ) : error ? (
        <ErrorState
          title="Failed to Load Validation Queue"
          message={error}
          onRetry={refetch}
        />
      ) : queue.length === 0 ? (
        <EmptyState
          icon={Inbox}
          title="Validation Queue Empty"
          description="There are currently no community challenges pending government review or verification."
          actionLabel="View Platform Challenges"
          actionTo="/"
        />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Main Inspection View for Active Challenge (Left 2 cols) */}
          <div className="lg:col-span-2 space-y-6">
            {activeChallenge && (
              <div className="saas-card rounded-3xl p-6 sm:p-8 space-y-6 relative overflow-hidden">
                <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-blue-500 via-indigo-500 to-transparent" />
                
                {/* Dossier Header */}
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/[0.08] pb-5">
                  <div className="space-y-1.5">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-mono text-xs font-bold text-amber-400 bg-slate-900 px-2.5 py-1 rounded-lg border border-slate-750 tracking-wider">
                        {activeChallenge.id}
                      </span>
                      <Badge variant="primary" dot={true}>
                        {activeChallenge.domain || "General"}
                      </Badge>
                      {activeChallenge.priority && (
                        <Badge variant="warning">
                          {activeChallenge.priority} Urgency
                        </Badge>
                      )}
                    </div>
                    <h2 className="text-xl sm:text-2xl font-bold text-white font-display leading-snug">
                      {activeChallenge.title}
                    </h2>
                  </div>

                  <Badge variant={getStatusDetails(activeChallenge.status).badgeVariant} size="lg" dot={true}>
                    {getStatusDetails(activeChallenge.status).label}
                  </Badge>
                </div>

                {/* Metadata Cards Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 text-xs">
                  <div className="p-4 rounded-2xl bg-slate-900/80 border border-white/[0.08] space-y-1 shadow-sm">
                    <span className="text-slate-400 block text-[10px] font-bold uppercase tracking-wider">Submitted By</span>
                    <strong className="text-white block font-semibold truncate">{activeChallenge.submittedBy || "Community Citizen"}</strong>
                    <span className="text-slate-400 text-[11px] font-mono block">
                      {activeChallenge.submittedAt ? new Date(activeChallenge.submittedAt).toLocaleDateString() : "Recently"}
                    </span>
                  </div>

                  <div className="p-4 rounded-2xl bg-slate-900/80 border border-white/[0.08] space-y-1 shadow-sm">
                    <span className="text-slate-400 block text-[10px] font-bold uppercase tracking-wider">Location Jurisdiction</span>
                    <strong className="text-emerald-400 block font-semibold truncate">{activeChallenge.location?.district || "Jharkhand"}</strong>
                    <span className="text-slate-400 text-[11px] block truncate">{activeChallenge.location?.block || "Block under survey"}</span>
                  </div>

                  <div className="p-4 rounded-2xl bg-slate-900/80 border border-white/[0.08] space-y-1 shadow-sm">
                    <span className="text-slate-400 block text-[10px] font-bold uppercase tracking-wider">Affected Demographics</span>
                    <strong className="text-amber-300 block font-semibold truncate">{activeChallenge.affectedPopulation || "Community Assessment"}</strong>
                    <span className="text-slate-400 text-[11px] block">Field impact estimate</span>
                  </div>
                </div>

                {/* Citizen Problem Statement */}
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
                    <FileText className="w-3.5 h-3.5 text-blue-400" />
                    <span>Citizen Field Problem Statement</span>
                  </h4>
                  <div className="text-xs sm:text-sm text-slate-300 leading-relaxed bg-slate-900/90 p-5 rounded-2xl border border-white/[0.08] whitespace-pre-line shadow-inner">
                    {activeChallenge.description}
                  </div>
                </div>

                {/* Official Action Controls */}
                <div className="p-6 rounded-2xl bg-slate-900/90 border border-blue-500/30 space-y-4 shadow-saas-card">
                  <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
                    <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-2">
                      <ShieldCheck className="w-4 h-4 text-blue-400" />
                      <span>Government Verification & Institutional Outreach</span>
                    </h4>
                    <span className="text-[10px] font-mono text-slate-400">Auth Clearance: State Nodal Level</span>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs text-slate-300 font-semibold block">
                      Assign Nodal Department *
                    </label>
                    <select
                      value={selectedDepartment}
                      onChange={(e) => setSelectedDepartment(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-700 text-xs text-white focus:outline-none focus:border-blue-500 transition-colors"
                    >
                      <option value="Dept of Higher & Technical Education">Dept of Higher & Technical Education (Govt. of Jharkhand)</option>
                      <option value="Dept of Agriculture & Farmers Welfare">Dept of Agriculture & Farmers Welfare (Govt. of Jharkhand)</option>
                      <option value="Dept of Drinking Water & Sanitation">Dept of Drinking Water & Sanitation (Govt. of Jharkhand)</option>
                      <option value="Dept of Health, Medical Education & Family Welfare">Dept of Health & Medical Education</option>
                      <option value="Jharkhand State Livelihood Promotion Society">Jharkhand State Livelihood Promotion Society (JSLPS)</option>
                    </select>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs text-slate-300 font-semibold block">
                      Official Verification Remarks & Field Directives
                    </label>
                    <textarea
                      rows={3}
                      value={officialNotes}
                      onChange={(e) => setOfficialNotes(e.target.value)}
                      placeholder="Add official verification notes, field ground-truth check references, or institutional guidance..."
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
                    />
                  </div>

                  <div className="flex flex-wrap items-center justify-end gap-3 pt-2">
                    <button
                      type="button"
                      disabled={isProcessing}
                      onClick={handleReject}
                      className="btn-saas-secondary px-4 py-2.5 rounded-xl text-rose-300 hover:text-rose-200 hover:bg-rose-500/10 text-xs font-semibold disabled:opacity-50 transition-colors"
                    >
                      Reject / Out of Scope
                    </button>
                    <button
                      type="button"
                      disabled={isProcessing}
                      onClick={handleValidate}
                      className="btn-saas-teal px-6 py-2.5 rounded-xl text-xs font-bold flex items-center space-x-2 shadow-glow-emerald disabled:opacity-50"
                    >
                      {isProcessing ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          <span>Publishing Recommendation...</span>
                        </>
                      ) : (
                        <>
                          <CheckCircle2 className="w-4 h-4" />
                          <span>Validate & Recommend to Universities</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>

              </div>
            )}
          </div>

          {/* Validation Queue List on Right (Right 1 col) */}
          <div className="space-y-4">
            <div className="saas-card rounded-3xl p-5 border border-white/[0.08] space-y-4">
              
              <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-1.5">
                  <Filter className="w-3.5 h-3.5 text-blue-400" />
                  <span>Validation Queue</span>
                </h3>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-blue-500/15 text-blue-300 border border-blue-500/30">
                  {queue.length} Reports
                </span>
              </div>

              {/* Quick Queue Filter */}
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  type="text"
                  value={queueFilter}
                  onChange={(e) => setQueueFilter(e.target.value)}
                  placeholder="Filter queue by title or district..."
                  className="w-full pl-8 pr-3 py-1.5 rounded-xl bg-slate-900 border border-slate-750 text-white placeholder-slate-500 text-xs focus:outline-none focus:border-blue-500"
                />
              </div>

              {/* Queue Items */}
              <div className="space-y-2.5 max-h-[700px] overflow-y-auto pr-1">
                {filteredQueue.map((item) => {
                  const isSelected = activeChallenge?.id === item.id;
                  const statusDetails = getStatusDetails(item.status);

                  return (
                    <div 
                      key={item.id}
                      onClick={() => handleSelectChallenge(item)}
                      className={`p-4 rounded-2xl border text-left cursor-pointer transition-all ${
                        isSelected 
                          ? 'bg-blue-600/15 border-blue-500/60 shadow-glow-sm ring-1 ring-blue-500/40' 
                          : 'bg-slate-900/60 border-white/[0.06] hover:bg-slate-850 hover:border-white/[0.12]'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-2 mb-1.5">
                        <span className="text-[10px] font-mono text-blue-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                          {item.id}
                        </span>
                        <Badge variant={statusDetails.badgeVariant} size="sm" dot={true}>
                          {statusDetails.label}
                        </Badge>
                      </div>

                      <h4 className="text-xs font-bold text-white leading-snug line-clamp-2">
                        {item.title}
                      </h4>

                      <div className="flex items-center justify-between text-[10px] text-slate-400 mt-2.5 pt-2 border-t border-white/[0.04]">
                        <span className="flex items-center space-x-1">
                          <MapPin className="w-3 h-3 text-emerald-400" />
                          <span className="truncate max-w-[110px]">{item.location?.district || item.domain}</span>
                        </span>
                        <span className="text-slate-500 font-mono">
                          {item.submittedAt ? new Date(item.submittedAt).toLocaleDateString() : ""}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>

            </div>
          </div>

        </div>
      )}

    </div>
  );
};
