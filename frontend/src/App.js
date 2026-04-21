import React from 'react';
import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import HeroSection from './components/HeroSection';
import ShowcaseCarousel from './components/ShowcaseCarousel';
import FeaturesSection from './components/FeaturesSection';
import FooterSection from './components/FooterSection';
import MatrixRain from './components/MatrixRain';

const Home = () => {
  return (
    <div className="relative min-h-screen bg-white overflow-x-hidden">
      {/* Background gradient overlay - matching Emergent's light blue/cyan/purple gradient */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse at 75% 15%, rgba(186, 230, 253, 0.4) 0%, rgba(255,255,255,0) 50%), radial-gradient(ellipse at 60% 50%, rgba(207, 250, 254, 0.25) 0%, rgba(255,255,255,0) 45%), radial-gradient(ellipse at 40% 70%, rgba(221, 214, 254, 0.15) 0%, rgba(255,255,255,0) 40%)',
          zIndex: 0,
        }}
      />
      
      {/* Matrix Rain Background */}
      <MatrixRain />

      {/* Content */}
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

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="*" element={<Home />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
