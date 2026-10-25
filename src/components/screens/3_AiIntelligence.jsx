import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useJanSetu } from '../../context/JanSetuContext';
import { useChallenge } from '../../hooks/useChallenge';
import { useAiAnalysis } from '../../hooks/useAiAnalysis';
import { useChallenges } from '../../hooks/useChallenges';
import { Badge } from '../common/Badge';
import { StatCard } from '../common/StatCard';
import { LoadingState } from '../states/LoadingState';
import { EmptyState } from '../states/EmptyState';
import { 
  Sparkles, 
  Cpu, 
  Search, 
  CheckCircle2, 
  GitMerge, 
  ArrowRight, 
  RefreshCw, 
  ShieldCheck, 
  Sliders,
  AlertCircle,
  FileText,
  Play,
  Check,
  ChevronDown,
  Layers,
  Activity,
  Zap,
  Target
} from 'lucide-react';
import { SEED_CHALLENGES } from '../../data/seedData';

export const AiIntelligence = () => {
  const { activeChallengeId, setActiveChallengeId } = useJanSetu();
  const [searchParams, setSearchParams] = useSearchParams();
  const { challenges } = useChallenges();

  const challengeId = searchParams.get('id') || activeChallengeId || 'c-arsenic-ranchi';
  
  const { challenge, loading: challengeLoading } = useChallenge(challengeId);
  const { analysis, status, loading: analysisLoading, triggerAnalysis, refetch } = useAiAnalysis(challengeId);
  const navigate = useNavigate();

  const problemCatalog = Array.isArray(challenges) && challenges.length > 0 ? challenges : SEED_CHALLENGES;

  const handleSelectChallenge = (id) => {
    setActiveChallengeId(id);
    setSearchParams({ id });
  };

  const handleForwardToGovt = () => {
    navigate('/government-dashboard');
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6 animate-in fade-in">
      
      {/* SaaS AI Engine Telemetry Banner */}
      <div className="saas-card rounded-2xl p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 relative overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-blue-500 via-indigo-500 to-teal-400" />
        
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400 shrink-0 shadow-[0_0_12px_rgba(59,130,246,0.2)]">
            <Cpu className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold text-white tracking-tight">JanSetu Deterministic AI Engine</span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 flex items-center space-x-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                <span>Deterministic Core Active</span>
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Deterministic NLP parsing • TF-IDF semantic clustering • Zero external cloud dependency • Grounded in Jharkhand civic datasets
            </p>
          </div>
        </div>

        {/* Quick Challenge Selector Dropdown */}
        <div className="flex items-center space-x-2 shrink-0">
          <span className="text-xs text-slate-400 hidden md:inline">Inspect Problem:</span>
          <select
            value={challengeId}
            onChange={(e) => handleSelectChallenge(e.target.value)}
            className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white font-medium focus:outline-none focus:border-blue-500 max-w-[220px] truncate"
          >
            {problemCatalog.map((p) => (
              <option key={p.id} value={p.id}>
                {p.title}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Header Card */}
      <div className="saas-panel p-6 sm:p-8 rounded-3xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-blue-500 via-indigo-500 to-transparent" />

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-5 relative z-10">
          <div>
            <div className="flex items-center space-x-2">
              <Badge variant="primary" dot={true}>Screen 03 • AI Problem Intelligence</Badge>
              <span className="text-xs text-slate-400 font-mono bg-slate-900 px-2 py-0.5 rounded border border-slate-800">{challenge?.id || challengeId}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-white mt-1.5 font-display tracking-tight">
              Problem Structuring & Semantic Triaging
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 mt-1 max-w-2xl leading-relaxed">
              Autonomous diagnostic engine structures raw community text, calculates urgency priority indices, maps institutional capability requirements, and flags regional duplicates.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => triggerAnalysis()}
              disabled={status === "PROCESSING"}
              className="btn-saas-secondary px-4 py-2.5 rounded-xl text-xs font-semibold flex items-center space-x-2 disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${status === "PROCESSING" ? 'animate-spin text-blue-400' : ''}`} />
              <span>{status === "PROCESSING" ? "Analyzing..." : "Re-run AI Diagnostics"}</span>
            </button>

            <button
              onClick={handleForwardToGovt}
              className="btn-saas-primary px-5 py-2.5 rounded-xl text-xs font-bold flex items-center space-x-2 shadow-glow-sm"
            >
              <span>Validation Queue</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Target Challenge Summary */}
      {challenge && (
        <div className="saas-card rounded-2xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-0.5">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Inspecting Civic Challenge</span>
            <h3 className="text-base font-bold text-white">{challenge.title}</h3>
            <p className="text-xs text-slate-400">
              District: <span className="text-emerald-400 font-semibold">{challenge.district || challenge.location?.district || "Ranchi"}</span> • Domain: <span className="text-blue-300 font-semibold capitalize">{challenge.domain || "water_sanitation"}</span>
            </p>
          </div>
          <div className="flex items-center space-x-2 shrink-0">
            <Badge variant="primary" dot={true}>{challenge.status || challenge.validation_status || "VALIDATED"}</Badge>
            <span className="text-xs text-amber-400 font-mono bg-slate-900 px-2.5 py-1 rounded-lg border border-slate-750">
              {challenge.reference_code || challenge.referenceCode || challenge.id}
            </span>
          </div>
        </div>
      )}

      {/* Analysis KPI Grid */}
      {(status === "COMPLETED" || analysis) && analysis && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Classification Certainty"
            value={`${analysis.domainConfidence || 96}%`}
            subtitle={analysis.subDomain || "Sub-Domain Confirmed"}
            icon={Target}
            color="blue"
          />
          <StatCard
            title="Priority Urgency Score"
            value={`${analysis.priorityScore || 88} / 100`}
            subtitle={analysis.priorityLevel || "Critical Priority"}
            icon={Zap}
            color="amber"
          />
          <StatCard
            title="Cluster Proximity"
            value={analysis.semanticDuplicates?.length > 0 ? `${analysis.semanticDuplicates[0].similarity}%` : "Unique"}
            subtitle={analysis.semanticDuplicates?.length > 0 ? "Related Duplicate Found" : "No Regional Duplicates"}
            icon={GitMerge}
            color="teal"
          />
          <StatCard
            title="Institutional Readiness"
            value="High"
            subtitle={`${analysis.requiredCapabilities?.length || 4} Core Capabilities Required`}
            icon={Activity}
            color="emerald"
          />
        </div>
      )}

      {/* When Processing */}
      {status === "PROCESSING" && (
        <LoadingState 
          message="JanSetu Deterministic AI Engine is structuring domain context, extracting entities, and calculating clustering..." 
          minHeight="min-h-[260px]"
        />
      )}

      {/* When Analysis Exists */}
      {(status === "COMPLETED" || analysis) && analysis && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Left Columns: Domain & Capabilities */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Domain & Priority Card */}
            <div className="saas-card rounded-3xl p-6 sm:p-7 space-y-4">
              <div className="flex items-center justify-between border-b border-white/[0.08] pb-3.5">
                <div className="flex items-center space-x-2">
                  <Sparkles className="w-4 h-4 text-blue-400" />
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider">Domain & Urgency Assessment</h3>
                </div>
                {analysis.domainConfidence !== undefined && (
                  <Badge variant="success" dot={true}>Engine Confidence: {analysis.domainConfidence}%</Badge>
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 rounded-2xl bg-slate-900/80 border border-white/[0.08] space-y-1">
                  <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Classified Domain</span>
                  <p className="text-base font-bold text-white capitalize">{analysis.domain || challenge?.domain || "Water & Sanitation"}</p>
                  {analysis.subDomain && <p className="text-xs text-teal-400 font-semibold">{analysis.subDomain}</p>}
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/80 border border-white/[0.08] space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Calculated Priority</span>
                    <span className="text-xs font-mono font-bold text-amber-400">
                      {analysis.priorityScore !== undefined ? `${analysis.priorityScore}/100` : "88/100"}
                    </span>
                  </div>
                  <p className="text-base font-bold text-amber-300">
                    {analysis.priorityLevel || challenge?.priority || "Critical"}
                  </p>
                </div>
              </div>

              {analysis.priorityRationale && (
                <div className="p-4 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-xs text-slate-300 leading-relaxed">
                  <strong className="text-blue-300 font-semibold">Diagnostic Rationale: </strong>
                  {analysis.priorityRationale}
                </div>
              )}
            </div>

            {/* Extracted Entities Table Card */}
            {Array.isArray(analysis.extractedEntities) && analysis.extractedEntities.length > 0 && (
              <div className="saas-card rounded-3xl p-6 sm:p-7 space-y-4">
                <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2">
                    <Search className="w-4 h-4 text-teal-400" />
                    <span>Extracted Semantic Entities</span>
                  </h3>
                  <span className="text-[10px] font-mono text-slate-400">{analysis.extractedEntities.length} Features Tagged</span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-white/[0.08] text-slate-400">
                        <th className="pb-3 font-semibold uppercase text-[10px] tracking-wider">Entity Category</th>
                        <th className="pb-3 font-semibold uppercase text-[10px] tracking-wider">Extracted Value / Target</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/[0.04]">
                      {analysis.extractedEntities.map((ent, idx) => (
                        <tr key={idx} className="hover:bg-slate-850/50 transition-colors">
                          <td className="py-3 font-medium text-slate-300">{ent.category}</td>
                          <td className="py-3 text-white font-mono text-xs">
                            <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-750 text-blue-300">
                              {ent.value}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Required Capabilities Matrix */}
            {Array.isArray(analysis.requiredCapabilities) && analysis.requiredCapabilities.length > 0 && (
              <div className="saas-card rounded-3xl p-6 sm:p-7 space-y-4">
                <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2">
                    <Sliders className="w-4 h-4 text-purple-400" />
                    <span>Required Institutional Capabilities Matrix</span>
                  </h3>
                  <span className="text-[10px] font-mono text-slate-400">Weighted Matching Vector</span>
                </div>

                <div className="space-y-3">
                  {analysis.requiredCapabilities.map((cap, idx) => (
                    <div key={idx} className="p-3.5 rounded-2xl bg-slate-900/80 border border-white/[0.08] space-y-2">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-semibold text-slate-200">{cap.name}</span>
                        {cap.weight !== undefined && (
                          <span className="font-mono text-blue-400 font-bold">{cap.weight}% Weight</span>
                        )}
                      </div>
                      {cap.weight !== undefined && (
                        <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                          <div 
                            className="h-full bg-gradient-to-r from-blue-500 via-indigo-500 to-teal-400 rounded-full"
                            style={{ width: `${cap.weight}%` }}
                          />
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

          </div>

          {/* Right Column: Semantic Duplicate Clustering */}
          <div className="space-y-6">
            <div className="saas-card rounded-3xl p-6 sm:p-7 space-y-4">
              <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
                <div className="flex items-center space-x-2">
                  <GitMerge className="w-4 h-4 text-amber-400" />
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider">Semantic Duplicate Detection</h3>
                </div>
                {Array.isArray(analysis.semanticDuplicates) && (
                  <Badge variant="warning" size="sm" dot={true}>
                    {analysis.semanticDuplicates.length} Clustered
                  </Badge>
                )}
              </div>

              {!Array.isArray(analysis.semanticDuplicates) || analysis.semanticDuplicates.length === 0 ? (
                <p className="text-xs text-slate-400 leading-relaxed py-6 text-center">
                  No regional duplicates detected. Challenge registered as a unique regional innovation mandate.
                </p>
              ) : (
                <div className="space-y-3">
                  {analysis.semanticDuplicates.map((dup) => (
                    <div key={dup.id} className="p-4 rounded-2xl bg-slate-900/90 border border-white/[0.08] space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-mono text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">{dup.id}</span>
                        {dup.similarity && (
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-300 font-bold border border-amber-500/30">
                            {dup.similarity}% Similarity
                          </span>
                        )}
                      </div>
                      <h5 className="text-xs font-bold text-white leading-snug">{dup.title}</h5>
                      {dup.district && (
                        <p className="text-[10px] text-slate-400">District: {dup.district}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {analysis.clusterSummary && (
                <div className="p-3.5 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-200 leading-relaxed">
                  {analysis.clusterSummary}
                </div>
              )}
            </div>

            <div className="saas-panel p-6 rounded-3xl border border-white/[0.08] text-xs space-y-2.5 text-slate-400 shadow-sm">
              <div className="flex items-center space-x-2 text-slate-200 font-semibold">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Deterministic Explainability Standards</span>
              </div>
              <p className="leading-relaxed text-[11px]">
                The Basic AI Engine structures problems and provides transparent capability vectors. Final mandate issuance rests with verified government nodal officers.
              </p>
            </div>
          </div>

        </div>
      )}

    </div>
  );
};
