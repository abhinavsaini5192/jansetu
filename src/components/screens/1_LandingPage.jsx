import React from 'react';
import { Link } from 'react-router-dom';
import { useJanSetu } from '../../context/JanSetuContext';
import { Badge } from '../common/Badge';
import { 
  ArrowRight, 
  Sparkles, 
  Check, 
  TrendingUp, 
  Cpu, 
  Users, 
  Building2, 
  GraduationCap, 
  CheckCircle2,
  Layers
} from 'lucide-react';
import Ferrofluid from '../effects/Ferrofluid';

export const LandingPage = () => {
  const { language } = useJanSetu();

  return (
    <div className="relative isolate min-h-screen space-y-16 pb-16">
      
      {/* Full Page Interactive Ferrofluid Background */}
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
        <Ferrofluid
          colors={["#094ae2", "#2253e1", "#021257"]}
          speed={0.5}
          scale={1}
          turbulence={1}
          fluidity={0.07}
          rimWidth={0.2}
          sharpness={3}
          shimmer={1}
          glow={2}
          flowDirection="down"
          opacity={1}
          mouseInteraction={true}
          mouseStrength={1}
          mouseRadius={0.3}
        />
        {/* Subtle ambient overlay to maintain optimal legibility across all sections */}
        <div className="absolute inset-0 bg-navy-950/25 pointer-events-none" />
      </div>

      <div className="relative z-10 space-y-16">
        {/* Hero Section */}
        <section className="pt-16 pb-20 px-4 sm:px-6 lg:px-8 text-center min-h-[580px] flex items-center justify-center">
          <div className="max-w-4xl mx-auto space-y-6 pointer-events-auto">
            
            {/* Official Badge */}
            <div className="saas-badge bg-white/[0.04] border-white/[0.12] text-xs font-semibold text-slate-300 shadow-saas-card">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="font-mono text-blue-300">SIH 2026 Problem ID: SIH26043</span>
              <span className="text-slate-600">•</span>
              <span className="text-amber-300 font-medium">Govt. of Jharkhand</span>
            </div>

          {/* Main Headline */}
          <h1 className="text-4xl sm:text-6xl font-black font-display tracking-tight text-white leading-tight">
            From Community Problems to{" "}
            <span className="text-gradient-blue">Deployable Solutions.</span>
          </h1>

          <p className="text-base sm:text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed font-normal">
            JanSetu is a centralized societal innovation operating system. We bridge citizens, government departments, premier universities, and industry partners to transform real-world grassroots challenges into verified, deployable technology solutions.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <Link
              to="/citizen-portal"
              className="btn-saas-primary px-6 py-3.5 rounded-2xl font-bold text-sm flex items-center space-x-2"
            >
              <span>{language === 'hi' ? "समस्या दर्ज करें" : "Report a Community Challenge"}</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              to="/problems"
              className="btn-saas-secondary px-6 py-3.5 rounded-2xl font-bold text-sm flex items-center space-x-2"
            >
              <Layers className="w-4 h-4 text-blue-400" />
              <span>Browse Uploaded Problems</span>
            </Link>
          </div>

          <div className="pt-2 text-xs text-slate-400 flex items-center justify-center space-x-4">
            <span className="flex items-center space-x-1.5">
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span>Closed-Loop Innovation</span>
            </span>
            <span className="flex items-center space-x-1.5">
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span>Explainable AI Matching</span>
            </span>
            <span className="flex items-center space-x-1.5">
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span>Evidence-Based Impact</span>
            </span>
          </div>

        </div>
      </section>

      {/* How JanSetu Works: The Closed Loop Innovation Pipeline */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        <div className="text-center max-w-3xl mx-auto mb-12 space-y-3">
          <Badge variant="teal" dot={true}>The Closed-Loop Ecosystem</Badge>
          <h2 className="text-3xl sm:text-4xl font-black text-white font-display tracking-tight">
            How Community Problems Become Deployable Solutions
          </h2>
          <p className="text-sm text-slate-400 leading-relaxed font-normal">
            Traditional portals stop at grievance logging. JanSetu operates a full 6-phase innovation lifecycle powered by explainable AI and institutional accountability.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          
          <div className="saas-card rounded-2xl p-5 border border-white/[0.08] space-y-3 relative group">
            <div className="w-10 h-10 rounded-xl bg-blue-500/15 border border-blue-500/25 flex items-center justify-center text-blue-400 font-bold text-xs font-mono">
              01
            </div>
            <h4 className="text-sm font-bold text-white group-hover:text-blue-300 transition-colors">Citizen Report</h4>
            <p className="text-xs text-slate-400 leading-relaxed font-normal">
              Bilingual crowdsourcing with voice input, geo-tagging, and photo evidence.
            </p>
          </div>

          <div className="saas-card rounded-2xl p-5 border border-white/[0.08] space-y-3 relative group">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/15 border border-indigo-500/25 flex items-center justify-center text-indigo-400 font-bold text-xs font-mono">
              02
            </div>
            <h4 className="text-sm font-bold text-white group-hover:text-indigo-300 transition-colors">AI Intelligence</h4>
            <p className="text-xs text-slate-400 leading-relaxed font-normal">
              Domain scoring, entity extraction, and semantic duplicate clustering.
            </p>
          </div>

          <div className="saas-card rounded-2xl p-5 border border-white/[0.08] space-y-3 relative group">
            <div className="w-10 h-10 rounded-xl bg-amber-500/15 border border-amber-500/25 flex items-center justify-center text-amber-400 font-bold text-xs font-mono">
              03
            </div>
            <h4 className="text-sm font-bold text-white group-hover:text-amber-300 transition-colors">Govt Validation</h4>
            <p className="text-xs text-slate-400 leading-relaxed font-normal">
              Official verification by District/State authorities and nodal department assignment.
            </p>
          </div>

          <div className="saas-card rounded-2xl p-5 border border-white/[0.08] space-y-3 relative group">
            <div className="w-10 h-10 rounded-xl bg-teal-500/15 border border-teal-500/25 flex items-center justify-center text-teal-400 font-bold text-xs font-mono">
              04
            </div>
            <h4 className="text-sm font-bold text-white group-hover:text-teal-300 transition-colors">HEI Recommendation & Adoption</h4>
            <p className="text-xs text-slate-400 leading-relaxed font-normal">
              Autonomous universities review AI-recommended challenges matching their labs and voluntarily adopt research projects.
            </p>
          </div>

          <div className="saas-card rounded-2xl p-5 border border-white/[0.08] space-y-3 relative group">
            <div className="w-10 h-10 rounded-xl bg-purple-500/15 border border-purple-500/25 flex items-center justify-center text-purple-400 font-bold text-xs font-mono">
              05
            </div>
            <h4 className="text-sm font-bold text-white group-hover:text-purple-300 transition-colors">Industry / CSR</h4>
            <p className="text-xs text-slate-400 leading-relaxed font-normal">
              Enterprises provide milestone seed funding, hardware, and field trial logistics.
            </p>
          </div>

          <div className="saas-card rounded-2xl p-5 border border-white/[0.08] space-y-3 relative group">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/15 border border-emerald-500/25 flex items-center justify-center text-emerald-400 font-bold text-xs font-mono">
              06
            </div>
            <h4 className="text-sm font-bold text-white group-hover:text-emerald-300 transition-colors">Verified Impact</h4>
            <p className="text-xs text-slate-400 leading-relaxed font-normal">
              Before/after metrics, farmer satisfaction, and digital signature by state authority.
            </p>
          </div>

        </div>
      </section>

      {/* Key Differentiators Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        <div className="saas-panel rounded-3xl p-8 sm:p-10 border border-white/[0.1]">
          <div className="mb-8">
            <Badge variant="primary" dot={true}>Platform Architecture</Badge>
            <h3 className="text-2xl sm:text-3xl font-black text-white mt-2 font-display">
              Why JanSetu is a Paradigm Shift for Societal Problem Solving
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="p-5 rounded-2xl saas-card space-y-2">
              <div className="flex items-center space-x-2 text-blue-400 font-bold text-sm">
                <Cpu className="w-4 h-4" />
                <span>Semantic Duplicate Clustering</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed font-normal">
                Connects related community complaints into high-priority regional initiatives using semantic embeddings.
              </p>
            </div>

            <div className="p-5 rounded-2xl saas-card space-y-2">
              <div className="flex items-center space-x-2 text-teal-400 font-bold text-sm">
                <GraduationCap className="w-4 h-4" />
                <span>Explainable HEI Matching</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed font-normal">
                Recommends institutions based on faculty publications, accredited labs, student capabilities, and field proximity.
              </p>
            </div>

            <div className="p-5 rounded-2xl saas-card space-y-2">
              <div className="flex items-center space-x-2 text-purple-400 font-bold text-sm">
                <Building2 className="w-4 h-4" />
                <span>Industry & CSR Co-Funding</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed font-normal">
                Connects Corporate Social Responsibility (CSR) programs directly with academic prototypes to guarantee funding and field hardware.
              </p>
            </div>

            <div className="p-5 rounded-2xl saas-card space-y-2">
              <div className="flex items-center space-x-2 text-amber-400 font-bold text-sm">
                <TrendingUp className="w-4 h-4" />
                <span>AI Milestone Delay Detection</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed font-normal">
                Continuous project intelligence monitors seasonal windows and alerts government administrators before projects risk seasonal obsolescence.
              </p>
            </div>

            <div className="p-5 rounded-2xl saas-card space-y-2">
              <div className="flex items-center space-x-2 text-emerald-400 font-bold text-sm">
                <CheckCircle2 className="w-4 h-4" />
                <span>Evidence-Based Impact</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed font-normal">
                Projects require baseline comparison, community feedback audits, and digital sign-off from state nodal officers.
              </p>
            </div>

            <div className="p-5 rounded-2xl saas-card space-y-2">
              <div className="flex items-center space-x-2 text-rose-400 font-bold text-sm">
                <Users className="w-4 h-4" />
                <span>Rural-First Accessibility</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed font-normal">
                Designed for grassroots adoption with Hindi + English UI, speech-to-text input, and localized advisory output.
              </p>
            </div>
          </div>
        </div>
      </section>
      </div>

    </div>
  );
};
