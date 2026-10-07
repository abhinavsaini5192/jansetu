import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useJanSetu } from '../../context/JanSetuContext';
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
      };

      const result = await challengeService.createChallenge(payload);
      const newId = result?.id || result?.challengeId;

      if (newId) {
        setActiveChallengeId(newId);
        showToast("Challenge submitted successfully to platform.", "success");
        navigate(`/ai-intelligence`);
      } else {
        showToast("Challenge recorded.", "success");
        navigate(`/`);
      }
    } catch (err) {
      setSubmitError(err.message || "Failed to submit challenge. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      
      {/* Top Protocol Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-navy-800/80">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
              MODULE 02
            </span>
            <span className="text-xs text-slate-400">Citizen Crowdsourcing Gateway</span>
          </div>
          <h1 className="text-2xl font-bold text-white font-display tracking-tight">
            {language === 'hi' ? "जनसमस्या रिपोर्ट पोर्टल" : "Report a Community Challenge"}
          </h1>
          <p className="text-xs text-slate-400">
            {language === 'hi' 
              ? "झारखंड के ग्रामीण व शहरी क्षेत्रों की समस्याएं दर्ज करें। प्लेटफॉर्म एआई सीधे नोडल विश्वविद्यालय व विभाग से जोड़ेगा।" 
              : "Crowdsource real grassroots challenges. Platform AI structures, clusters, and routes reports to accredited institutions."}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="px-3 py-1.5 rounded-lg bg-navy-900 border border-navy-800 text-right">
            <p className="text-[10px] font-mono text-slate-500 uppercase">State Jurisdiction</p>
            <p className="text-xs font-semibold text-slate-300">Jharkhand • 24 Districts</p>
          </div>
        </div>
      </div>

      {submitError && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-start space-x-3 text-xs text-rose-300">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-semibold text-rose-200">Submission Blocked</p>
            <p>{submitError}</p>
          </div>
        </div>
      )}

      {/* Upgraded Professional Problem Entry Card */}
      <form 
        onSubmit={handleSubmit} 
        className="rounded-2xl bg-navy-900/95 backdrop-blur-xl border border-navy-750 shadow-2xl overflow-hidden divide-y divide-navy-800/70"
      >
        
        {/* Card Official Top Bar */}
        <div className="px-6 py-4 bg-navy-850/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center space-x-2.5">
            <div className="w-2 h-2 rounded-full bg-blue-500"></div>
            <span className="text-[11px] font-mono uppercase tracking-wider text-slate-300 font-semibold">
              INTAKE PROTOCOL: SIH26043-STD
            </span>
            <span className="text-slate-600">•</span>
            <span className="text-[11px] text-slate-400">Official Community Submission</span>
          </div>

          <div className="flex items-center space-x-2 text-[11px]">
            <span className="px-2 py-0.5 rounded bg-navy-800 border border-navy-700 text-slate-400 font-mono">
              Status: Draft
            </span>
            <span className="px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-medium flex items-center space-x-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>AI Validation Pipeline Active</span>
            </span>
          </div>
        </div>

        {/* Section 01: Core Problem Identification */}
        <div className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="flex items-center justify-center w-5 h-5 rounded-full bg-blue-500/10 text-blue-400 text-[10px] font-mono font-bold border border-blue-500/20">
                01
              </span>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                {language === 'hi' ? "मुख्य समस्या पहचान" : "Core Challenge Identity"}
              </h3>
            </div>
            <span className="text-[11px] text-slate-500">* Indicates required fields</span>
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
              className="w-full px-3.5 py-2.5 rounded-lg bg-navy-950/80 border border-navy-700 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/30 transition-all font-sans"
            />
          </div>

          {/* Domain & Urgency Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
            {/* Domain */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300 flex items-center space-x-1.5">
                <Layers className="w-3.5 h-3.5 text-blue-400" />
                <span>{language === 'hi' ? "कार्यक्षेत्र / श्रेणी *" : "Domain & Sector *"}</span>
              </label>
              <div className="relative">
                <select
                  value={formData.domain}
                  onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
                  className="w-full appearance-none px-3.5 py-2.5 pr-8 rounded-lg bg-navy-950/80 border border-navy-700 text-white text-xs focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/30 transition-all cursor-pointer font-sans"
                >
                  {DOMAINS.map(dm => (
                    <option key={dm.id} value={dm.id}>
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
                  className="w-full appearance-none px-3.5 py-2.5 pr-8 rounded-lg bg-navy-950/80 border border-navy-700 text-white text-xs focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/30 transition-all cursor-pointer font-sans"
                >
                  {URGENCY_LEVELS.map(u => (
                    <option key={u.id} value={u.id}>
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
        <div className="p-6 space-y-4">
          <div className="flex items-center space-x-2">
            <span className="flex items-center justify-center w-5 h-5 rounded-full bg-blue-500/10 text-blue-400 text-[10px] font-mono font-bold border border-blue-500/20">
              02
            </span>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
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
                  className="w-full appearance-none px-3 py-2.5 pr-7 rounded-lg bg-navy-950/80 border border-navy-700 text-white text-xs focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/30 transition-all cursor-pointer font-sans"
                >
                  {JHARKHAND_DISTRICTS.map(d => (
                    <option key={d} value={d}>{d}</option>
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
                className="w-full px-3 py-2.5 rounded-lg bg-navy-950/80 border border-navy-700 text-white placeholder-slate-500 text-xs focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/30 transition-all font-sans"
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
                className="w-full px-3 py-2.5 rounded-lg bg-navy-950/80 border border-navy-700 text-white placeholder-slate-500 text-xs focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/30 transition-all font-sans"
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
                className="w-full px-3 py-2.5 rounded-lg bg-navy-950/80 border border-navy-700 text-white placeholder-slate-500 text-xs focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/30 transition-all font-sans"
              />
            </div>
          </div>
        </div>

        {/* Section 03: Narrative Context & Voice Dictation */}
        <div className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="flex items-center justify-center w-5 h-5 rounded-full bg-blue-500/10 text-blue-400 text-[10px] font-mono font-bold border border-blue-500/20">
                03
              </span>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
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
                  : 'bg-navy-800 hover:bg-navy-750 text-slate-300 border border-navy-700 hover:border-navy-600'
              }`}
            >
              {isRecording ? (
                <>
                  <MicOff className="w-3.5 h-3.5 text-rose-400 animate-spin" />
                  <span>Listening (Speak Now)...</span>
                </>
              ) : (
                <>
                  <Mic className="w-3.5 h-3.5 text-blue-400" />
                  <span>{language === 'hi' ? "ध्वनि इनपुट (Voice Dictation)" : "Voice Dictation"}</span>
                  <span className="text-[10px] px-1 py-0.2 rounded bg-navy-900 text-slate-400 border border-navy-700 font-mono">
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
                className="w-full px-3.5 py-3 rounded-lg bg-navy-950/80 border border-navy-700 text-white placeholder-slate-500 text-xs leading-relaxed focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/30 transition-all font-sans resize-y"
              />
              <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 px-1 pt-1">
                <span>Markdown & plain text supported</span>
                <span>{formData.description.length}/2000 characters</span>
              </div>
            </div>

            {audioTranscript && (
              <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-start space-x-2 text-xs text-emerald-300">
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
        <div className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="flex items-center justify-center w-5 h-5 rounded-full bg-blue-500/10 text-blue-400 text-[10px] font-mono font-bold border border-blue-500/20">
                04
              </span>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                {language === 'hi' ? "प्रमाण फोटो व दस्तावेज (वैकल्पिक)" : "Field Evidence & Verification Files"}
              </h3>
            </div>
            <span className="text-[11px] text-slate-500">Optional</span>
          </div>

          <div className="rounded-xl border border-dashed border-navy-700 bg-navy-950/50 hover:bg-navy-950/70 transition-colors p-5 text-center">
            <input
              type="file"
              multiple
              onChange={handleFileUpload}
              className="hidden"
              id="evidence-file-input"
            />
            <label htmlFor="evidence-file-input" className="cursor-pointer block space-y-2">
              <div className="w-10 h-10 rounded-full bg-navy-850 border border-navy-700 flex items-center justify-center mx-auto text-blue-400">
                <Upload className="w-4 h-4" />
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
                <span className="px-1.5 py-0.5 rounded bg-navy-900 border border-navy-800">PNG</span>
                <span className="px-1.5 py-0.5 rounded bg-navy-900 border border-navy-800">JPG</span>
                <span className="px-1.5 py-0.5 rounded bg-navy-900 border border-navy-800">PDF</span>
                <span>• Max 10MB per file</span>
              </div>
            </label>

            {attachments.length > 0 && (
              <div className="mt-4 pt-3 border-t border-navy-800/80 flex flex-wrap gap-2 justify-center">
                {attachments.map((file, idx) => (
                  <span 
                    key={idx} 
                    className="inline-flex items-center space-x-1.5 text-[11px] pl-2.5 pr-1.5 py-1 rounded-md bg-navy-850 border border-navy-700 text-slate-200"
                  >
                    <Paperclip className="w-3 h-3 text-blue-400" />
                    <span className="max-w-[180px] truncate">{file}</span>
                    <button 
                      type="button" 
                      onClick={() => handleRemoveAttachment(idx)}
                      className="w-4 h-4 rounded hover:bg-navy-700 flex items-center justify-center text-slate-400 hover:text-rose-400 transition-colors"
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
        <div className="px-6 py-4 bg-navy-850/50 flex flex-col sm:flex-row items-center justify-between gap-4">
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
              className="px-4 py-2.5 rounded-lg bg-navy-800 hover:bg-navy-750 border border-navy-700 text-xs font-medium text-slate-300 transition-colors disabled:opacity-50 flex items-center space-x-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5 text-slate-400" />
              <span>Reset</span>
            </button>

            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 sm:flex-initial px-6 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs shadow-md shadow-blue-600/20 flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
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

    </div>
  );
};
