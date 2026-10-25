import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useJanSetu } from '../../context/JanSetuContext';
import { useAuth } from '../../context/AuthContext';
import { challengeService } from '../../services/challengeService';
import { JHARKHAND_DISTRICTS, DOMAINS, URGENCY_LEVELS } from '../../config/constants';
import { Badge } from '../common/Badge';
import { 
  Send, 
  Mic, 
  MicOff, 
  Upload, 
  MapPin, 
  Sparkles, 
  CheckCircle2, 
  AlertCircle, 
  FileText, 
  Camera, 
  Layers, 
  Users, 
  Clock, 
  ArrowRight,
  Loader2,
  Lock,
  X,
  ChevronDown,
  Info,
  ShieldCheck,
  Paperclip,
  RotateCcw
} from 'lucide-react';

export const CitizenPortal = () => {
  const { language, setActiveChallengeId, showToast } = useJanSetu();
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    title: "",
    titleHi: "",
    description: "",
    domain: DOMAINS[0].id,
    district: JHARKHAND_DISTRICTS[0],
    block: "",
    panchayat: "",
    affectedPopulation: "",
    urgency: URGENCY_LEVELS[1].id,
  });

  const [attachments, setAttachments] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [submittedSuccess, setSubmittedSuccess] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [audioTranscript, setAudioTranscript] = useState("");

  const handleVoiceToggle = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      showToast("Speech recognition is not supported in this browser.", "error");
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = language === 'hi' ? 'hi-IN' : 'en-IN';
    recognition.continuous = false;
    recognition.interimResults = false;

    if (!isRecording) {
      setIsRecording(true);
      recognition.start();

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setAudioTranscript(transcript);
        setFormData(prev => ({
          ...prev,
          description: prev.description ? `${prev.description} ${transcript}` : transcript
        }));
        setIsRecording(false);
        showToast("Voice input transcribed successfully.", "success");
      };

      recognition.onerror = (event) => {
        console.warn("Speech recognition error:", event.error);
        setIsRecording(false);
      };

      recognition.onend = () => {
        setIsRecording(false);
      };
    } else {
      setIsRecording(false);
    }
  };

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      const fileNames = files.map(f => f.name);
      setAttachments(prev => [...prev, ...fileNames]);
      showToast(`Attached ${files.length} file(s)`, "info");
    }
  };

  const handleRemoveAttachment = (indexToRemove) => {
    setAttachments(prev => prev.filter((_, idx) => idx !== indexToRemove));
  };

  const handleReset = () => {
    setFormData({
      title: "",
      titleHi: "",
      description: "",
      domain: DOMAINS[0].id,
      district: JHARKHAND_DISTRICTS[0],
      block: "",
      panchayat: "",
      affectedPopulation: "",
      urgency: URGENCY_LEVELS[1].id,
    });
    setAttachments([]);
    setAudioTranscript("");
    setSubmitError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.title.trim() || !formData.description.trim()) {
      setSubmitError("Please fill out the required challenge title and description.");
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const payload = {
        title: formData.title,
        titleHi: formData.titleHi || undefined,
        description: formData.description,
        domain: formData.domain,
        location: {
          district: formData.district,
          block: formData.block || undefined,
          panchayat: formData.panchayat || undefined,
        },
        affectedPopulation: formData.affectedPopulation || undefined,
        urgency: formData.urgency,
        attachments: attachments,
        submittedAt: new Date().toISOString(),
        submitted_by_user_id: user?.id || "usr_citizen",
        submitter_email: user?.email || "citizen@jansetu.gov.in",
        submitter_name: user?.full_name || "Community Citizen",
      };

      const result = await challengeService.createChallenge(payload);
      const newId = result?.id || result?.challengeId || `JS-${Date.now().toString().slice(-4)}`;
      const refCode = result?.reference_code || result?.referenceCode || `JS-2026-${Math.floor(1000 + Math.random() * 9000)}`;

      setActiveChallengeId(newId);
      setSubmittedSuccess({
        id: newId,
        referenceCode: refCode,
        title: formData.title,
        district: formData.district,
        block: formData.block,
        domain: formData.domain,
        beneficiaries: formData.affectedPopulation,
      });
      showToast("Challenge recorded in State Community Registry.", "success");
    } catch (err) {
      setSubmitError(err.message || "Failed to submit challenge. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      
      {/* Top SaaS Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/[0.07]">
        <div className="space-y-1.5">
          <div className="flex items-center space-x-2">
            <Badge variant="blue" dot={true}>
              MODULE 02 • INTAKE GATEWAY
            </Badge>
            <span className="text-[11px] text-slate-500 font-mono">SIH26043-CIVIC-v2</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white font-display tracking-tight">
            {language === 'hi' ? "जनसमस्या रिपोर्ट पोर्टल" : "Report a Community Challenge"}
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 max-w-2xl">
            {language === 'hi' 
              ? "झारखंड के ग्रामीण व शहरी क्षेत्रों की समस्याएं दर्ज करें। प्लेटफॉर्म एआई सीधे नोडल विश्वविद्यालय व विभाग से जोड़ेगा।" 
              : "Crowdsource real grassroots challenges. Platform AI structures, clusters, and routes verified reports to accredited university solver labs."}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="px-3.5 py-2 rounded-xl bg-saas-elevated/70 border border-white/[0.08] text-right shadow-saas-card backdrop-blur-md">
            <p className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">Territory Anchor</p>
            <p className="text-xs font-semibold text-slate-200">Jharkhand • 24 Districts</p>
          </div>
        </div>
      </div>

      {submitError && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-start space-x-3 text-xs text-rose-300 shadow-saas-card animate-in fade-in">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-semibold text-rose-200">Submission Blocked</p>
            <p>{submitError}</p>
          </div>
        </div>
      )}

      {/* Submission Success Confirmation Dossier */}
      {submittedSuccess && (
        <div className="saas-panel border-emerald-500/40 p-6 sm:p-8 space-y-6 shadow-2xl animate-in zoom-in-95 relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-500 via-teal-400 to-cyan-500" />
          
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/[0.07] pb-5">
            <div className="flex items-center space-x-3.5">
              <div className="w-12 h-12 rounded-2xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shadow-glow-sm">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div>
                <span className="text-[10px] uppercase font-mono font-bold tracking-wider text-emerald-400 flex items-center space-x-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span>OFFICIAL CIVIC INTAKE RECEIPT</span>
                </span>
                <h2 className="text-xl font-bold text-white font-display">
                  Problem Statement Successfully Logged
                </h2>
              </div>
            </div>

            <div className="px-4 py-2 rounded-xl bg-saas-dark border border-white/[0.08] text-right shadow-inner">
              <p className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">State Reference Code</p>
              <p className="font-mono text-base font-extrabold text-amber-400 tracking-wider">
                {submittedSuccess.referenceCode}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-4 rounded-xl bg-saas-dark/70 border border-white/[0.06] text-xs">
            <div>
              <span className="text-slate-500 block text-[10px] uppercase font-mono font-semibold">Title</span>
              <span className="font-semibold text-white line-clamp-1">{submittedSuccess.title}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px] uppercase font-mono font-semibold">District & Block</span>
              <span className="font-semibold text-emerald-400">{submittedSuccess.district}{submittedSuccess.block ? `, ${submittedSuccess.block}` : ''}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px] uppercase font-mono font-semibold">Validation Queue</span>
              <span className="inline-flex items-center space-x-1.5 font-semibold text-amber-400">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse"></span>
                <span>Queued for Official Review</span>
              </span>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-saas-card/60 border border-white/[0.06] space-y-2 text-xs">
            <div className="flex items-center space-x-2 text-indigo-300 font-semibold">
              <ShieldCheck className="w-4 h-4 text-indigo-400" />
              <span>Next Steps in the Closed-Loop Pipeline:</span>
            </div>
            <p className="text-slate-400 leading-relaxed text-[11px]">
              1. District Nodal Officers verify ground truth and assign solver mandates.<br />
              2. Accredited Higher Education Institutions (HEIs) receive technical matching.<br />
              3. You and your community can track the live resolution progress of this challenge.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
            <button
              type="button"
              onClick={() => {
                handleReset();
                setSubmittedSuccess(null);
              }}
              className="btn-saas-secondary w-full sm:w-auto px-4 py-2.5 rounded-xl font-semibold text-xs flex items-center justify-center space-x-2"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Submit Another Challenge</span>
            </button>

            <button
              type="button"
              onClick={() => navigate('/problems?tab=my_problems')}
              className="btn-saas-teal w-full sm:w-auto px-5 py-2.5 rounded-xl font-bold text-xs flex items-center justify-center space-x-2"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Track in My Problems</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* Authentication Gate for Unauthenticated Public Guests */}
      {!isAuthenticated && (
        <div className="saas-panel p-8 sm:p-12 space-y-6 text-center relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500" />
          
          <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center mx-auto text-indigo-400 shadow-glow-sm">
            <Lock className="w-8 h-8" />
          </div>

          <div className="space-y-2 max-w-lg mx-auto">
            <h2 className="text-xl sm:text-2xl font-bold text-white font-display">
              Sign In Required to Report a Challenge
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
              To prevent fraudulent submissions, maintain civic accountability, and enable you to <span className="text-white font-semibold">track, edit, or remove your problem statement</span> once resolved by the authorities, please sign in with your account.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
            <button
              onClick={() => navigate('/login?redirect=/citizen-portal')}
              className="btn-saas-primary w-full sm:w-auto px-6 py-3 rounded-xl font-bold text-sm flex items-center justify-center space-x-2 shadow-glow-sm"
            >
              <span>Sign In with Your Account</span>
              <ArrowRight className="w-4 h-4 shrink-0" />
            </button>

            <button
              onClick={() => navigate('/problems')}
              className="btn-saas-secondary w-full sm:w-auto px-6 py-3 rounded-xl font-semibold text-sm flex items-center justify-center space-x-2"
            >
              <Layers className="w-4 h-4 text-indigo-400 shrink-0" />
              <span>Browse Uploaded Problems</span>
            </button>
          </div>
        </div>
      )}

      {/* Upgraded Professional Problem Entry Card (Only shown if Authenticated) */}
      {isAuthenticated && (
      <form 
        onSubmit={handleSubmit} 
        className="saas-panel overflow-hidden divide-y divide-white/[0.07]"
      >
        
        {/* Card Official Top Bar */}
        <div className="px-6 py-4 bg-saas-card/50 flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/[0.07]">
          <div className="flex items-center space-x-2.5">
            <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse"></span>
            <span className="text-[11px] font-mono uppercase tracking-wider text-slate-300 font-semibold">
              INTAKE PROTOCOL: SIH26043-STD
            </span>
            <span className="text-slate-600">•</span>
            <span className="text-[11px] text-slate-400">Authenticated Civic Entry</span>
          </div>

          <div className="flex items-center space-x-2 text-[11px]">
            <span className="px-2.5 py-0.5 rounded-full bg-white/[0.04] border border-white/[0.08] text-slate-400 font-mono text-[10px]">
              Active Author: {user?.full_name || "Citizen"}
            </span>
            <Badge variant="emerald" dot={true}>
              AI Triaging Live
            </Badge>
          </div>
        </div>

        {/* Section 01: Core Problem Identification */}
        <div className="p-6 sm:p-7 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <span className="flex items-center justify-center w-6 h-6 rounded-lg bg-indigo-500/15 text-indigo-400 text-[10px] font-mono font-bold border border-indigo-500/30">
                01
              </span>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">
                {language === 'hi' ? "मुख्य समस्या पहचान" : "Core Challenge Identity"}
              </h3>
            </div>
            <span className="text-[11px] text-slate-500 font-mono">* Required fields</span>
          </div>

          {/* Problem Title */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-medium text-slate-300">
                {language === 'hi' ? "समस्या का आधिकारिक शीर्षक *" : "Challenge Title *"}
              </label>
              <span className="text-[10px] font-mono text-slate-500">
                {formData.title.length}/120
              </span>
            </div>
            <input
              type="text"
              required
              maxLength={120}
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder={language === 'hi' ? "उदा. प्रखंड में धान के पत्तों में पीलापन और सड़न" : "e.g., Solar-Powered Water Purification System for Tribal School"}
              className="saas-input text-sm"
            />
          </div>

          {/* Domain & Urgency Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
            {/* Domain */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300 flex items-center space-x-1.5">
                <Layers className="w-3.5 h-3.5 text-indigo-400" />
                <span>{language === 'hi' ? "कार्यक्षेत्र / श्रेणी *" : "Domain & Sector *"}</span>
              </label>
              <div className="relative">
                <select
                  value={formData.domain}
                  onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
                  className="saas-input appearance-none pr-8 cursor-pointer"
                >
                  {DOMAINS.map(dm => (
                    <option key={dm.id} value={dm.id} className="bg-saas-dark text-white">
                      {language === 'hi' ? dm.labelHi : dm.label}
                    </option>
                  ))}
                </select>
                <ChevronDown className="w-3.5 h-3.5 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              </div>
            </div>

            {/* Urgency Window */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300 flex items-center space-x-1.5">
                <Clock className="w-3.5 h-3.5 text-amber-400" />
                <span>{language === 'hi' ? "प्राथमिकता विंडो *" : "Urgency & Operational Window *"}</span>
              </label>
              <div className="relative">
                <select
                  value={formData.urgency}
                  onChange={(e) => setFormData({ ...formData, urgency: e.target.value })}
                  className="saas-input appearance-none pr-8 cursor-pointer"
                >
                  {URGENCY_LEVELS.map(u => (
                    <option key={u.id} value={u.id} className="bg-saas-dark text-white">
                      {u.label}
                    </option>
                  ))}
                </select>
                <ChevronDown className="w-3.5 h-3.5 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              </div>
            </div>
          </div>
        </div>

        {/* Section 02: Geographic & Demographic Anchor */}
        <div className="p-6 sm:p-7 space-y-4">
          <div className="flex items-center space-x-2.5">
            <span className="flex items-center justify-center w-6 h-6 rounded-lg bg-indigo-500/15 text-indigo-400 text-[10px] font-mono font-bold border border-indigo-500/30">
              02
            </span>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">
              {language === 'hi' ? "क्षेत्रीय अधिकार क्षेत्र एवं आबादी" : "Jurisdiction & Field Demographics"}
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* District */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300 flex items-center space-x-1">
                <MapPin className="w-3.5 h-3.5 text-rose-400" />
                <span>{language === 'hi' ? "जिला *" : "District *"}</span>
              </label>
              <div className="relative">
                <select
                  value={formData.district}
                  onChange={(e) => setFormData({ ...formData, district: e.target.value })}
                  className="saas-input appearance-none pr-7 cursor-pointer"
                >
                  {JHARKHAND_DISTRICTS.map(d => (
                    <option key={d} value={d} className="bg-saas-dark text-white">{d}</option>
                  ))}
                </select>
                <ChevronDown className="w-3.5 h-3.5 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              </div>
            </div>

            {/* Block / Tehsil */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300">
                {language === 'hi' ? "प्रखंड / ब्लॉक" : "Block / Tehsil"}
              </label>
              <input
                type="text"
                value={formData.block}
                onChange={(e) => setFormData({ ...formData, block: e.target.value })}
                placeholder="e.g. Ghaghra"
                className="saas-input"
              />
            </div>

            {/* Gram Panchayat / Village */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300">
                {language === 'hi' ? "ग्राम पंचायत / गाँव" : "Gram Panchayat / Village"}
              </label>
              <input
                type="text"
                value={formData.panchayat}
                onChange={(e) => setFormData({ ...formData, panchayat: e.target.value })}
                placeholder="e.g. Belagarha"
                className="saas-input"
              />
            </div>

            {/* Affected Population */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300 flex items-center space-x-1">
                <Users className="w-3.5 h-3.5 text-indigo-400" />
                <span>{language === 'hi' ? "प्रभावित जनसंख्या" : "Beneficiaries"}</span>
              </label>
              <input
                type="text"
                value={formData.affectedPopulation}
                onChange={(e) => setFormData({ ...formData, affectedPopulation: e.target.value })}
                placeholder="e.g. ~450 residents"
                className="saas-input"
              />
            </div>
          </div>
        </div>

        {/* Section 03: Narrative Context & Voice Dictation */}
        <div className="p-6 sm:p-7 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <span className="flex items-center justify-center w-6 h-6 rounded-lg bg-indigo-500/15 text-indigo-400 text-[10px] font-mono font-bold border border-indigo-500/30">
                03
              </span>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">
                {language === 'hi' ? "समस्या का विस्तृत विवरण व साक्ष्य" : "Problem Narrative & Impact Detail"}
              </h3>
            </div>

            {/* Voice Dictation Button */}
            <button
              type="button"
              onClick={handleVoiceToggle}
              className={`inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                isRecording 
                  ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40 animate-pulse' 
                  : 'btn-saas-secondary text-[11px]'
              }`}
            >
              {isRecording ? (
                <>
                  <MicOff className="w-3.5 h-3.5 text-rose-400 animate-spin" />
                  <span>Listening (Speak Now)...</span>
                </>
              ) : (
                <>
                  <Mic className="w-3.5 h-3.5 text-indigo-400" />
                  <span>{language === 'hi' ? "ध्वनि इनपुट (Voice Dictation)" : "Voice Dictation"}</span>
                  <span className="text-[10px] px-1 py-0.2 rounded bg-saas-dark text-slate-400 border border-white/[0.08] font-mono">
                    {language === 'hi' ? 'HI' : 'EN'}
                  </span>
                </>
              )}
            </button>
          </div>

          <div className="space-y-2">
            <div className="relative">
              <textarea
                rows={5}
                required
                maxLength={2000}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder={language === 'hi' ? "यहाँ अपनी समस्या का विस्तृत विवरण लिखें..." : "Provide exact field observations, historical timeline, current consequences, and specific barriers encountered by the community..."}
                className="saas-input leading-relaxed resize-y min-h-[120px]"
              />
              <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 px-1 pt-1">
                <span>Markdown & plain text supported</span>
                <span>{formData.description.length}/2000 characters</span>
              </div>
            </div>

            {audioTranscript && (
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-start space-x-2.5 text-xs text-emerald-300">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <div className="space-y-0.5">
                  <p className="font-semibold text-[11px]">Speech Transcribed</p>
                  <p className="text-[11px] text-emerald-200/90 font-mono leading-tight">"{audioTranscript}"</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Section 04: Supporting Evidence Vault */}
        <div className="p-6 sm:p-7 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <span className="flex items-center justify-center w-6 h-6 rounded-lg bg-indigo-500/15 text-indigo-400 text-[10px] font-mono font-bold border border-indigo-500/30">
                04
              </span>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">
                {language === 'hi' ? "प्रमाण फोटो व दस्तावेज (वैकल्पिक)" : "Field Evidence & Verification Files"}
              </h3>
            </div>
            <span className="text-[11px] text-slate-500 font-mono">Optional</span>
          </div>

          <div className="rounded-xl border border-dashed border-white/[0.12] bg-saas-dark/40 hover:bg-saas-dark/70 hover:border-indigo-500/40 transition-all p-6 text-center">
            <input
              type="file"
              multiple
              onChange={handleFileUpload}
              className="hidden"
              id="evidence-file-input"
            />
            <label htmlFor="evidence-file-input" className="cursor-pointer block space-y-2">
              <div className="w-11 h-11 rounded-2xl bg-saas-elevated border border-white/[0.08] flex items-center justify-center mx-auto text-indigo-400 shadow-saas-card">
                <Upload className="w-5 h-5" />
              </div>
              <div className="space-y-0.5">
                <p className="text-xs font-semibold text-slate-200">
                  {language === 'hi' ? "फाइल अपलोड करने के लिए क्लिक करें" : "Click to select or drag supporting field evidence"}
                </p>
                <p className="text-[11px] text-slate-400">
                  Photographs of field conditions, laboratory reports, or community petition scans
                </p>
              </div>
              <div className="flex items-center justify-center gap-1.5 pt-1 text-[10px] font-mono text-slate-500">
                <span className="px-1.5 py-0.5 rounded bg-saas-elevated border border-white/[0.06]">PNG</span>
                <span className="px-1.5 py-0.5 rounded bg-saas-elevated border border-white/[0.06]">JPG</span>
                <span className="px-1.5 py-0.5 rounded bg-saas-elevated border border-white/[0.06]">PDF</span>
                <span>• Max 10MB per file</span>
              </div>
            </label>

            {attachments.length > 0 && (
              <div className="mt-4 pt-3 border-t border-white/[0.07] flex flex-wrap gap-2 justify-center">
                {attachments.map((file, idx) => (
                  <span 
                    key={idx} 
                    className="inline-flex items-center space-x-1.5 text-[11px] pl-2.5 pr-1.5 py-1 rounded-lg bg-saas-elevated border border-white/[0.08] text-slate-200 shadow-sm"
                  >
                    <Paperclip className="w-3 h-3 text-indigo-400" />
                    <span className="max-w-[180px] truncate">{file}</span>
                    <button 
                      type="button" 
                      onClick={() => handleRemoveAttachment(idx)}
                      className="w-4 h-4 rounded hover:bg-white/[0.08] flex items-center justify-center text-slate-400 hover:text-rose-400 transition-colors"
                      title="Remove file"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Section 05: Official Audit Bar & Actions */}
        <div className="px-6 py-4 bg-saas-card/50 flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-white/[0.07]">
          <div className="flex items-center space-x-2.5 text-xs text-slate-400">
            <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
            <span className="text-[11px] leading-tight">
              Cryptographically timestamped record. Routed through JanSetu AI Triaging Pipeline.
            </span>
          </div>

          <div className="flex items-center space-x-3 w-full sm:w-auto">
            <button
              type="button"
              onClick={handleReset}
              disabled={isSubmitting}
              className="btn-saas-secondary px-4 py-2.5 rounded-xl text-xs font-semibold flex items-center space-x-1.5 disabled:opacity-50"
            >
              <RotateCcw className="w-3.5 h-3.5 text-slate-400" />
              <span>Reset</span>
            </button>

            <button
              type="submit"
              disabled={isSubmitting}
              className="btn-saas-primary px-6 py-2.5 rounded-xl flex-1 sm:flex-initial text-xs font-bold flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Submitting to State Registry...</span>
                </>
              ) : (
                <>
                  <span>{language === 'hi' ? "समस्या दर्ज करें" : "Submit Challenge to Platform"}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </div>
        </div>

      </form>
      )}

    </div>
  );
};
