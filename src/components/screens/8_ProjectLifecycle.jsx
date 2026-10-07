import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useJanSetu } from '../../context/JanSetuContext';
import { useProject } from '../../hooks/useProject';
import { LifecycleProgressBar } from '../common/LifecycleProgressBar';
import { Badge } from '../common/Badge';
import { SkeletonCard } from '../states/SkeletonCard';
import { EmptyState } from '../states/EmptyState';
import { ErrorState } from '../states/ErrorState';
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  ArrowRight, 
  Layers, 
  Zap,
  Inbox,
  Loader2
} from 'lucide-react';

export const ProjectLifecycle = () => {
  const { activeChallengeId, activeProjectId, showToast } = useJanSetu();
  const identifier = activeProjectId || activeChallengeId;
  const isChallenge = !activeProjectId;

  const { project, loading, error, updateMilestone, refetch } = useProject(identifier, isChallenge);
  const navigate = useNavigate();

  const [updatingMilestoneId, setUpdatingMilestoneId] = useState(null);

  const handleMilestoneComplete = async (milestoneId) => {
    setUpdatingMilestoneId(milestoneId);
    try {
      await updateMilestone(milestoneId, { status: "COMPLETED", progress: 100 });
      showToast("Milestone marked complete.", "success");
    } catch (err) {
      showToast(err.message || "Failed to update milestone.", "error");
    } finally {
      setUpdatingMilestoneId(null);
    }
  };

  const handleProceedToImpact = () => {
    navigate('/impact-dashboard');
  };

  if (!identifier) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16">
        <EmptyState
          icon={Activity}
          title="No Project Selected"
          description="Select an active project or challenge to monitor milestone execution and lifecycle risks."
          actionLabel="View Validation Queue"
          actionTo="/government-dashboard"
        />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        <SkeletonCard count={2} />
      </div>
    );
  }

  if (error && !project) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16">
        <ErrorState
          title="Failed to Load Lifecycle Data"
          message={error}
          onRetry={refetch}
        />
      </div>
    );
  }

  if (!project) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16">
        <EmptyState
          icon={Layers}
          title="Project Lifecycle Not Started"
          description="A project has not been initialized for this mandate yet. Milestone tracking will activate once the university submits an accepted proposal."
          actionLabel="Go to University Workspace"
          actionTo="/university-workspace"
        />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-panel p-6 rounded-3xl border border-blue-500/30">
        <div>
          <div className="flex items-center space-x-2">
            <Badge variant="primary">Screen 08 • Project Lifecycle & Risk Intelligence</Badge>
            <span className="text-xs text-slate-400 font-mono">{project.code || project.id}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white mt-1 font-display">
            Milestone Tracking & Execution Roadmap
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Monitor real-world prototype progress, task completion, and automated risk alerts throughout the innovation cycle.
          </p>
        </div>

        <button
          onClick={handleProceedToImpact}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-400 hover:from-emerald-400 hover:to-teal-300 text-slate-950 font-black text-xs flex items-center space-x-2 shadow-glow-emerald"
        >
          <span>Evidence-Based Impact Dashboard</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Dynamic Lifecycle Progress Line */}
      <LifecycleProgressBar 
        statusKey={project.currentStage || "PROTOTYPE_BUILT"} 
        title={project.name}
      />

      {/* 2-Column: Milestones vs AI Risk Intelligence */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Col 1 & 2: Interactive Milestones */}
        <div className="lg:col-span-2 glass-card rounded-3xl p-6 border border-navy-700 space-y-4">
          <div className="flex items-center justify-between border-b border-navy-700 pb-3">
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                Project Milestones ({project.milestones?.length || 0})
              </h3>
              <p className="text-xs text-slate-400">Mark completed milestones as deliverables are verified</p>
            </div>
            {project.progressPercentage !== undefined && (
              <Badge variant="teal">Overall: {project.progressPercentage}%</Badge>
            )}
          </div>

          {!Array.isArray(project.milestones) || project.milestones.length === 0 ? (
            <p className="text-xs text-slate-400 py-8 text-center">
              No milestones defined for this project yet.
            </p>
          ) : (
            <div className="space-y-3">
              {project.milestones.map((m) => {
                const isDone = m.status === 'COMPLETED';

                return (
                  <div 
                    key={m.id}
                    className={`p-4 rounded-2xl border transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
                      isDone 
                        ? 'bg-navy-850/60 border-emerald-500/20' 
                        : 'bg-navy-850 border-navy-700'
                    }`}
                  >
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-mono font-bold text-amber-400">{m.id}</span>
                        <h4 className="text-xs font-bold text-white">{m.title}</h4>
                        {isDone ? (
                          <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold">
                            Complete ✓
                          </span>
                        ) : (
                          <span className="text-[10px] px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-bold">
                            {m.progress ? `${m.progress}%` : "Pending"}
                          </span>
                        )}
                      </div>
                      {m.dueDate && (
                        <p className="text-[11px] text-slate-400">Target Date: {m.dueDate}</p>
                      )}
                    </div>

                    {!isDone && (
                      <button
                        onClick={() => handleMilestoneComplete(m.id)}
                        disabled={updatingMilestoneId === m.id}
                        className="px-3.5 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold flex items-center space-x-1.5 shrink-0 transition-all disabled:opacity-50"
                      >
                        {updatingMilestoneId === m.id ? (
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        ) : (
                          <Zap className="w-3.5 h-3.5 text-amber-300" />
                        )}
                        <span>Verify & Mark Complete</span>
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Col 3: AI Risk & Alerts */}
        <div className="space-y-6">
          <div className="glass-card rounded-3xl p-6 border border-navy-700 space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 flex items-center space-x-2 border-b border-navy-800 pb-3">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <span>Project Risk Intelligence</span>
            </h3>

            {!Array.isArray(project.risks) || project.risks.length === 0 ? (
              <p className="text-xs text-slate-400 py-4 leading-relaxed">
                No active schedule risks or seasonal bottlenecks flagged for this project.
              </p>
            ) : (
              <div className="space-y-3">
                {project.risks.map((risk, idx) => (
                  <div key={idx} className="p-3.5 rounded-2xl bg-navy-850 border border-amber-500/30 space-y-1">
                    <span className="text-xs font-bold text-amber-300 block">{risk.title || "Seasonal Delay Alert"}</span>
                    <p className="text-[11px] text-slate-300 leading-relaxed">{risk.description || risk}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

      </div>

    </div>
  );
};
