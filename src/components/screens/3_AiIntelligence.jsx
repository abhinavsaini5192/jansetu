import React from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useJanSetu } from '../../context/JanSetuContext';
import { useChallenge } from '../../hooks/useChallenge';
import { useAiAnalysis } from '../../hooks/useAiAnalysis';
import { Badge } from '../common/Badge';
import { LoadingState } from '../states/LoadingState';
import { EmptyState } from '../states/EmptyState';
import { ErrorState } from '../states/ErrorState';
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
  Play
} from 'lucide-react';

export const AiIntelligence = () => {
  const { activeChallengeId } = useJanSetu();
  const [searchParams] = useSearchParams();
  const challengeId = searchParams.get('id') || activeChallengeId;
  
  const { challenge, loading: challengeLoading } = useChallenge(challengeId);
  const { analysis, status, loading: analysisLoading, error, triggerAnalysis, refetch } = useAiAnalysis(challengeId);
  const navigate = useNavigate();

  if (!challengeId) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16">
        <EmptyState
          icon={Cpu}
          title="No Challenge Selected"
          description="Select a challenge from the listing or submit a new community report to inspect AI structuring and duplicate analysis."
          actionLabel="Go to Challenges"
          actionTo="/"
        />
      </div>
    );
  }

  if (challengeLoading || analysisLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16">
        <LoadingState message="Retrieving AI intelligence insights..." />
      </div>
    );
  }

  if (error && !analysis) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16">
        <ErrorState
          title="AI Analysis Unavailable"
          message={error}
          onRetry={refetch}
        />
      </div>
    );
  }

  const handleForwardToGovt = () => {
    navigate('/government-dashboard');
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-panel p-6 rounded-3xl border border-blue-500/30">
        <div>
          <div className="flex items-center space-x-2">
            <Badge variant="primary">Screen 03 • AI Problem Intelligence</Badge>
            <span className="text-xs text-slate-400 font-mono">{challenge?.id || challengeId}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white mt-1 font-display">
            Problem Structuring & Semantic Clustering
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            AI structures raw community submissions, verifies semantic duplication across regional tickets, and determines required solver capabilities.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => triggerAnalysis()}
            disabled={status === "PROCESSING"}
            className="px-4 py-2.5 rounded-xl bg-navy-850 hover:bg-navy-750 text-slate-200 border border-navy-700 text-xs font-semibold flex items-center space-x-2 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${status === "PROCESSING" ? 'animate-spin text-blue-400' : ''}`} />
            <span>{status === "PROCESSING" ? "Analyzing..." : "Re-run AI Analysis"}</span>
          </button>

          <button
            onClick={handleForwardToGovt}
            className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs flex items-center space-x-2 shadow-glow-sm"
          >
            <span>Government Queue</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Target Challenge Summary */}
      {challenge && (
        <div className="glass-card rounded-2xl p-5 border border-navy-750 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Inspecting Challenge</span>
            <h3 className="text-base font-bold text-white mt-0.5">{challenge.title}</h3>
            <p className="text-xs text-slate-400">
              District: <span className="text-slate-300">{challenge.location?.district || "Unspecified"}</span> • Domain: <span className="text-teal-400">{challenge.domain}</span>
            </p>
          </div>
          <Badge variant="primary">{challenge.status || "PENDING"}</Badge>
        </div>
      )}

      {/* When AI Analysis is Not Started */}
      {status === "NOT_STARTED" && (
        <div className="glass-card rounded-3xl p-8 border border-navy-750 text-center space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400 mx-auto">
            <Sparkles className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white">AI Analysis Not Yet Generated</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
            This challenge has not been processed through the AI domain extraction and semantic clustering pipeline yet.
          </p>
          <button
            onClick={() => triggerAnalysis()}
            className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs inline-flex items-center space-x-2"
          >
            <Play className="w-3.5 h-3.5" />
            <span>Execute AI Analysis Now</span>
          </button>
        </div>
      )}

      {/* When Processing */}
      {status === "PROCESSING" && (
        <LoadingState 
          message="AI Neural Engine is processing domain context, extracting entities, and checking duplicate clusters..." 
          minHeight="min-h-[260px]"
        />
      )}

      {/* When Analysis Exists */}
      {status === "COMPLETED" && analysis && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Left Columns: Domain & Capabilities */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Domain & Priority Card */}
            <div className="glass-card rounded-2xl p-6 border border-navy-700 space-y-4">
              <div className="flex items-center justify-between border-b border-navy-700 pb-3">
                <div className="flex items-center space-x-2">
                  <Sparkles className="w-4 h-4 text-blue-400" />
                  <h3 className="text-sm font-bold text-white">Domain & Urgency Assessment</h3>
                </div>
                {analysis.domainConfidence !== undefined && (
                  <Badge variant="success">Confidence: {analysis.domainConfidence}%</Badge>
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-navy-850 border border-navy-700 space-y-1">
                  <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Classified Domain</span>
                  <p className="text-base font-bold text-white">{analysis.domain || challenge?.domain || "—"}</p>
                  {analysis.subDomain && <p className="text-xs text-brand-teal font-medium">{analysis.subDomain}</p>}
                </div>

                <div className="p-4 rounded-xl bg-navy-850 border border-navy-700 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Priority Score</span>
                    <span className="text-xs font-bold text-amber-400">
                      {analysis.priorityScore !== undefined ? `${analysis.priorityScore} / 100` : "—"}
                    </span>
                  </div>
                  <p className="text-base font-bold text-amber-300">
                    {analysis.priorityLevel || challenge?.priority || "Normal"}
                  </p>
                </div>
              </div>

              {analysis.priorityRationale && (
                <div className="p-3.5 rounded-xl bg-blue-500/10 border border-blue-500/20 text-xs text-slate-300 leading-relaxed">
                  <strong className="text-blue-300">Priority Rationale: </strong>
                  {analysis.priorityRationale}
                </div>
              )}
            </div>

            {/* Extracted Entities */}
            {Array.isArray(analysis.extractedEntities) && analysis.extractedEntities.length > 0 && (
              <div className="glass-card rounded-2xl p-6 border border-navy-700 space-y-4">
                <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                  <Search className="w-4 h-4 text-teal-400" />
                  <span>Extracted Contextual Entities</span>
                </h3>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-navy-700 text-slate-400">
                        <th className="pb-2 font-semibold">Entity Category</th>
                        <th className="pb-2 font-semibold">Extracted Value</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-navy-800">
                      {analysis.extractedEntities.map((ent, idx) => (
                        <tr key={idx} className="hover:bg-navy-800/40 transition-colors">
                          <td className="py-2.5 font-medium text-slate-300">{ent.category}</td>
                          <td className="py-2.5 text-white font-mono">{ent.value}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Required Capabilities Matrix */}
            {Array.isArray(analysis.requiredCapabilities) && analysis.requiredCapabilities.length > 0 && (
              <div className="glass-card rounded-2xl p-6 border border-navy-700 space-y-4">
                <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                  <Sliders className="w-4 h-4 text-purple-400" />
                  <span>Required Institutional Capabilities</span>
                </h3>

                <div className="space-y-3">
                  {analysis.requiredCapabilities.map((cap, idx) => (
                    <div key={idx} className="p-3 rounded-xl bg-navy-850 border border-navy-700 space-y-1.5">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-semibold text-slate-200">{cap.name}</span>
                        {cap.weight !== undefined && (
                          <span className="font-mono text-blue-400 font-bold">{cap.weight}% Weight</span>
                        )}
                      </div>
                      {cap.weight !== undefined && (
                        <div className="w-full bg-navy-950 rounded-full h-1.5 overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-blue-500 to-teal-400 rounded-full"
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
            <div className="glass-card rounded-2xl p-6 border border-navy-700 space-y-4">
              <div className="flex items-center justify-between border-b border-navy-700 pb-3">
                <div className="flex items-center space-x-2">
                  <GitMerge className="w-4 h-4 text-amber-400" />
                  <h3 className="text-sm font-bold text-white">Duplicate Detection</h3>
                </div>
                {Array.isArray(analysis.semanticDuplicates) && (
                  <Badge variant="warning" size="sm">
                    {analysis.semanticDuplicates.length} Related
                  </Badge>
                )}
              </div>

              {!Array.isArray(analysis.semanticDuplicates) || analysis.semanticDuplicates.length === 0 ? (
                <p className="text-xs text-slate-400 leading-relaxed py-4 text-center">
                  No semantic duplicate reports detected. This challenge is registered as a unique regional ticket.
                </p>
              ) : (
                <div className="space-y-3">
                  {analysis.semanticDuplicates.map((dup) => (
                    <div key={dup.id} className="p-3.5 rounded-xl bg-navy-850 border border-navy-700 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-mono text-amber-400 font-bold">{dup.id}</span>
                        {dup.similarity && (
                          <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-bold">
                            {dup.similarity}% Match
                          </span>
                        )}
                      </div>
                      <h5 className="text-xs font-bold text-white">{dup.title}</h5>
                      {dup.district && (
                        <p className="text-[10px] text-slate-400">District: {dup.district}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {analysis.clusterSummary && (
                <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-200 leading-relaxed">
                  {analysis.clusterSummary}
                </div>
              )}
            </div>

            <div className="glass-panel p-5 rounded-2xl border border-navy-800 text-xs space-y-2 text-slate-400">
              <div className="flex items-center space-x-2 text-slate-200 font-semibold">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Non-Autonomous Governance</span>
              </div>
              <p className="leading-relaxed text-[11px]">
                AI provides structuring recommendations. Validation authority rests solely with verified government nodal officers.
              </p>
            </div>
          </div>

        </div>
      )}

    </div>
  );
};
