import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { JanSetuProvider } from './context/JanSetuContext';
import { Navbar } from './components/layout/Navbar';
import { Footer } from './components/layout/Footer';
import Particles from './components/effects/Particles';
import { ProtectedRoute } from './components/common/ProtectedRoute';

// Public Screens
import { LandingPage } from './components/screens/1_LandingPage';
import { CitizenPortal } from './components/screens/2_CitizenPortal';
import { ProblemsCatalog } from './components/screens/10_ProblemsCatalog';
import { AuthLogin } from './components/screens/AuthLogin';

// Official Restricted Screens
import { AiIntelligence } from './components/screens/3_AiIntelligence';
import { GovernmentDashboard } from './components/screens/4_GovernmentDashboard';
import { UniversityMatching } from './components/screens/5_UniversityMatching';
import { UniversityWorkspace } from './components/screens/6_UniversityWorkspace';
import { IndustryCollaboration } from './components/screens/7_IndustryCollaboration';
import { ProjectLifecycle } from './components/screens/8_ProjectLifecycle';
import { ImpactDashboard } from './components/screens/9_ImpactDashboard';

function AppLayout() {
  const location = useLocation();
  const isLandingPage = location.pathname === '/';

  return (
    <div className="relative min-h-screen bg-navy-950 text-slate-100 flex flex-col selection:bg-blue-600 selection:text-white">
      {/* Dynamic Background for pages other than landing page */}
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
      
      <main className="relative z-10 flex-grow pt-24 sm:pt-28">
        <Routes>
          {/* Public Access Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/citizen-portal" element={<CitizenPortal />} />
          <Route path="/problems" element={<ProblemsCatalog />} />
          <Route path="/challenges" element={<ProblemsCatalog />} />
          <Route path="/login" element={<AuthLogin />} />

          {/* Official Restricted Routes (Protected from Public Access) */}
          <Route 
            path="/government-dashboard" 
            element={
              <ProtectedRoute requireOfficial deskTitle="Government Administration & Validation Desk">
                <GovernmentDashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/ai-intelligence" 
            element={
              <ProtectedRoute requireOfficial deskTitle="AI Intelligence & Semantic Triaging Desk">
                <AiIntelligence />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/university-matching" 
            element={
              <ProtectedRoute requireOfficial deskTitle="Higher Education Institution Matching Desk">
                <UniversityMatching />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/university-workspace" 
            element={
              <ProtectedRoute requireOfficial deskTitle="University Research & Development Workspace">
                <UniversityWorkspace />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/industry-collaboration" 
            element={
              <ProtectedRoute requireOfficial deskTitle="Industry CSR Co-Funding Desk">
                <IndustryCollaboration />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/project-lifecycle" 
            element={
              <ProtectedRoute requireOfficial deskTitle="State Project Lifecycle Desk">
                <ProjectLifecycle />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/impact-dashboard" 
            element={
              <ProtectedRoute requireOfficial deskTitle="Verified Societal Impact & Audit Desk">
                <ImpactDashboard />
              </ProtectedRoute>
            } 
          />

          {/* Catch-all redirect */}
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
