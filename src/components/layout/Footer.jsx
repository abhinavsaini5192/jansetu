import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Sparkles, Building2, Award } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="border-t border-navy-800 bg-navy-950 text-slate-400 py-12 px-4 sm:px-6 lg:px-8 mt-16">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
        
        {/* Col 1: Platform identity */}
        <div className="space-y-3 md:col-span-1">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-600 to-teal-400 flex items-center justify-center">
              <span className="text-sm font-bold text-white">JS</span>
            </div>
            <span className="text-lg font-bold text-white font-display tracking-tight">JanSetu</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            AI-Powered Societal Innovation & Collaboration Platform. Converting grassroots community challenges into validated, university-assigned, and industry-supported deployable outcomes.
          </p>
          <div className="pt-2 text-[11px] text-slate-400">
            <span className="text-amber-400 font-semibold">SIH26043</span> • Smart Education Theme
          </div>
        </div>

        {/* Col 2: Institutional Backing */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center space-x-1.5">
            <Building2 className="w-3.5 h-3.5 text-blue-400" />
            <span>Nodal Authorities</span>
          </h4>
          <ul className="text-xs space-y-2">
            <li className="text-slate-300 font-medium">Govt. of Jharkhand</li>
            <li>Department of Higher & Technical Education</li>
            <li>Department of Agriculture & Farmers Welfare</li>
            <li>Higher Education Institutions & Research Labs</li>
            <li>Smart India Hackathon Initiative</li>
          </ul>
        </div>

        {/* Col 3: Innovation Pipeline */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center space-x-1.5">
            <Sparkles className="w-3.5 h-3.5 text-teal-400" />
            <span>Innovation OS</span>
          </h4>
          <ul className="text-xs space-y-1.5 text-slate-400">
            <li><Link to="/citizen-portal" className="hover:text-white transition-colors">1. Citizen Challenge Crowdsourcing</Link></li>
            <li><Link to="/ai-intelligence" className="hover:text-white transition-colors">2. Semantic AI Clustering & Scoring</Link></li>
            <li><Link to="/government-dashboard" className="hover:text-white transition-colors">3. Official Validation & Mandates</Link></li>
            <li><Link to="/university-matching" className="hover:text-white transition-colors">4. Explainable HEI Matching Engine</Link></li>
            <li><Link to="/industry-collaboration" className="hover:text-white transition-colors">5. CSR & Industry Tech Transfer</Link></li>
            <li><Link to="/impact-dashboard" className="hover:text-white transition-colors">6. Verified Societal Impact</Link></li>
          </ul>
        </div>

        {/* Col 4: Platform Security & Standards */}
        <div className="space-y-3 bg-navy-900/60 p-4 rounded-xl border border-navy-800">
          <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center space-x-1.5">
            <Award className="w-3.5 h-3.5 text-amber-400" />
            <span>Open Innovation Standard</span>
          </h4>
          <p className="text-xs text-slate-400 leading-relaxed">
            Standardized societal problem-to-deployment operating system connecting 24 districts with multidisciplinary research institutions across India.
          </p>
          <div className="text-[11px] text-emerald-400 font-medium flex items-center space-x-1">
            <Shield className="w-3 h-3" />
            <span>Government Verified Auditing</span>
          </div>
        </div>

      </div>

      <div className="max-w-7xl mx-auto pt-6 border-t border-navy-900 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400">
        <p>© 2026 JanSetu Platform • Problem ID: SIH26043 • Government of Jharkhand</p>
        <p className="mt-2 sm:mt-0 flex items-center space-x-1">
          <span>Crafted for impactful governance & deployable social innovation</span>
        </p>
      </div>
    </footer>
  );
};
