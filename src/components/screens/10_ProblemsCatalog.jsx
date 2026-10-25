import React, { useState, useMemo } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useJanSetu } from '../../context/JanSetuContext';
import { useAuth } from '../../context/AuthContext';
import { useChallenges } from '../../hooks/useChallenges';
import { challengeService } from '../../services/challengeService';
import { JHARKHAND_DISTRICTS, DOMAINS, URGENCY_LEVELS } from '../../config/constants';
import { Badge } from '../common/Badge';
import { SkeletonCard } from '../states/SkeletonCard';
import { EmptyState } from '../states/EmptyState';
import { ErrorState } from '../states/ErrorState';
import { 
  Search, 
  Filter, 
  MapPin, 
  Users, 
  Clock, 
  Sparkles, 
  GraduationCap, 
  ArrowRight, 
  ShieldCheck, 
  AlertTriangle, 
  FileText, 
  Layers, 
  Eye, 
  X, 
  Send, 
  RotateCcw,
  CheckCircle2,
  Building2,
  Calendar,
  ChevronRight,
  TrendingUp,
  Tag,
  Lock,
  Edit3,
  Trash2,
  CheckCircle,
  UserCheck,
  Save,
  AlertCircle
} from 'lucide-react';

export const ProblemsCatalog = () => {
  const { language, setActiveChallengeId, showToast } = useJanSetu();
  const { user, isAuthenticated, isOfficial } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { challenges, loading, error, refetch } = useChallenges();

  // Active view tab: "all" or "my_problems"
  const activeTab = searchParams.get('tab') === 'my_problems' ? 'my_problems' : 'all';

  // Search & Filter State
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedDomain, setSelectedDomain] = useState("ALL");
  const [selectedDistrict, setSelectedDistrict] = useState("ALL");
  const [selectedStatus, setSelectedStatus] = useState("ALL");
  const [selectedUrgency, setSelectedUrgency] = useState("ALL");
  const [sortBy, setSortBy] = useState("newest");

  // Selected challenge for detail/tracking modal
  const [selectedProblem, setSelectedProblem] = useState(null);

  // Edit Problem State
  const [editingProblem, setEditingProblem] = useState(null);
  const [editFormData, setEditFormData] = useState({
    title: "",
    description: "",
    urgency: "MEDIUM",
    status: "SUBMITTED",
  });
  const [isSavingEdit, setIsSavingEdit] = useState(false);

  // Status styling map
  const getStatusBadgeVariant = (status) => {
    const s = (status || "").toLowerCase();
    if (s === 'validated') return 'success';
    if (s === 'under_review' || s === 'pending') return 'warning';
    if (s === 'assigned' || s === 'assigned_hei') return 'teal';
    if (s === 'resolved') return 'success';
    if (s === 'rejected') return 'danger';
    if (s === 'duplicate') return 'secondary';
    return 'primary';
  };

  const getUrgencyBadge = (urgency) => {
    const u = (urgency || "").toLowerCase();
    if (u === 'critical') {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30 animate-pulse">
          Critical Urgency
        </span>
      );
    }
    if (u === 'high') {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30">
          High Priority
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-blue-500/10 text-blue-300 border border-blue-500/20">
        Standard Window
      </span>
    );
  };

  // Helper: check if a challenge belongs to the logged-in citizen
  const isUserProblem = (problem) => {
    if (!user) return false;
    if (problem.submitted_by_user_id && String(problem.submitted_by_user_id) === String(user.id)) return true;
    if (problem.submitter_email && user.email && problem.submitter_email.toLowerCase() === user.email.toLowerCase()) return true;
    if (problem.is_user_submitted && !isOfficial) return true;
    // For demo testing when logged in as citizen@jansetu.gov.in, pair with arsenic challenge as demo anchor
    if (user.email === "citizen@jansetu.gov.in" && (problem.id.includes("arsenic") || problem.is_user_submitted)) return true;
    return false;
  };

  // Filter and Sort Logic
  const filteredProblems = useMemo(() => {
    if (!Array.isArray(challenges)) return [];

    return challenges
      .filter((item) => {
        // Tab filter: "my_problems" vs "all"
        if (activeTab === 'my_problems') {
          if (!isUserProblem(item)) return false;
        }

        // Search query
        if (searchQuery.trim()) {
          const q = searchQuery.toLowerCase();
          const title = (item.title || "").toLowerCase();
          const titleHi = (item.title_hi || item.titleHi || "").toLowerCase();
          const desc = (item.description || "").toLowerCase();
          const district = (item.district || item.location?.district || "").toLowerCase();
          const ref = (item.reference_code || item.referenceCode || item.id || "").toLowerCase();
          const domain = (item.domain || "").toLowerCase();

          if (!title.includes(q) && !titleHi.includes(q) && !desc.includes(q) && !district.includes(q) && !ref.includes(q) && !domain.includes(q)) {
            return false;
          }
        }

        // Domain filter
        if (selectedDomain !== "ALL") {
          const itemDomain = (item.domain || "").toLowerCase();
          if (itemDomain !== selectedDomain.toLowerCase()) return false;
        }

        // District filter
        if (selectedDistrict !== "ALL") {
          const itemDistrict = item.district || item.location?.district || "";
          if (itemDistrict.toLowerCase() !== selectedDistrict.toLowerCase()) return false;
        }

        // Status filter
        if (selectedStatus !== "ALL") {
          const itemStatus = (item.validation_status || item.status || "").toLowerCase();
          if (itemStatus !== selectedStatus.toLowerCase()) return false;
        }

        // Urgency filter
        if (selectedUrgency !== "ALL") {
          const itemUrgency = (item.urgency || "").toLowerCase();
          if (itemUrgency !== selectedUrgency.toLowerCase()) return false;
        }

        return true;
      })
      .sort((a, b) => {
        if (sortBy === "newest") {
          const dateA = new Date(a.submitted_at || a.submittedAt || a.created_at || 0);
          const dateB = new Date(b.submitted_at || b.submittedAt || b.created_at || 0);
          return dateB - dateA;
        }
        if (sortBy === "urgency") {
          const urgencyOrder = { critical: 4, high: 3, medium: 2, low: 1 };
          const uA = urgencyOrder[(a.urgency || "").toLowerCase()] || 0;
          const uB = urgencyOrder[(b.urgency || "").toLowerCase()] || 0;
          return uB - uA;
        }
        if (sortBy === "title") {
          return (a.title || "").localeCompare(b.title || "");
        }
        return 0;
      });
  }, [challenges, activeTab, searchQuery, selectedDomain, selectedDistrict, selectedStatus, selectedUrgency, sortBy, user]);

  // Aggregate stats
  const totalCount = challenges?.length || 0;
  const myProblemsCount = challenges?.filter(c => isUserProblem(c)).length || 0;
  const validatedCount = challenges?.filter(c => (c.validation_status || c.status || "").toLowerCase() === 'validated').length || 0;
  const underReviewCount = challenges?.filter(c => ['under_review', 'pending', 'submitted'].includes((c.validation_status || c.status || "").toLowerCase())).length || 0;
  const uniqueDistricts = new Set(challenges?.map(c => c.district || c.location?.district).filter(Boolean)).size;

  const handleAction = (challengeId, route) => {
    if (!isOfficial) {
      showToast("Official administrative clearance required for this workspace.", "warning");
      navigate(`/login?redirect=${encodeURIComponent(route)}`);
      return;
    }
    setActiveChallengeId(challengeId);
    navigate(route);
  };

  const handleResetFilters = () => {
    setSearchQuery("");
    setSelectedDomain("ALL");
    setSelectedDistrict("ALL");
    setSelectedStatus("ALL");
    setSelectedUrgency("ALL");
    setSortBy("newest");
  };

  // Open Edit Dialog
  const handleOpenEdit = (problem, e) => {
    if (e) e.stopPropagation();
    setEditingProblem(problem);
    setEditFormData({
      title: problem.title || "",
      description: problem.description || "",
      urgency: problem.urgency || "MEDIUM",
      status: problem.validation_status || problem.status || "SUBMITTED",
    });
  };

  // Save Edit Changes
  const handleSaveEdit = async (e) => {
    e.preventDefault();
    if (!editingProblem) return;

    setIsSavingEdit(true);
    try {
      await challengeService.updateChallenge(editingProblem.id, {
        title: editFormData.title,
        description: editFormData.description,
        urgency: editFormData.urgency,
        validation_status: editFormData.status,
        status: editFormData.status,
      });
      showToast("Problem statement updated successfully.", "success");
      setEditingProblem(null);
      refetch();
    } catch (err) {
      showToast(err.message || "Failed to update problem statement.", "error");
    } finally {
      setIsSavingEdit(false);
    }
  };

  // Remove / Delete Problem
  const handleDeleteProblem = async (problemId, problemTitle, e) => {
    if (e) e.stopPropagation();
    const confirmed = window.confirm(`Are you sure you want to remove the problem: "${problemTitle}"? This will withdraw it from the platform.`);
    if (!confirmed) return;

    try {
      await challengeService.deleteChallenge(problemId);
      showToast("Problem statement removed successfully.", "info");
      if (selectedProblem?.id === problemId) setSelectedProblem(null);
      refetch();
    } catch (err) {
      showToast(err.message || "Failed to delete problem.", "error");
    }
  };

  // Mark as Resolved
  const handleMarkResolved = async (problem, e) => {
    if (e) e.stopPropagation();
    try {
      await challengeService.updateChallenge(problem.id, {
        validation_status: "RESOLVED",
        status: "RESOLVED",
      });
      showToast("Problem marked as Resolved! Verified by community.", "success");
      refetch();
    } catch (err) {
      showToast("Could not mark as resolved.", "error");
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-in fade-in">
      
      {/* Header and Call to Action */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-5 saas-panel p-6 sm:p-8 rounded-3xl relative overflow-hidden">
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <span className="saas-badge bg-blue-500/10 text-blue-300 border-blue-500/30">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse"></span>
              PUBLIC COMMUNITY REGISTRY
            </span>
            <span className="text-xs text-slate-400 font-mono">Jharkhand Open Innovation OS</span>
          </div>
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-black text-white tracking-tight font-display">
            Grassroots Problem Statements
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
            Transparent registry of citizen-reported challenges across 24 districts of Jharkhand. 
            Track community resolutions, examine solver matches, or report a local societal issue.
          </p>
        </div>

        <Link
          to="/citizen-portal"
          className="btn-saas-primary px-5 py-3 rounded-2xl text-xs font-bold flex items-center space-x-2 self-start md:self-center shrink-0"
        >
          <Send className="w-4 h-4" />
          <span>Report New Problem</span>
        </Link>
      </div>

      {/* Aggregate Statistics Ribbon */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="saas-card rounded-2xl p-4.5 flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-xl bg-blue-500/15 border border-blue-500/25 text-blue-400 flex items-center justify-center shrink-0">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <span className="text-2xl font-black text-white font-mono tracking-tight">{totalCount}</span>
            <p className="text-[11px] text-slate-400 font-medium">Total Uploaded</p>
          </div>
        </div>

        <div className="saas-card rounded-2xl p-4.5 flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/15 border border-emerald-500/25 text-emerald-400 flex items-center justify-center shrink-0">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <span className="text-2xl font-black text-emerald-300 font-mono tracking-tight">{validatedCount}</span>
            <p className="text-[11px] text-slate-400 font-medium">Govt Validated</p>
          </div>
        </div>

        <div className="saas-card rounded-2xl p-4.5 flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-xl bg-amber-500/15 border border-amber-500/25 text-amber-400 flex items-center justify-center shrink-0">
            <Clock className="w-5 h-5" />
          </div>
          <div>
            <span className="text-2xl font-black text-amber-300 font-mono tracking-tight">{underReviewCount}</span>
            <p className="text-[11px] text-slate-400 font-medium">Under Evaluation</p>
          </div>
        </div>

        <div className="saas-card rounded-2xl p-4.5 flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-xl bg-teal-500/15 border border-teal-500/25 text-teal-400 flex items-center justify-center shrink-0">
            <MapPin className="w-5 h-5" />
          </div>
          <div>
            <span className="text-2xl font-black text-teal-300 font-mono tracking-tight">{uniqueDistricts}</span>
            <p className="text-[11px] text-slate-400 font-medium">Districts Active</p>
          </div>
        </div>
      </div>

      {/* Primary View Switcher: All Problems vs My Reported Problems */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/[0.08] pb-3">
        <div className="flex items-center space-x-1.5 rounded-2xl bg-saas-dark border border-white/[0.08] p-1">
          <button
            onClick={() => setSearchParams({})}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 ${
              activeTab === 'all'
                ? 'btn-saas-primary text-white shadow-saas-card'
                : 'text-slate-400 hover:text-white hover:bg-white/[0.04]'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>All Community Problems</span>
            <span className="px-1.5 py-0.2 rounded bg-black/40 text-[10px] font-mono">
              {totalCount}
            </span>
          </button>

          <button
            onClick={() => {
              if (!isAuthenticated) {
                navigate('/login?redirect=/problems?tab=my_problems');
              } else {
                setSearchParams({ tab: 'my_problems' });
              }
            }}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 ${
              activeTab === 'my_problems'
                ? 'btn-saas-teal text-white shadow-saas-card'
                : 'text-slate-400 hover:text-white hover:bg-white/[0.04]'
            }`}
          >
            <UserCheck className="w-3.5 h-3.5" />
            <span>My Reported Problems</span>
            {isAuthenticated && (
              <span className="px-1.5 py-0.2 rounded bg-black/40 text-[10px] font-mono text-emerald-300">
                {myProblemsCount}
              </span>
            )}
          </button>
        </div>

        {activeTab === 'my_problems' && (
          <div className="text-xs text-emerald-400 font-medium flex items-center space-x-1.5 bg-emerald-500/10 px-3.5 py-1.5 rounded-xl border border-emerald-500/25">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Tracking & Management Mode: You can edit or remove your reported problems below.</span>
          </div>
        )}
      </div>

      {/* Filter and Search Panel */}
      <div className="saas-panel rounded-2xl p-5 border border-white/[0.08] space-y-4">
        {/* Search Bar */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search problems by keyword, reference code (e.g. JS-2026-W001), district, or domain..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl saas-input placeholder-slate-500 text-xs"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white text-xs"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Filter Pills Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-3 pt-1">
          {/* Domain Filter */}
          <div className="space-y-1">
            <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Domain</label>
            <select
              value={selectedDomain}
              onChange={(e) => setSelectedDomain(e.target.value)}
              className="w-full px-2.5 py-2 rounded-xl saas-input text-xs cursor-pointer"
            >
              <option value="ALL">All Domains</option>
              {DOMAINS.map(d => (
                <option key={d.id} value={d.id}>{d.label}</option>
              ))}
            </select>
          </div>

          {/* District Filter */}
          <div className="space-y-1">
            <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">District</label>
            <select
              value={selectedDistrict}
              onChange={(e) => setSelectedDistrict(e.target.value)}
              className="w-full px-2.5 py-2 rounded-xl saas-input text-xs cursor-pointer"
            >
              <option value="ALL">All 24 Districts</option>
              {JHARKHAND_DISTRICTS.map(d => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div className="space-y-1">
            <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Status</label>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="w-full px-2.5 py-2 rounded-xl saas-input text-xs cursor-pointer"
            >
              <option value="ALL">All Statuses</option>
              <option value="SUBMITTED">Submitted</option>
              <option value="UNDER_REVIEW">Under Review</option>
              <option value="VALIDATED">Validated</option>
              <option value="ASSIGNED">Adopted by HEI</option>
              <option value="RESOLVED">Resolved</option>
            </select>
          </div>

          {/* Urgency Filter */}
          <div className="space-y-1">
            <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Urgency</label>
            <select
              value={selectedUrgency}
              onChange={(e) => setSelectedUrgency(e.target.value)}
              className="w-full px-2.5 py-2 rounded-xl saas-input text-xs cursor-pointer"
            >
              <option value="ALL">All Urgencies</option>
              {URGENCY_LEVELS.map(u => (
                <option key={u.id} value={u.id}>{u.label}</option>
              ))}
            </select>
          </div>

          {/* Sort By & Reset */}
          <div className="space-y-1 col-span-2 sm:col-span-4 lg:col-span-1 flex items-end justify-between lg:justify-end gap-2">
            <div className="w-full">
              <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Sort By</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full px-2.5 py-2 rounded-xl saas-input text-xs cursor-pointer"
              >
                <option value="newest">Newest First</option>
                <option value="urgency">Highest Urgency</option>
                <option value="title">Title (A-Z)</option>
              </select>
            </div>

            <button
              onClick={handleResetFilters}
              title="Reset all filters"
              className="p-2.5 rounded-xl btn-saas-secondary transition-colors shrink-0"
            >
              <RotateCcw className="w-4 h-4 text-slate-400 hover:text-white" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Catalog Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((idx) => (
            <SkeletonCard key={idx} />
          ))}
        </div>
      ) : error ? (
        <ErrorState message={error} onRetry={refetch} />
      ) : filteredProblems.length === 0 ? (
        activeTab === 'my_problems' ? (
          <div className="p-12 text-center rounded-3xl saas-panel border border-white/[0.08] space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto">
              <UserCheck className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white font-display">No Reported Challenges Found</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
              You haven't reported any problems under this account yet. When you submit a challenge through the Citizen Portal, you will be able to track its progress, edit details, or remove it here.
            </p>
            <Link
              to="/citizen-portal"
              className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl btn-saas-primary text-xs font-bold"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Report Your First Challenge</span>
            </Link>
          </div>
        ) : (
          <EmptyState
            title="No matching problem statements found"
            description="Try modifying search keywords or resetting filters to view all civic challenges."
            actionLabel="Reset Filters"
            onAction={handleResetFilters}
          />
        )
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProblems.map((problem) => {
            const isOwner = isUserProblem(problem);
            const refCode = problem.reference_code || problem.referenceCode || problem.id;
            const districtStr = problem.district || problem.location?.district || "Jharkhand";
            const blockStr = problem.block || problem.location?.block || problem.village_or_ward || "";
            const beneficiaries = problem.estimated_beneficiaries || problem.affected_population;
            const submittedDate = problem.submitted_at || problem.submittedAt || problem.created_at;
            const statusStr = problem.validation_status || problem.status || "SUBMITTED";

            return (
              <div
                key={problem.id}
                className={`saas-card rounded-2xl p-5 border flex flex-col justify-between transition-all duration-300 relative overflow-hidden group ${
                  isOwner ? 'border-emerald-500/40 bg-emerald-950/10' : 'border-white/[0.08]'
                }`}
              >
                {/* Specular Urgency Indicator Accent Line */}
                <div className={`absolute top-0 left-0 right-0 h-[2px] ${
                  (problem.urgency || '').toLowerCase() === 'critical'
                    ? 'bg-gradient-to-r from-rose-500 via-red-500 to-rose-600'
                    : (problem.urgency || '').toLowerCase() === 'high'
                    ? 'bg-gradient-to-r from-amber-400 via-orange-500 to-amber-500'
                    : 'bg-gradient-to-r from-blue-500 via-indigo-500 to-teal-400'
                }`} />

                {/* Card Header: Reference Code & Status */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center space-x-1.5">
                      <span className="font-mono text-[11px] font-bold text-amber-300 bg-black/40 px-2 py-0.5 rounded-lg border border-white/[0.08] tracking-wider">
                        {refCode}
                      </span>
                      {isOwner && (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                          My Report
                        </span>
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-1.5">
                      {getUrgencyBadge(problem.urgency)}
                      <Badge variant={getStatusBadgeVariant(statusStr)} dot={true}>
                        {statusStr}
                      </Badge>
                    </div>
                  </div>

                  {/* Title */}
                  <div>
                    <h3 className="text-base font-bold text-slate-100 group-hover:text-blue-400 transition-colors line-clamp-2 leading-snug">
                      {problem.title}
                    </h3>
                    {problem.title_hi && (
                      <p className="text-xs text-slate-400 font-medium mt-0.5 line-clamp-1">
                        {problem.title_hi}
                      </p>
                    )}
                  </div>

                  {/* Description Snippet */}
                  <p className="text-xs text-slate-300 line-clamp-3 leading-relaxed font-normal">
                    {problem.description}
                  </p>

                  {/* Metadata Chips */}
                  <div className="pt-2.5 border-t border-white/[0.08] space-y-2 text-xs">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-white/[0.04] text-blue-300 text-[11px] border border-white/[0.06]">
                        <Tag className="w-3 h-3 text-blue-400" />
                        <span className="font-semibold capitalize">{problem.domain || "General"}</span>
                      </span>

                      <span className="inline-flex items-center space-x-1 text-slate-400 text-[11px]">
                        <MapPin className="w-3 h-3 text-emerald-400 shrink-0" />
                        <span className="truncate max-w-[130px] font-medium">
                          {districtStr}{blockStr ? `, ${blockStr}` : ''}
                        </span>
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
                      {beneficiaries ? (
                        <span className="flex items-center space-x-1 text-teal-300">
                          <Users className="w-3 h-3 shrink-0" />
                          <span className="truncate max-w-[140px]">{beneficiaries}</span>
                        </span>
                      ) : (
                        <span className="text-slate-400">Community impact</span>
                      )}

                      {submittedDate && (
                        <span className="flex items-center space-x-1 font-mono text-[10px]">
                          <Clock className="w-3 h-3 text-slate-400" />
                          <span>{new Date(submittedDate).toLocaleDateString()}</span>
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Card Action Buttons */}
                <div className="pt-4 mt-4 border-t border-white/[0.08] space-y-2">
                  
                  {/* Official Action Buttons (Only for authenticated officials) */}
                  {isOfficial && (
                    <div className="grid grid-cols-2 gap-2">
                      <button
                        onClick={() => handleAction(problem.id, '/ai-intelligence')}
                        className="w-full py-2 px-3 rounded-xl btn-saas-secondary text-blue-300 text-xs font-semibold flex items-center justify-center space-x-1.5"
                      >
                        <Sparkles className="w-3.5 h-3.5 text-blue-400" />
                        <span>AI Insights</span>
                      </button>

                      <button
                        onClick={() => handleAction(problem.id, '/university-matching')}
                        className="w-full py-2 px-3 rounded-xl btn-saas-secondary text-teal-300 text-xs font-semibold flex items-center justify-center space-x-1.5"
                      >
                        <GraduationCap className="w-3.5 h-3.5 text-teal-400" />
                        <span>HEI Matches</span>
                      </button>
                    </div>
                  )}

                  {/* Citizen Owner Actions: Edit, Delete, Mark Resolved */}
                  {isOwner && (
                    <div className="grid grid-cols-2 gap-2 pb-1">
                      <button
                        onClick={(e) => handleOpenEdit(problem, e)}
                        className="py-1.5 px-3 rounded-xl btn-saas-amber text-xs font-semibold flex items-center justify-center space-x-1.5"
                      >
                        <Edit3 className="w-3.5 h-3.5" />
                        <span>Edit Problem</span>
                      </button>

                      <button
                        onClick={(e) => handleDeleteProblem(problem.id, problem.title, e)}
                        className="py-1.5 px-3 rounded-xl btn-saas-danger text-xs font-semibold flex items-center justify-center space-x-1.5"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                        <span>Remove / Delete</span>
                      </button>
                    </div>
                  )}

                  <button
                    onClick={() => setSelectedProblem(problem)}
                    className="w-full py-2.5 px-3 rounded-xl btn-saas-secondary text-slate-200 hover:text-white text-xs font-semibold flex items-center justify-center space-x-2 shadow-sm"
                  >
                    <Eye className="w-3.5 h-3.5 text-blue-400" />
                    <span>{isOwner ? "Track Status & Dossier" : "View Problem Dossier"}</span>
                  </button>
                </div>

              </div>
            );
          })}
        </div>
      )}

      {/* Detailed Tracking Dossier Modal */}
      {selectedProblem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in">
          <div className="saas-panel w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-3xl p-6 sm:p-8 space-y-6 shadow-2xl relative border border-white/[0.12]">
            
            {/* Close Button */}
            <button
              onClick={() => setSelectedProblem(null)}
              className="absolute top-6 right-6 p-2 rounded-xl btn-saas-secondary transition-colors"
            >
              <X className="w-4 h-4 text-slate-400 hover:text-white" />
            </button>

            {/* Modal Header */}
            <div className="space-y-2 pr-10">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-xs font-bold text-amber-300 bg-black/40 px-2.5 py-1 rounded-lg border border-white/[0.08]">
                  {selectedProblem.reference_code || selectedProblem.referenceCode || selectedProblem.id}
                </span>
                <Badge variant={getStatusBadgeVariant(selectedProblem.validation_status || selectedProblem.status)} dot={true}>
                  {selectedProblem.validation_status || selectedProblem.status}
                </Badge>
                {getUrgencyBadge(selectedProblem.urgency)}
                {isUserProblem(selectedProblem) && (
                  <span className="text-[10px] font-bold px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                    Your Reported Problem
                  </span>
                )}
              </div>
              <h2 className="text-xl sm:text-2xl font-bold text-white font-display">
                {selectedProblem.title}
              </h2>
              {selectedProblem.title_hi && (
                <p className="text-sm text-slate-400 font-medium">
                  {selectedProblem.title_hi}
                </p>
              )}
            </div>

            {/* Lifecycle Progress Tracking Timeline */}
            <div className="p-4 rounded-2xl saas-card space-y-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-1.5">
                <TrendingUp className="w-3.5 h-3.5 text-blue-400" />
                <span>Live State Resolution Pipeline:</span>
              </span>

              <div className="grid grid-cols-4 gap-2 text-center text-[10px] font-mono">
                <div className="p-2.5 rounded-xl bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                  <CheckCircle className="w-3.5 h-3.5 mx-auto mb-1 text-emerald-400" />
                  <span>1. Submitted</span>
                </div>
                <div className={`p-2.5 rounded-xl border ${
                  ['under_review', 'validated', 'assigned', 'resolved'].includes((selectedProblem.validation_status || selectedProblem.status || '').toLowerCase())
                    ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                    : 'bg-black/30 text-slate-500 border-white/[0.06]'
                }`}>
                  <ShieldCheck className="w-3.5 h-3.5 mx-auto mb-1" />
                  <span>2. Govt Review</span>
                </div>
                <div className={`p-2.5 rounded-xl border ${
                  ['assigned', 'resolved'].includes((selectedProblem.validation_status || selectedProblem.status || '').toLowerCase())
                    ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                    : 'bg-black/30 text-slate-500 border-white/[0.06]'
                }`}>
                  <GraduationCap className="w-3.5 h-3.5 mx-auto mb-1" />
                  <span>3. HEI Adopted</span>
                </div>
                <div className={`p-2.5 rounded-xl border ${
                  (selectedProblem.validation_status || selectedProblem.status || '').toLowerCase() === 'resolved'
                    ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                    : 'bg-black/30 text-slate-500 border-white/[0.06]'
                }`}>
                  <CheckCircle2 className="w-3.5 h-3.5 mx-auto mb-1" />
                  <span>4. Resolved</span>
                </div>
              </div>
            </div>

            {/* Metadata Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 p-4 rounded-2xl saas-card text-xs">
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">Domain</span>
                <span className="font-bold text-white capitalize">{selectedProblem.domain || "General"}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">District</span>
                <span className="font-bold text-emerald-400">{selectedProblem.district || selectedProblem.location?.district || "Jharkhand"}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">Block / Panchayat</span>
                <span className="font-bold text-white">{selectedProblem.block || selectedProblem.location?.block || selectedProblem.village_or_ward || "N/A"}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">Beneficiaries</span>
                <span className="font-bold text-teal-300">{selectedProblem.estimated_beneficiaries || selectedProblem.affected_population || "Community"}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">Department</span>
                <span className="font-bold text-slate-300">{selectedProblem.assigned_department || "Pending Assignment"}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">Submitted Date</span>
                <span className="font-bold text-slate-300 font-mono text-[11px]">
                  {selectedProblem.submitted_at ? new Date(selectedProblem.submitted_at).toLocaleDateString() : "Recent"}
                </span>
              </div>
            </div>

            {/* Description */}
            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-1.5">
                <FileText className="w-3.5 h-3.5 text-blue-400" />
                <span>Problem Statement & Field Context</span>
              </h4>
              <p className="text-xs sm:text-sm text-slate-300 leading-relaxed p-4 rounded-2xl saas-input whitespace-pre-line">
                {selectedProblem.description}
              </p>
            </div>

            {/* Modal Actions */}
            <div className="pt-4 border-t border-white/[0.08]">
              
              {/* If owner citizen: offer direct Edit & Remove */}
              {isUserProblem(selectedProblem) && (
                <div className="flex flex-wrap items-center justify-between gap-3 p-3.5 rounded-2xl saas-card mb-3">
                  <div className="flex items-center space-x-2 text-xs text-slate-300">
                    <UserCheck className="w-4 h-4 text-emerald-400" />
                    <span>You are the verified submitter of this problem dossier.</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => {
                        const prob = selectedProblem;
                        setSelectedProblem(null);
                        handleOpenEdit(prob);
                      }}
                      className="px-3 py-1.5 rounded-xl btn-saas-amber text-xs font-semibold flex items-center space-x-1"
                    >
                      <Edit3 className="w-3 h-3" />
                      <span>Edit Statement</span>
                    </button>
                    <button
                      onClick={() => handleDeleteProblem(selectedProblem.id, selectedProblem.title)}
                      className="px-3 py-1.5 rounded-xl btn-saas-danger text-xs font-semibold flex items-center space-x-1"
                    >
                      <Trash2 className="w-3 h-3" />
                      <span>Remove</span>
                    </button>
                  </div>
                </div>
              )}

              {/* Official Controls (For authorized officials only) */}
              {isOfficial ? (
                <div className="flex flex-wrap items-center justify-end gap-3">
                  <button
                    onClick={() => {
                      setSelectedProblem(null);
                      handleAction(selectedProblem.id, '/ai-intelligence');
                    }}
                    className="px-4 py-2.5 rounded-xl btn-saas-primary text-xs font-semibold flex items-center space-x-2"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Analyze with AI</span>
                  </button>

                  <button
                    onClick={() => {
                      setSelectedProblem(null);
                      handleAction(selectedProblem.id, '/university-matching');
                    }}
                    className="px-4 py-2.5 rounded-xl btn-saas-teal text-xs font-semibold flex items-center space-x-2"
                  >
                    <GraduationCap className="w-3.5 h-3.5" />
                    <span>University Recommendations</span>
                  </button>

                  <button
                    onClick={() => {
                      setSelectedProblem(null);
                      handleAction(selectedProblem.id, '/government-dashboard');
                    }}
                    className="px-4 py-2.5 rounded-xl btn-saas-secondary text-xs font-semibold flex items-center space-x-2"
                  >
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>Govt Desk</span>
                  </button>
                </div>
              ) : !isAuthenticated ? (
                <div className="p-3.5 rounded-2xl saas-card flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
                  <div className="flex items-center space-x-2 text-slate-400 text-[11px]">
                    <Lock className="w-4 h-4 text-amber-400 shrink-0" />
                    <span>Log in to track your submissions, edit dossiers, or access official evaluation desks.</span>
                  </div>
                  <Link
                    to="/login"
                    onClick={() => setSelectedProblem(null)}
                    className="px-4 py-2 rounded-xl btn-saas-primary text-xs font-semibold shrink-0"
                  >
                    Sign In to Platform
                  </Link>
                </div>
              ) : null}
            </div>

          </div>
        </div>
      )}

      {/* Edit Problem Dialog Modal (For Submitting Citizens) */}
      {editingProblem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in">
          <div className="saas-panel w-full max-w-lg rounded-3xl p-6 sm:p-8 space-y-5 shadow-2xl relative border border-white/[0.12]">
            <button
              onClick={() => setEditingProblem(null)}
              className="absolute top-6 right-6 p-2 rounded-xl btn-saas-secondary"
            >
              <X className="w-4 h-4 text-slate-400 hover:text-white" />
            </button>

            <div className="space-y-1">
              <span className="text-[10px] font-mono uppercase font-bold text-amber-400">
                CITIZEN MANAGEMENT CONTROLS
              </span>
              <h3 className="text-lg font-bold text-white font-display">
                Edit Community Problem Statement
              </h3>
            </div>

            <form onSubmit={handleSaveEdit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Challenge Title</label>
                <input
                  type="text"
                  required
                  value={editFormData.title}
                  onChange={(e) => setEditFormData({ ...editFormData, title: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl saas-input text-xs"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Detailed Description / Observations</label>
                <textarea
                  rows={4}
                  required
                  value={editFormData.description}
                  onChange={(e) => setEditFormData({ ...editFormData, description: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl saas-input text-xs resize-y"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-300">Urgency Window</label>
                  <select
                    value={editFormData.urgency}
                    onChange={(e) => setEditFormData({ ...editFormData, urgency: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl saas-input text-xs cursor-pointer"
                  >
                    {URGENCY_LEVELS.map(u => (
                      <option key={u.id} value={u.id}>{u.label}</option>
                    ))}
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-300">Community Status</label>
                  <select
                    value={editFormData.status}
                    onChange={(e) => setEditFormData({ ...editFormData, status: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl saas-input text-xs cursor-pointer"
                  >
                    <option value="SUBMITTED">Submitted</option>
                    <option value="UNDER_REVIEW">Under Review</option>
                    <option value="RESOLVED">Resolved (Solved by Community/Govt)</option>
                  </select>
                </div>
              </div>

              <div className="pt-3 border-t border-white/[0.08] flex items-center justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setEditingProblem(null)}
                  className="px-4 py-2 rounded-xl btn-saas-secondary text-xs font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSavingEdit}
                  className="px-5 py-2 rounded-xl btn-saas-primary text-xs font-bold flex items-center space-x-1.5 disabled:opacity-50"
                >
                  <Save className="w-3.5 h-3.5" />
                  <span>{isSavingEdit ? "Saving..." : "Save Changes"}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};
