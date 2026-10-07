import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { JanSetuProvider } from './context/JanSetuContext';
import { Navbar } from './components/layout/Navbar';
import { Footer } from './components/layout/Footer';
import Particles from './components/effects/Particles';

// Screens
import { LandingPage } from './components/screens/1_LandingPage';
import { CitizenPortal } from './components/screens/2_CitizenPortal';
import { AiIntelligence } from './components/screens/3_AiIntelligence';
import { GovernmentDashboard } from './components/screens/4_GovernmentDashboard';
import { UniversityMatching } from './components/screens/5_UniversityMatching';
import { UniversityWorkspace } from './components/screens/6_UniversityWorkspace';
import { IndustryCollaboration } from './components/screens/7_IndustryCollaboration';
import { ProjectLifecycle } from './components/screens/8_ProjectLifecycle';
import { ImpactDashboard } from './components/screens/9_ImpactDashboard';
import { ProblemsCatalog } from './components/screens/10_ProblemsCatalog';

function AppLayout() {
  const location = useLocation();
  const isLandingPage = location.pathname === '/';

  return (
    <div className="relative min-h-screen bg-navy-950 text-slate-100 flex flex-col selection:bg-blue-600 selection:text-white">
      {/* Dynamic Background for all pages OTHER than the landing page */}
      {!isLandingPage && (
        <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
          <div style={{ width: '100%', height: '100%', position: 'relative' }}>
            <Particles
              particleColors={["#0b053e"]}
              particleCount={1000}
              particleSpread={10}
              speed={0.1}
              particleBaseSize={100}
              moveParticlesOnHover={true}
              alphaParticles={false}
              disableRotation={false}
            />
          </div>
        </div>
      )}

      <Navbar />
      
      <main className="relative z-10 flex-grow">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/citizen-portal" element={<CitizenPortal />} />
          <Route path="/ai-intelligence" element={<AiIntelligence />} />
          <Route path="/government-dashboard" element={<GovernmentDashboard />} />
          <Route path="/university-matching" element={<UniversityMatching />} />
          <Route path="/university-workspace" element={<UniversityWorkspace />} />
          <Route path="/industry-collaboration" element={<IndustryCollaboration />} />
          <Route path="/project-lifecycle" element={<ProjectLifecycle />} />
          <Route path="/impact-dashboard" element={<ImpactDashboard />} />
          <Route path="/problems" element={<ProblemsCatalog />} />
          <Route path="/challenges" element={<ProblemsCatalog />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      <Footer />
    </div>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <JanSetuProvider>
          <AppLayout />
        </JanSetuProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;

