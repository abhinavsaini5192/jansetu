import React, { useState } from 'react';
import { useJanSetu } from '../../context/JanSetuContext';
import { useChallenge } from '../../hooks/useChallenge';
import { useImpact } from '../../hooks/useImpact';
import { Badge } from '../common/Badge';
import { StatCard } from '../common/StatCard';
import { SkeletonCard } from '../states/SkeletonCard';
import { EmptyState } from '../states/EmptyState';
import { ErrorState } from '../states/ErrorState';
import { 
  Award, 
  CheckCircle2, 
  Clock, 
  Users, 
  MapPin, 
  ShieldCheck, 
  Star, 
  FileCheck, 
  Inbox,
  Loader2
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';

export const ImpactDashboard = () => {
  const { activeChallengeId, showToast, triggerConfetti } = useJanSetu();
  const challengeId = activeChallengeId || 'c-arsenic-ranchi';
  const { challenge } = useChallenge(challengeId);
  const { impact, loading, error, verifyImpact, submitEvidence, refetch } = useImpact(challengeId);

  const [signatoryNote, setSignatoryNote] = useState("");
  const [isVerifying, setIsVerifying] = useState(false);
  const [showEvidenceModal, setShowEvidenceModal] = useState(false);
  const [evidenceForm, setEvidenceForm] = useState({
    villagesCovered: "",
    beneficiariesReached: "",
    baselineMetric: "",
    postInterventionMetric: "",
    economicBenefit: ""
  });
  const [isSubmittingEvidence, setIsSubmittingEvidence] = useState(false);

  const handleVerify = async () => {
    if (!impact?.id) return;
    setIsVerifying(true);
    try {
      await verifyImpact(impact.id, {
        signatoryNote: signatoryNote || "Verified on-ground according to official societal impact protocols."
      });
      triggerConfetti();
      showToast("Official Government Verification recorded.", "success");
    } catch (err) {
      showToast(err.message || "Verification failed.", "error");
    } finally {
      setIsVerifying(false);
    }
  };

  const handleEvidenceSubmit = async (e) => {
    e.preventDefault();
    setIsSubmittingEvidence(true);
    try {
      await submitEvidence(evidenceForm);
      showToast("Field impact evidence submitted successfully.", "success");
      setShowEvidenceModal(false);
    } catch (err) {
      showToast(err.message || "Failed to submit evidence.", "error");
    } finally {
      setIsSubmittingEvidence(false);
    }
  };

  if (!challengeId) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16">
        <EmptyState
          icon={Award}
          title="No Challenge Selected"
          description="Select a completed or piloted challenge to inspect verifiable field evidence and government impact sign-off."
          actionLabel="View Platform Overview"
          actionTo="/"
        />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        <SkeletonCard count={3} />
      </div>
    );
  }

  if (error && !impact) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16">
        <ErrorState
          title="Failed to Load Impact Metrics"
          message={error}
          onRetry={refetch}
        />
      </div>
    );
  }

  if (!impact) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 space-y-6">
        <EmptyState
          icon={Award}
          title="Impact Data Has Not Been Submitted Yet"
          description="A project is only considered successful once verifiable field evidence and community feedback are submitted and reviewed."
          actionLabel="Submit Field Evidence"
          onAction={() => setShowEvidenceModal(true)}
        />

        {showEvidenceModal && (
          <div className="glass-card p-6 rounded-3xl border border-navy-700 space-y-4">
            <h3 className="text-base font-bold text-white">Submit Field Impact Evidence</h3>
            <form onSubmit={handleEvidenceSubmit} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs text-slate-300 font-semibold block mb-1">Villages / Panchayats Covered *</label>
                  <input
                    type="number"
                    required
                    value={evidenceForm.villagesCovered}
                    onChange={e => setEvidenceForm({ ...evidenceForm, villagesCovered: e.target.value })}
                    placeholder="e.g., 4"
                    className="w-full px-3 py-2 rounded-xl bg-navy-850 border border-navy-700 text-xs text-white"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-300 font-semibold block mb-1">Beneficiaries Reached *</label>
                  <input
                    type="text"
                    required
                    value={evidenceForm.beneficiariesReached}
                    onChange={e => setEvidenceForm({ ...evidenceForm, beneficiariesReached: e.target.value })}
                    placeholder="e.g., 850+ farmers"
                    className="w-full px-3 py-2 rounded-xl bg-navy-850 border border-navy-700 text-xs text-white"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs text-slate-300 font-semibold block mb-1">Baseline Metric (Before Intervention)</label>
                  <input
                    type="text"
                    value={evidenceForm.baselineMetric}
                    onChange={e => setEvidenceForm({ ...evidenceForm, baselineMetric: e.target.value })}
                    placeholder="e.g., 34% crop loss"
                    className="w-full px-3 py-2 rounded-xl bg-navy-850 border border-navy-700 text-xs text-white"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-300 font-semibold block mb-1">Measured Outcome (Post-Intervention)</label>
                  <input
                    type="text"
                    value={evidenceForm.postInterventionMetric}
                    onChange={e => setEvidenceForm({ ...evidenceForm, postInterventionMetric: e.target.value })}
                    placeholder="e.g., 9% residual loss"
                    className="w-full px-3 py-2 rounded-xl bg-navy-850 border border-navy-700 text-xs text-white"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowEvidenceModal(false)}
                  className="px-4 py-2 rounded-xl bg-navy-800 text-xs font-semibold text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingEvidence}
                  className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs"
                >
                  {isSubmittingEvidence ? "Submitting..." : "Save Evidence Record"}
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    );
  }

  const chartData = impact.chartData || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-in fade-in">
      
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-5 saas-panel p-6 sm:p-8 rounded-3xl relative overflow-hidden">
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <span className="saas-badge bg-emerald-500/10 text-emerald-300 border-emerald-500/30">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              EVIDENCE-BASED IMPACT
            </span>
            <span className="text-xs text-slate-400 font-mono">{challenge?.id || activeChallengeId}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white font-display tracking-tight">
            Measurable Societal Impact & Verification
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
            A project is only complete when verified on-ground. Review verifiable baseline vs outcome metrics, community feedback audits, and state certification.
          </p>
        </div>

        {impact.isGovernmentVerified ? (
          <div className="flex items-center space-x-3 px-5 py-3 rounded-2xl bg-emerald-500/15 text-emerald-300 border border-emerald-500/35 shadow-saas-card shrink-0">
            <Award className="w-6 h-6 text-emerald-400" />
            <div className="text-left">
              <span className="text-[10px] uppercase font-bold tracking-wider block text-emerald-400 font-mono">Official State Seal</span>
              <span className="text-xs font-black tracking-wide">IMPACT VERIFIED ✓</span>
            </div>
          </div>
        ) : (
          <button
            onClick={handleVerify}
            disabled={isVerifying}
            className="btn-saas-teal px-6 py-3 rounded-2xl text-xs font-black flex items-center space-x-2 shrink-0 disabled:opacity-50"
          >
            {isVerifying ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Verifying...</span>
              </>
            ) : (
              <>
                <ShieldCheck className="w-4 h-4" />
                <span>Authorize Government Verification</span>
              </>
            )}
          </button>
        )}
      </div>

      {/* Real Stat Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <StatCard 
          title="Villages Covered" 
          value={impact.villagesCovered !== undefined ? `${impact.villagesCovered} Villages` : "—"} 
          subtitle="Ground coverage" 
          color="blue" 
        />
        <StatCard 
          title="Beneficiaries Reached" 
          value={impact.beneficiariesReached || "—"} 
          subtitle="Citizens impacted" 
          color="teal" 
        />
        <StatCard 
          title="Baseline vs Outcome" 
          value={impact.postInterventionMetric || "—"} 
          subtitle={impact.baselineMetric ? `Baseline: ${impact.baselineMetric}` : "Post-intervention"} 
          color="rose" 
        />
        <StatCard 
          title="Economic Benefit" 
          value={impact.economicBenefit || "—"} 
          subtitle="Estimated preserved yield" 
          color="amber" 
        />
      </div>

      {/* Main Impact Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Col 1 & 2: Before vs After Comparative Data & Chart */}
        <div className="lg:col-span-2 space-y-6">
          
          {chartData.length > 0 && (
            <div className="saas-card rounded-2xl p-6 sm:p-7 border border-white/[0.08] space-y-4">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                Impact Delta Visualization
              </h3>
              <div className="h-60 w-full pt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                    <YAxis stroke="#64748b" fontSize={11} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#070B14', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px', fontSize: '11px' }}
                      itemStyle={{ color: '#fff' }}
                    />
                    <Bar dataKey="Before" fill="#F43F5E" radius={[6, 6, 0, 0]} />
                    <Bar dataKey="After" fill="#10B981" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Evidence Dossier */}
          {Array.isArray(impact.evidenceDossier) && impact.evidenceDossier.length > 0 && (
            <div className="saas-card rounded-2xl p-6 sm:p-7 border border-white/[0.08] space-y-4">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-2">
                <FileCheck className="w-4 h-4 text-teal-400" />
                <span>Auditable Evidence Dossier</span>
              </h3>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {impact.evidenceDossier.map((doc, idx) => (
                  <div key={idx} className="p-4 rounded-xl saas-panel border border-white/[0.08] space-y-2">
                    {doc.fileUrl && (
                      <img
                        src={doc.fileUrl}
                        alt={doc.title || "Evidence"}
                        className="w-full h-32 rounded-xl object-cover border border-white/[0.08]"
                      />
                    )}
                    <h5 className="text-xs font-bold text-white">{doc.title || `Evidence Artifact #${idx + 1}`}</h5>
                    {doc.description && (
                      <p className="text-[11px] text-slate-400 leading-relaxed font-normal">{doc.description}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>

        {/* Col 3: State Verification Seal */}
        <div className="space-y-6">
          <div className="saas-card rounded-2xl p-6 border border-emerald-500/35 space-y-4 relative overflow-hidden">
            {/* Emerald Top Highlight */}
            <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-emerald-500 via-teal-400 to-cyan-400" />

            <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                  State Verification
                </h3>
              </div>
              <Badge variant={impact.isGovernmentVerified ? "success" : "warning"} size="sm" dot={true}>
                {impact.isGovernmentVerified ? "Verified" : "Pending Review"}
              </Badge>
            </div>

            <div className="text-center py-3">
              <div className="w-16 h-16 rounded-2xl bg-emerald-500/15 border border-emerald-400/40 flex items-center justify-center mx-auto shadow-saas-card">
                <Award className="w-8 h-8 text-emerald-400" />
              </div>
              <h4 className="text-base font-black text-white font-display mt-3">
                {impact.isGovernmentVerified ? "Certified Societal Outcome" : "Awaiting Verification"}
              </h4>
              <p className="text-[11px] text-slate-400">
                Department of Higher & Technical Education
              </p>
            </div>

            {impact.isGovernmentVerified ? (
              <div className="p-3.5 rounded-xl saas-panel border border-white/[0.08] space-y-2 text-xs">
                <span className="text-slate-400 block text-[10px] font-semibold uppercase tracking-wider">Official Attestation:</span>
                <p className="text-slate-200 italic leading-relaxed text-[11px]">
                  "{impact.verificationNotes || "Officially verified on-ground."}"
                </p>
                <div className="pt-2 border-t border-white/[0.06] text-[10px] text-emerald-400 font-mono flex items-center justify-between">
                  <span>Signatory: {impact.verificationSignatory || "State Authority"}</span>
                  <span>{impact.verifiedAt ? new Date(impact.verifiedAt).toLocaleDateString() : ""}</span>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <textarea
                  rows={3}
                  value={signatoryNote}
                  onChange={e => setSignatoryNote(e.target.value)}
                  placeholder="Official verification notes or inspection reference..."
                  className="w-full px-3.5 py-2.5 rounded-xl saas-input text-xs placeholder-slate-500 resize-y"
                />
                <button
                  onClick={handleVerify}
                  disabled={isVerifying}
                  className="w-full py-3 rounded-xl btn-saas-teal text-xs font-bold flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Execute Verification Stamp</span>
                </button>
              </div>
            )}
          </div>
        </div>

      </div>

    </div>
  );
};
