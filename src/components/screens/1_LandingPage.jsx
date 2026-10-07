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
            <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-navy-850/80 backdrop-blur-sm border border-blue-500/30 text-xs font-semibold text-blue-300 shadow-glow-sm">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>SIH 2026 Problem ID: SIH26043</span>
              <span className="text-slate-400">•</span>
              <span className="text-amber-300">Govt. of Jharkhand</span>
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
              className="px-6 py-3.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-sm shadow-glow-md flex items-center space-x-2 transition-all hover:scale-105"
            >
              <span>{language === 'hi' ? "समस्या दर्ज करें" : "Report a Community Challenge"}</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              to="/problems"
              className="px-6 py-3.5 rounded-xl bg-navy-850 hover:bg-navy-800 text-slate-200 border border-navy-700 font-semibold text-sm flex items-center space-x-2 transition-all hover:border-blue-500/50"
            >
              <Layers className="w-4 h-4 text-blue-400" />
              <span>Browse Uploaded Problems</span>
            </Link>
          </div>

          <div className="pt-2 text-xs text-slate-400 flex items-center justify-center space-x-4">
            <span className="flex items-center space-x-1">
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span>Closed-Loop Innovation</span>
            </span>
            <span className="flex items-center space-x-1">
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span>Explainable AI Matching</span>
            </span>
            <span className="flex items-center space-x-1">
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span>Evidence-Based Impact</span>
            </span>
          </div>

        </div>
      </section>



      {/* How JanSetu Works: The Closed Loop Innovation Pipeline */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        <div className="text-center max-w-3xl mx-auto mb-12 space-y-3">
          <Badge variant="teal">The Closed-Loop Ecosystem</Badge>
          <h2 className="text-3xl sm:text-4xl font-black text-white font-display">
            How Community Problems Become Deployable Solutions
          </h2>
          <p className="text-sm text-slate-400">
            Traditional portals stop at grievance logging. JanSetu operates a full 6-phase innovation lifecycle powered by explainable AI and institutional accountability.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          
          <div className="glass-card rounded-2xl p-5 border border-navy-700/80 space-y-3 relative group hover:border-blue-500/40 transition-colors">
            <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400 font-bold text-sm">
              01
            </div>
            <h4 className="text-sm font-bold text-white">Citizen Report</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Bilingual crowdsourcing with voice input, geo-tagging, and photo evidence.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-5 border border-navy-700/80 space-y-3 relative group hover:border-indigo-500/40 transition-colors">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-bold text-sm">
              02
            </div>
            <h4 className="text-sm font-bold text-white">AI Intelligence</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Domain scoring, entity extraction, and semantic duplicate clustering.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-5 border border-navy-700/80 space-y-3 relative group hover:border-amber-500/40 transition-colors">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 font-bold text-sm">
              03
            </div>
            <h4 className="text-sm font-bold text-white">Govt Validation</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Official verification by District/State authorities and nodal department assignment.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-5 border border-navy-700/80 space-y-3 relative group hover:border-teal-500/40 transition-colors">
            <div className="w-10 h-10 rounded-xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400 font-bold text-sm">
              04
            </div>
            <h4 className="text-sm font-bold text-white">HEI Matching</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Explainable AI pairs challenges with faculty, specialized labs, and student teams.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-5 border border-navy-700/80 space-y-3 relative group hover:border-purple-500/40 transition-colors">
            <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 font-bold text-sm">
              05
            </div>
            <h4 className="text-sm font-bold text-white">Industry / CSR</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Enterprises provide milestone seed funding, hardware, and field trial logistics.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-5 border border-navy-700/80 space-y-3 relative group hover:border-emerald-500/40 transition-colors">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 font-bold text-sm">
              06
            </div>
            <h4 className="text-sm font-bold text-white">Verified Impact</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Before/after metrics, farmer satisfaction, and digital signature by state authority.
            </p>
          </div>

        </div>
      </section>

      {/* Key Differentiators Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        <div className="glass-panel rounded-3xl p-8 border border-navy-700/80">
          <div className="mb-8">
            <Badge variant="primary">Platform Architecture</Badge>
            <h3 className="text-2xl font-bold text-white mt-2 font-display">
              Why JanSetu is a Paradigm Shift for Societal Problem Solving
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="p-5 rounded-2xl bg-navy-850/60 border border-navy-700 space-y-2">
              <div className="flex items-center space-x-2 text-blue-400 font-bold text-sm">
                <Cpu className="w-4 h-4" />
                <span>Semantic Duplicate Clustering</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Connects related community complaints into high-priority regional initiatives using semantic embeddings.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-navy-850/60 border border-navy-700 space-y-2">
              <div className="flex items-center space-x-2 text-teal-400 font-bold text-sm">
                <GraduationCap className="w-4 h-4" />
                <span>Explainable HEI Matching</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Recommends institutions based on faculty publications, accredited labs, student capabilities, and field proximity.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-navy-850/60 border border-navy-700 space-y-2">
              <div className="flex items-center space-x-2 text-purple-400 font-bold text-sm">
                <Building2 className="w-4 h-4" />
                <span>Industry & CSR Co-Funding</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Connects Corporate Social Responsibility (CSR) programs directly with academic prototypes to guarantee funding and field hardware.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-navy-850/60 border border-navy-700 space-y-2">
              <div className="flex items-center space-x-2 text-amber-400 font-bold text-sm">
                <TrendingUp className="w-4 h-4" />
                <span>AI Milestone Delay Detection</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Continuous project intelligence monitors seasonal windows and alerts government administrators before projects risk seasonal obsolescence.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-navy-850/60 border border-navy-700 space-y-2">
              <div className="flex items-center space-x-2 text-emerald-400 font-bold text-sm">
                <CheckCircle2 className="w-4 h-4" />
                <span>Evidence-Based Impact</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Projects require baseline comparison, community feedback audits, and digital sign-off from state nodal officers.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-navy-850/60 border border-navy-700 space-y-2">
              <div className="flex items-center space-x-2 text-rose-400 font-bold text-sm">
                <Users className="w-4 h-4" />
                <span>Rural-First Accessibility</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
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
