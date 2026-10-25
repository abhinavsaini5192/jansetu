import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useJanSetu } from '../../context/JanSetuContext';
import { useProject } from '../../hooks/useProject';
import { Badge } from '../common/Badge';
import { SkeletonCard } from '../states/SkeletonCard';
import { EmptyState } from '../states/EmptyState';
import { ErrorState } from '../states/ErrorState';
import { 
  Building2, 
  GraduationCap, 
  Users, 
  FileText, 
  CheckCircle2, 
  Clock, 
  ArrowRight, 
  Briefcase, 
  Plus,
  Loader2
} from 'lucide-react';

export const UniversityWorkspace = () => {
  const { activeChallengeId, activeProjectId, showToast } = useJanSetu();
  const identifier = activeProjectId || activeChallengeId || 'proj-jalkavach-01';
  const isChallenge = Boolean(activeChallengeId && !activeProjectId);

  const { project, loading, error, createProject, refetch } = useProject(identifier, isChallenge);
  const navigate = useNavigate();

  const [showProposalModal, setShowProposalModal] = useState(false);
  const [proposalForm, setProposalForm] = useState({
    name: "",
    institutionName: "",
    department: "",
    leadFaculty: "",
    studentLead: "",
    budget: "",
    summary: ""
  });
  const [isSubmittingProposal, setIsSubmittingProposal] = useState(false);

  const handleCreateProposal = async (e) => {
    e.preventDefault();
    setIsSubmittingProposal(true);
    try {
      await createProject({
        ...proposalForm,
        challengeId: activeChallengeId,
      });
      showToast("Project proposal created successfully.", "success");
      setShowProposalModal(false);
    } catch (err) {
      showToast(err.message || "Failed to create project proposal.", "error");
    } finally {
      setIsSubmittingProposal(false);
    }
  };

  const handleProceedToIndustry = () => {
    navigate('/industry-collaboration');
  };

  if (!identifier) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16">
        <EmptyState
          icon={Building2}
          title="No Active Project Selected"
          description="Select an accepted challenge or active project from your dashboard to view the university research workspace."
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
          title="Failed to Load Project Workspace"
          message={error}
          onRetry={refetch}
        />
      </div>
    );
  }

  if (!project) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 space-y-6">
        <EmptyState
          icon={GraduationCap}
          title="No Project Workspace Initialized"
          description="You haven't adopted a challenge or initialized a research project for this problem yet. Browse AI-recommended problems matching your university labs to adopt a challenge."
          actionLabel="Browse Recommended Challenges"
          onAction={() => navigate('/university-matching')}
        />

        {showProposalModal && (
          <div className="saas-panel p-6 rounded-3xl border border-white/[0.08] space-y-4">
            <h3 className="text-base font-bold text-white">Initialize Project Proposal</h3>
            <form onSubmit={handleCreateProposal} className="space-y-4">
              <div>
                <label className="text-xs text-slate-300 font-semibold block mb-1">Project Name *</label>
                <input
                  type="text"
                  required
                  value={proposalForm.name}
                  onChange={e => setProposalForm({ ...proposalForm, name: e.target.value })}
                  placeholder="e.g., IoT Groundwater Contamination Monitor"
                  className="w-full px-3 py-2 rounded-xl bg-navy-850 border border-navy-700 text-xs text-white"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs text-slate-300 font-semibold block mb-1">Lead University *</label>
                  <input
                    type="text"
                    required
                    value={proposalForm.institutionName}
                    onChange={e => setProposalForm({ ...proposalForm, institutionName: e.target.value })}
                    placeholder="e.g., BIT Mesra / BAU Ranchi"
                    className="w-full px-3 py-2 rounded-xl bg-navy-850 border border-navy-700 text-xs text-white"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-300 font-semibold block mb-1">Faculty Mentor *</label>
                  <input
                    type="text"
                    required
                    value={proposalForm.leadFaculty}
                    onChange={e => setProposalForm({ ...proposalForm, leadFaculty: e.target.value })}
                    placeholder="e.g., Dr. R. K. Sinha"
                    className="w-full px-3 py-2 rounded-xl bg-navy-850 border border-navy-700 text-xs text-white"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowProposalModal(false)}
                  className="px-4 py-2 rounded-xl bg-navy-800 text-xs font-semibold text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingProposal}
                  className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs"
                >
                  {isSubmittingProposal ? "Creating..." : "Save Proposal"}
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-in fade-in">
      
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-5 saas-panel p-6 sm:p-8 rounded-3xl relative overflow-hidden">
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <span className="saas-badge bg-cyan-500/10 text-cyan-300 border-cyan-500/30">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
              UNIVERSITY & RESEARCH WORKSPACE
            </span>
            <span className="text-xs text-slate-400 font-mono">{project.code || project.id}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white font-display tracking-tight">
            Project Execution & Multidisciplinary Roster
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 max-w-xl leading-relaxed">
            Accepted challenges are executed by interdisciplinary student-faculty teams combining technical engineering, domain science, and rural field extension.
          </p>
        </div>

        <button
          onClick={handleProceedToIndustry}
          className="btn-saas-primary px-5 py-2.5 rounded-xl text-xs font-bold flex items-center space-x-2 shrink-0"
        >
          <span>Industry & CSR Collaboration</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Project Master Card */}
      <div className="saas-panel rounded-3xl p-6 sm:p-8 border border-white/[0.1] space-y-7">
        
        {/* Header with Title and Status */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-5 border-b border-white/[0.08] pb-6">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              {project.code && (
                <span className="font-mono text-xs font-bold text-blue-300 bg-black/40 px-2.5 py-1 rounded-lg border border-white/[0.08]">
                  {project.code}
                </span>
              )}
              <Badge variant="success" dot={true}>Active Project</Badge>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-white font-display">
              {project.name}
            </h2>
            <p className="text-xs text-slate-300 flex items-center space-x-2">
              <span className="text-teal-400 font-semibold">{project.institutionName || project.institution}</span>
              {project.department && <span>•</span>}
              <span className="text-slate-400">{project.department}</span>
            </p>
          </div>

          <div className="text-left lg:text-right">
            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block">Overall Execution Progress</span>
            <div className="flex items-center lg:justify-end space-x-2 mt-1">
              <span className="text-3xl font-black text-emerald-400 font-mono tracking-tight">
                {project.progressPercentage !== undefined ? `${project.progressPercentage}%` : "—"}
              </span>
            </div>
          </div>
        </div>

        {/* Project Meta Info */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-xs">
          <div className="p-4 rounded-xl saas-card">
            <span className="text-slate-400 block text-[10px] font-semibold uppercase tracking-wider">Faculty Mentor</span>
            <strong className="text-white block mt-1 text-sm font-semibold">{project.leadFaculty || "Unassigned"}</strong>
          </div>

          <div className="p-4 rounded-xl saas-card">
            <span className="text-slate-400 block text-[10px] font-semibold uppercase tracking-wider">Student Team Lead</span>
            <strong className="text-white block mt-1 text-sm font-semibold">{project.studentLead || "Unassigned"}</strong>
          </div>

          <div className="p-4 rounded-xl saas-card">
            <span className="text-slate-400 block text-[10px] font-semibold uppercase tracking-wider">Allocated Budget</span>
            <strong className="text-amber-400 block mt-1 text-sm font-mono">{project.budget || "Under Review"}</strong>
          </div>

          <div className="p-4 rounded-xl saas-card">
            <span className="text-slate-400 block text-[10px] font-semibold uppercase tracking-wider">Current Stage</span>
            <strong className="text-emerald-400 block mt-1 text-sm font-semibold">{project.currentStage || "In Development"}</strong>
          </div>
        </div>

        {/* Multidisciplinary Team Grid */}
        {Array.isArray(project.teamMembers) && project.teamMembers.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-2">
              <Users className="w-4 h-4 text-blue-400" />
              <span>Multidisciplinary Roster ({project.teamMembers.length} Members)</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {project.teamMembers.map((member, i) => (
                <div key={i} className="p-4 rounded-2xl saas-card space-y-1.5">
                  <div className="flex items-center justify-between">
                    <strong className="text-xs font-bold text-white">{member.name}</strong>
                    {member.role && <Badge variant="primary" size="sm" dot={true}>{member.role}</Badge>}
                  </div>
                  {member.dept && <p className="text-[11px] text-slate-400">{member.dept}</p>}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Proposal Summary */}
        {project.proposalSummary && (
          <div className="p-6 rounded-2xl saas-card space-y-2">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2 font-display">
              <FileText className="w-4 h-4 text-teal-400" />
              <span>Technical Solution Proposal</span>
            </h3>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-normal">
              {project.proposalSummary}
            </p>
          </div>
        )}

        {/* Milestones */}
        {Array.isArray(project.milestones) && project.milestones.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-2">
              <Clock className="w-4 h-4 text-amber-400" />
              <span>Project Milestones & Deliverables</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {project.milestones.map((m) => (
                <div 
                  key={m.id} 
                  className="p-4 rounded-2xl saas-card space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono text-slate-400 font-bold">{m.id}</span>
                    <Badge variant={m.status === 'COMPLETED' ? 'success' : 'primary'} size="sm" dot={true}>
                      {m.status || "Pending"}
                    </Badge>
                  </div>
                  <h4 className="text-xs font-bold text-slate-200">{m.title}</h4>
                  {m.dueDate && <p className="text-[10px] text-slate-500 font-mono">Target: {m.dueDate}</p>}
                </div>
              ))}
            </div>
          </div>
        )}

      </div>

    </div>
  );
};
