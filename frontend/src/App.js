import React from 'react';
import './App.css';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Header from './components/Header';
import HeroSection from './components/HeroSection';
import ShowcaseCarousel from './components/ShowcaseCarousel';
import FeaturesSection from './components/FeaturesSection';
import FooterSection from './components/FooterSection';
import MatrixRain from './components/MatrixRain';
import AuthPage from './pages/AuthPage';
import DashboardPage from './pages/DashboardPage';
import ChatPage from './pages/ChatPage';
import SharePage from './pages/SharePage';

const Home = () => {
  return (
    <div className="relative min-h-screen bg-white overflow-x-hidden">
      {/* Background gradient overlay */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse at 75% 15%, rgba(186, 230, 253, 0.4) 0%, rgba(255,255,255,0) 50%), radial-gradient(ellipse at 60% 50%, rgba(207, 250, 254, 0.25) 0%, rgba(255,255,255,0) 45%), radial-gradient(ellipse at 40% 70%, rgba(221, 214, 254, 0.15) 0%, rgba(255,255,255,0) 40%)',
          zIndex: 0,
        }}
      />
      <MatrixRain />
      <div className="relative" style={{ zIndex: 1 }}>
        <Header />
        <HeroSection />
        <ShowcaseCarousel />
        <FeaturesSection />
        <FooterSection />
      </div>
    </div>
  );
};

// Protected route wrapper
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return <div className="min-h-screen flex items-center justify-center"><div className="w-8 h-8 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" /></div>;
  if (!user) return <Navigate to="/auth" replace />;
  return children;
};

function App() {
  return (
    <div className="App">
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/auth" element={<AuthPage />} />
            <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
            <Route path="/chat" element={<ProtectedRoute><ChatPage /></ProtectedRoute>} />
            <Route path="/share/:slug" element={<SharePage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </div>
  );
}

export default App;
