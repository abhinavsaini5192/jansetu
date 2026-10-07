import React, { useState, useMemo } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useJanSetu } from '../../context/JanSetuContext';
import { useChallenges } from '../../hooks/useChallenges';
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
  Tag
} from 'lucide-react';

export const ProblemsCatalog = () => {
  const { language, setActiveChallengeId, showToast } = useJanSetu();
  const navigate = useNavigate();
  const { challenges, loading, error, refetch } = useChallenges();

  // Search & Filter State
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedDomain, setSelectedDomain] = useState("ALL");
  const [selectedDistrict, setSelectedDistrict] = useState("ALL");
  const [selectedStatus, setSelectedStatus] = useState("ALL");
  const [selectedUrgency, setSelectedUrgency] = useState("ALL");
  const [sortBy, setSortBy] = useState("newest"); // "newest", "urgency", "title"

  // Selected challenge for detail modal
  const [selectedProblem, setSelectedProblem] = useState(null);

  // Status styling map
  const getStatusBadgeVariant = (status) => {
    const s = (status || "").toLowerCase();
    if (s === 'validated') return 'success';
    if (s === 'under_review' || s === 'pending') return 'warning';
    if (s === 'assigned') return 'teal';
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
    if (u === 'medium') {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-blue-500/20 text-blue-300 border border-blue-500/30">
          Medium
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-slate-500/20 text-slate-300 border border-slate-500/30">
        Standard
      </span>
    );
  };

  // Filter and Sort Logic
  const filteredProblems = useMemo(() => {
    if (!Array.isArray(challenges)) return [];

    return challenges
      .filter((item) => {
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
  }, [challenges, searchQuery, selectedDomain, selectedDistrict, selectedStatus, selectedUrgency, sortBy]);

  // Aggregate stats
  const totalCount = challenges?.length || 0;
  const validatedCount = challenges?.filter(c => (c.validation_status || c.status || "").toLowerCase() === 'validated').length || 0;
  const underReviewCount = challenges?.filter(c => ['under_review', 'pending', 'submitted'].includes((c.validation_status || c.status || "").toLowerCase())).length || 0;
  const uniqueDistricts = new Set(challenges?.map(c => c.district || c.location?.district).filter(Boolean)).size;

  const handleAction = (challengeId, route) => {
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

  const hasActiveFilters = searchQuery !== "" || selectedDomain !== "ALL" || selectedDistrict !== "ALL" || selectedStatus !== "ALL" || selectedUrgency !== "ALL";

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Top Banner Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 glass-panel p-6 sm:p-8 rounded-3xl border border-navy-700/80">
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded text-[10px] font-mono font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20">
              COMMUNITY MANDATES
            </span>
            <span className="text-xs text-slate-400">Open Public Repository</span>
          </div>
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-black text-white tracking-tight font-display">
            Uploaded Societal Problems
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
            Browse and discover real grassroots challenges submitted by citizens and panchayats across Jharkhand. 
            Evaluate AI diagnostic intelligence, matching academia, and verified field impact.
          </p>
        </div>

        <Link
          to="/citizen-portal"
          className="px-5 py-3 rounded-2xl bg-gradient-to-r from-blue-600 via-indigo-600 to-teal-400 hover:from-blue-500 hover:to-teal-300 text-white font-bold text-xs flex items-center space-x-2 shadow-glow-sm hover:scale-105 transition-all self-start md:self-center shrink-0"
        >
          <Send className="w-4 h-4" />
          <span>Report New Problem</span>
        </Link>
      </div>

      {/* Aggregate Statistics Ribbon */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card rounded-2xl p-4 border border-navy-700/80 flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-xl bg-blue-500/20 text-blue-400 flex items-center justify-center shrink-0">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <span className="text-2xl font-black text-white font-mono">{totalCount}</span>
            <p className="text-[11px] text-slate-400 font-medium">Total Uploaded</p>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-4 border border-navy-700/80 flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <span className="text-2xl font-black text-emerald-300 font-mono">{validatedCount}</span>
            <p className="text-[11px] text-slate-400 font-medium">Govt Validated</p>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-4 border border-navy-700/80 flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center shrink-0">
            <Clock className="w-5 h-5" />
          </div>
          <div>
            <span className="text-2xl font-black text-amber-300 font-mono">{underReviewCount}</span>
            <p className="text-[11px] text-slate-400 font-medium">Under Evaluation</p>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-4 border border-navy-700/80 flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-xl bg-teal-500/20 text-teal-400 flex items-center justify-center shrink-0">
            <MapPin className="w-5 h-5" />
          </div>
          <div>
            <span className="text-2xl font-black text-teal-300 font-mono">{uniqueDistricts}</span>
            <p className="text-[11px] text-slate-400 font-medium">Districts Active</p>
          </div>
        </div>
      </div>

      {/* Interactive Filtering & Search Bar */}
      <div className="glass-card rounded-3xl p-5 sm:p-6 border border-navy-700/80 space-y-4">
        <div className="flex flex-col md:flex-row gap-3">
          
          {/* Live Search */}
          <div className="relative flex-grow">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by problem title, keyword, district, reference ID..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-navy-850 border border-navy-700 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 transition-colors"
            />
            {searchQuery && (
              <button 
                onClick={() => setSearchQuery("")}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* Quick Filters */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
            {/* Domain Filter */}
            <select
              value={selectedDomain}
              onChange={(e) => setSelectedDomain(e.target.value)}
              className="px-3 py-2.5 rounded-xl bg-navy-850 border border-navy-700 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
            >
              <option value="ALL">All Domains</option>
              {DOMAINS.map(d => (
                <option key={d.id} value={d.id}>{d.label}</option>
              ))}
            </select>

            {/* District Filter */}
            <select
              value={selectedDistrict}
              onChange={(e) => setSelectedDistrict(e.target.value)}
              className="px-3 py-2.5 rounded-xl bg-navy-850 border border-navy-700 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
            >
              <option value="ALL">All Districts</option>
              {JHARKHAND_DISTRICTS.map(dist => (
                <option key={dist} value={dist}>{dist}</option>
              ))}
            </select>

            {/* Status Filter */}
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-3 py-2.5 rounded-xl bg-navy-850 border border-navy-700 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
            >
              <option value="ALL">All Statuses</option>
              <option value="VALIDATED">Validated</option>
              <option value="UNDER_REVIEW">Under Review</option>
              <option value="SUBMITTED">Submitted</option>
              <option value="ASSIGNED">Assigned</option>
              <option value="REJECTED">Rejected</option>
            </select>

            {/* Sort Filter */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2.5 rounded-xl bg-navy-850 border border-navy-700 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
            >
              <option value="newest">Newest First</option>
              <option value="urgency">Highest Urgency</option>
              <option value="title">Alphabetical (A-Z)</option>
            </select>
          </div>

        </div>

        {/* Filter Badges Strip & Reset */}
        <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-navy-800 text-xs">
          <div className="text-slate-400 font-medium">
            Showing <strong className="text-white">{filteredProblems.length}</strong> of <span className="text-slate-400">{totalCount}</span> uploaded problems
          </div>

          {hasActiveFilters && (
            <button
              onClick={handleResetFilters}
              className="flex items-center space-x-1.5 text-blue-400 hover:text-blue-300 font-semibold transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset All Filters</span>
            </button>
          )}
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <SkeletonCard count={6} />
        </div>
      )}

      {/* Error State */}
      {!loading && error && (
        <ErrorState 
          title="Could Not Retrieve Problem Records"
          message={error}
          onRetry={refetch}
        />
      )}

      {/* Empty State */}
      {!loading && !error && filteredProblems.length === 0 && (
        <EmptyState
          icon={Layers}
          title={hasActiveFilters ? "No Problems Match Your Filter Criteria" : "No Community Problems Uploaded Yet"}
          description={
            hasActiveFilters 
              ? "Try adjusting your search terms, changing selected districts, or resetting filters to see more results."
              : "Be the first to submit an urgent community problem or infrastructure issue in your district."
          }
          actionLabel={hasActiveFilters ? "Clear All Filters" : "Report a Problem"}
          onAction={hasActiveFilters ? handleResetFilters : null}
          actionTo={!hasActiveFilters ? "/citizen-portal" : null}
        />
      )}

      {/* Cards Grid */}
      {!loading && !error && filteredProblems.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProblems.map((problem) => {
            const refCode = problem.reference_code || problem.referenceCode || problem.id?.slice(0, 8);
            const statusStr = problem.validation_status || problem.status || "SUBMITTED";
            const districtStr = problem.district || problem.location?.district || "Jharkhand";
            const blockStr = problem.block || problem.location?.block || problem.village_or_ward || "";
            const beneficiaries = problem.estimated_beneficiaries || problem.affected_population || problem.affectedPopulation;
            const submittedDate = problem.submitted_at || problem.submittedAt || problem.created_at;

            return (
              <div
                key={problem.id}
                className="glass-card rounded-3xl p-6 border border-navy-700/80 hover:border-blue-500/50 flex flex-col justify-between transition-all duration-300 hover:shadow-glow-sm hover:-translate-y-1 group"
              >
                {/* Card Header: Reference Code & Status */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-mono text-[11px] font-bold text-amber-400 bg-navy-850 px-2.5 py-1 rounded-lg border border-navy-700 tracking-wider">
                      {refCode}
                    </span>
                    <div className="flex items-center space-x-1.5">
                      {getUrgencyBadge(problem.urgency)}
                      <Badge variant={getStatusBadgeVariant(statusStr)}>
                        {statusStr}
                      </Badge>
                    </div>
                  </div>

                  {/* Title */}
                  <div>
                    <h3 className="text-base font-bold text-white group-hover:text-brand-primary transition-colors line-clamp-2 leading-snug">
                      {problem.title}
                    </h3>
                    {problem.title_hi && (
                      <p className="text-xs text-slate-400 font-medium mt-0.5 line-clamp-1">
                        {problem.title_hi}
                      </p>
                    )}
                  </div>

                  {/* Description Snippet */}
                  <p className="text-xs text-slate-300 line-clamp-3 leading-relaxed">
                    {problem.description}
                  </p>

                  {/* Metadata Chips */}
                  <div className="pt-2 border-t border-navy-800/80 space-y-2 text-xs">
                    {/* Domain & Location */}
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-navy-850 text-blue-300 text-[11px] border border-navy-700">
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

                    {/* Beneficiaries & Submission Date */}
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
                <div className="pt-5 mt-4 border-t border-navy-800 space-y-2">
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={() => handleAction(problem.id, '/ai-intelligence')}
                      className="w-full py-2 px-3 rounded-xl bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 hover:text-white border border-blue-500/30 text-xs font-semibold flex items-center justify-center space-x-1.5 transition-all"
                    >
                      <Sparkles className="w-3.5 h-3.5 text-blue-400" />
                      <span>AI Insights</span>
                    </button>

                    <button
                      onClick={() => handleAction(problem.id, '/university-matching')}
                      className="w-full py-2 px-3 rounded-xl bg-navy-800 hover:bg-navy-750 text-slate-200 border border-navy-600 text-xs font-semibold flex items-center justify-center space-x-1.5 transition-all"
                    >
                      <GraduationCap className="w-3.5 h-3.5 text-teal-400" />
                      <span>HEI Matches</span>
                    </button>
                  </div>

                  <button
                    onClick={() => setSelectedProblem(problem)}
                    className="w-full py-2 px-3 rounded-xl bg-navy-850 hover:bg-navy-800 text-slate-300 hover:text-white text-xs font-medium flex items-center justify-center space-x-1.5 border border-navy-700 transition-colors"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    <span>View Complete Dossier</span>
                  </button>
                </div>

              </div>
            );
          })}
        </div>
      )}

      {/* Detailed Problem Modal */}
      {selectedProblem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-950/80 backdrop-blur-md animate-in fade-in">
          <div className="glass-panel w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-3xl p-6 sm:p-8 border border-navy-700 space-y-6 shadow-2xl relative">
            
            {/* Close Button */}
            <button
              onClick={() => setSelectedProblem(null)}
              className="absolute top-6 right-6 p-2 rounded-xl bg-navy-850 hover:bg-navy-800 text-slate-400 hover:text-white border border-navy-700 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>

            {/* Modal Header */}
            <div className="space-y-2 pr-10">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-xs font-bold text-amber-400 bg-navy-850 px-2.5 py-1 rounded-lg border border-navy-700">
                  {selectedProblem.reference_code || selectedProblem.referenceCode || selectedProblem.id}
                </span>
                <Badge variant={getStatusBadgeVariant(selectedProblem.validation_status || selectedProblem.status)}>
                  {selectedProblem.validation_status || selectedProblem.status}
                </Badge>
                {getUrgencyBadge(selectedProblem.urgency)}
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

            {/* Metadata Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 p-4 rounded-2xl bg-navy-850 border border-navy-700 text-xs">
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
              <p className="text-xs sm:text-sm text-slate-300 leading-relaxed p-4 rounded-2xl bg-navy-900 border border-navy-800 whitespace-pre-line">
                {selectedProblem.description}
              </p>
            </div>

            {/* Existing Attempts or Constraints if available */}
            {selectedProblem.existing_attempts && (
              <div className="space-y-1.5 text-xs">
                <span className="font-semibold text-slate-300">Previous Interventions:</span>
                <p className="text-slate-400">{selectedProblem.existing_attempts}</p>
              </div>
            )}

            {/* Modal Quick Actions */}
            <div className="pt-4 border-t border-navy-700 flex flex-wrap items-center justify-end gap-3">
              <button
                onClick={() => {
                  setSelectedProblem(null);
                  handleAction(selectedProblem.id, '/ai-intelligence');
                }}
                className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-xs flex items-center space-x-2 shadow-glow-sm"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Analyze with AI</span>
              </button>

              <button
                onClick={() => {
                  setSelectedProblem(null);
                  handleAction(selectedProblem.id, '/university-matching');
                }}
                className="px-4 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-semibold text-xs flex items-center space-x-2 shadow-glow-sm"
              >
                <GraduationCap className="w-3.5 h-3.5" />
                <span>Match Universities</span>
              </button>

              <button
                onClick={() => {
                  setSelectedProblem(null);
                  handleAction(selectedProblem.id, '/government-dashboard');
                }}
                className="px-4 py-2.5 rounded-xl bg-navy-800 hover:bg-navy-750 text-slate-200 border border-navy-600 text-xs font-semibold flex items-center space-x-2"
              >
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Govt Desk</span>
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};
