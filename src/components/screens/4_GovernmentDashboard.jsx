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
  Loader2
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

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-panel p-6 rounded-3xl border border-navy-700">
        <div>
          <div className="flex items-center space-x-2">
            <Badge variant="warning">Screen 04 • Government Administration</Badge>
            <span className="text-xs text-slate-400">Govt of Jharkhand Portal</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white mt-1 font-display">
            Validation Queue & Mandate Assignment
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-xl">
            Authorize community reports, verify ground truth with district nodal officers, and issue official solver mandates to Higher Education Institutions (HEIs).
          </p>
        </div>

        {activeChallenge && activeChallenge.status !== 'SUBMITTED' && (
          <button
            onClick={() => handleProceedToMatching(activeChallenge.id)}
            className="px-5 py-2.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs flex items-center space-x-2 shadow-glow-teal transition-transform hover:scale-105"
          >
            <span>Proceed to University Matching</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        )}
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
          
          {/* Main Inspection View for Active Challenge */}
          <div className="lg:col-span-2 space-y-6">
            {activeChallenge && (
              <div className="glass-card rounded-2xl p-6 border border-navy-700 space-y-6">
                
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-navy-700 pb-4">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-mono text-slate-400 font-bold">{activeChallenge.id}</span>
                      <Badge variant="primary">{activeChallenge.domain}</Badge>
                      {activeChallenge.priority && (
                        <Badge variant="warning">{activeChallenge.priority}</Badge>
                      )}
                    </div>
                    <h3 className="text-lg font-bold text-white">{activeChallenge.title}</h3>
                  </div>

                  <Badge variant={getStatusDetails(activeChallenge.status).badgeVariant}>
                    {getStatusDetails(activeChallenge.status).label}
                  </Badge>
                </div>

                {/* Meta details */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
                  <div className="p-3 rounded-xl bg-navy-850 border border-navy-700">
                    <span className="text-slate-400 block text-[10px] font-semibold uppercase">Submitted By</span>
                    <strong className="text-white block mt-0.5">{activeChallenge.submittedBy || "Community Representative"}</strong>
                    <span className="text-slate-500 text-[11px]">
                      {activeChallenge.submittedAt ? new Date(activeChallenge.submittedAt).toLocaleDateString() : "Recently"}
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-navy-850 border border-navy-700">
                    <span className="text-slate-400 block text-[10px] font-semibold uppercase">Location</span>
                    <strong className="text-white block mt-0.5">{activeChallenge.location?.district || "Jharkhand"}</strong>
                    <span className="text-slate-400 text-[11px]">{activeChallenge.location?.block || "District Wide"}</span>
                  </div>

                  <div className="p-3 rounded-xl bg-navy-850 border border-navy-700">
                    <span className="text-slate-400 block text-[10px] font-semibold uppercase">Affected Population</span>
                    <strong className="text-amber-400 block mt-0.5">{activeChallenge.affectedPopulation || "Under assessment"}</strong>
                  </div>
                </div>

                {/* Description */}
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Citizen Problem Statement</h4>
                  <p className="text-xs text-slate-300 leading-relaxed bg-navy-850 p-4 rounded-xl border border-navy-700">
                    {activeChallenge.description}
                  </p>
                </div>

                {/* Official Action Controls */}
                <div className="p-5 rounded-2xl bg-navy-850 border border-blue-500/30 space-y-4">
                  <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-1.5">
                    <ShieldCheck className="w-4 h-4 text-blue-400" />
                    <span>Government Review & Assignment Controls</span>
                  </h4>

                  <div className="space-y-2">
                    <label className="text-xs text-slate-300 font-semibold">Assign Nodal Department</label>
                    <select
                      value={selectedDepartment}
                      onChange={(e) => setSelectedDepartment(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl bg-navy-900 border border-navy-700 text-xs text-white"
                    >
                      <option value="Dept of Higher & Technical Education">Dept of Higher & Technical Education (Govt. of Jharkhand)</option>
                      <option value="Dept of Agriculture & Farmers Welfare">Dept of Agriculture & Farmers Welfare (Govt. of Jharkhand)</option>
                      <option value="Dept of Drinking Water & Sanitation">Dept of Drinking Water & Sanitation (Govt. of Jharkhand)</option>
                      <option value="Dept of Health, Medical Education & Family Welfare">Dept of Health & Medical Education</option>
                      <option value="Jharkhand State Livelihood Promotion Society">Jharkhand State Livelihood Promotion Society (JSLPS)</option>
                    </select>
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs text-slate-300 font-semibold">Official Verification Remarks</label>
                    <textarea
                      rows={3}
                      value={officialNotes}
                      onChange={(e) => setOfficialNotes(e.target.value)}
                      placeholder="Add official verification notes, field check references, or mandate instructions..."
                      className="w-full px-3 py-2 rounded-xl bg-navy-900 border border-navy-700 text-xs text-white placeholder-slate-500"
                    />
                  </div>

                  <div className="flex flex-wrap items-center justify-end gap-3 pt-2">
                    <button
                      type="button"
                      disabled={isProcessing}
                      onClick={handleReject}
                      className="px-4 py-2 rounded-xl bg-navy-750 hover:bg-navy-700 text-rose-300 text-xs font-semibold disabled:opacity-50"
                    >
                      Reject / Out of Scope
                    </button>
                    <button
                      type="button"
                      disabled={isProcessing}
                      onClick={handleValidate}
                      className="px-6 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center space-x-2 shadow-glow-emerald disabled:opacity-50"
                    >
                      {isProcessing ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          <span>Submitting...</span>
                        </>
                      ) : (
                        <>
                          <CheckCircle2 className="w-4 h-4" />
                          <span>Validate & Issue Solver Mandate</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>

              </div>
            )}
          </div>

          {/* Queue List on Right */}
          <div className="space-y-4">
            <div className="glass-card rounded-2xl p-5 border border-navy-700 space-y-3">
              <div className="flex items-center justify-between border-b border-navy-700 pb-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-1.5">
                  <Filter className="w-3.5 h-3.5 text-blue-400" />
                  <span>Validation Queue ({queue.length})</span>
                </h3>
              </div>

              <div className="space-y-2.5">
                {queue.map((item) => {
                  const isSelected = activeChallenge?.id === item.id;
                  const statusDetails = getStatusDetails(item.status);

                  return (
                    <div 
                      key={item.id}
                      onClick={() => handleSelectChallenge(item)}
                      className={`p-3.5 rounded-xl border text-left cursor-pointer transition-all ${
                        isSelected 
                          ? 'bg-blue-600/15 border-blue-500/50 shadow-glow-sm' 
                          : 'bg-navy-850/60 border-navy-700 hover:bg-navy-800'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[10px] font-mono text-blue-400 font-semibold">{item.id}</span>
                        <Badge variant={statusDetails.badgeVariant} size="sm">
                          {statusDetails.label}
                        </Badge>
                      </div>
                      <h4 className="text-xs font-bold text-white leading-snug line-clamp-2">{item.title}</h4>
                      <div className="flex items-center justify-between text-[10px] text-slate-400 mt-2">
                        <span>{item.location?.district || item.domain}</span>
                        <span className="text-slate-500">
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
