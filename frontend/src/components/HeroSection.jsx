import React, { useState, useEffect, useCallback } from 'react';
import { Github, Apple, Facebook, Mail } from 'lucide-react';
import { showcaseItems as mockShowcase } from '../data/mockData';
import { fetchShowcase } from '../services/api';

const HeroSection = () => {
  const [items, setItems] = useState(mockShowcase);
  const [currentSlide, setCurrentSlide] = useState(0);

  useEffect(() => {
    fetchShowcase().then(data => {
      if (data && data.length > 0) setItems(data);
    });
  }, []);

  const totalSlides = items.length;

  const nextSlide = useCallback(() => {
    setCurrentSlide((prev) => (prev + 1) % totalSlides);
  }, [totalSlides]);

  const prevSlide = useCallback(() => {
    setCurrentSlide((prev) => (prev - 1 + totalSlides) % totalSlides);
  }, [totalSlides]);

  useEffect(() => {
    const timer = setInterval(nextSlide, 4000);
    return () => clearInterval(timer);
  }, [nextSlide]);

  return (
    <section className="relative min-h-screen flex items-center justify-center px-6 pt-20">
      <div className="max-w-7xl w-full mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        {/* Left - Auth Form */}
        <div className="flex flex-col items-center text-center relative z-10">
          <img
            src="https://assets.emergent.sh/assets/Landing-Hero-E.gif"
            alt="maligeeAi Logo"
            className="w-20 h-20 mb-6"
          />
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-2 leading-tight">
            Build Full-Stack
          </h1>
          <h2
            className="text-3xl md:text-4xl font-bold mb-8 leading-tight"
            style={{
              background: 'linear-gradient(135deg, #3B82F6, #06B6D4, #8B5CF6)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            Web & Mobile Apps in minutes
          </h2>

          {/* Google Button */}
          <button className="w-full max-w-sm flex items-center justify-center gap-3 px-6 py-3.5 bg-gray-800 hover:bg-gray-700 text-white rounded-full font-medium transition-colors duration-200 mb-4">
            <img
              src="https://assets.emergent.sh/assets/Google.svg"
              alt="Google"
              className="w-5 h-5"
            />
            Continue with Google
          </button>

          {/* Social buttons row */}
          <div className="flex items-center gap-3 mb-4 w-full max-w-sm justify-center">
            <button className="flex-1 flex items-center justify-center py-3 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors duration-200">
              <Github className="w-5 h-5 text-gray-700" />
            </button>
            <button className="flex-1 flex items-center justify-center py-3 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors duration-200">
              <Apple className="w-5 h-5 text-gray-700" />
            </button>
            <button className="flex-1 flex items-center justify-center py-3 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors duration-200">
              <Facebook className="w-5 h-5 text-gray-700" />
            </button>
          </div>

          {/* Email Button */}
          <button className="w-full max-w-sm flex items-center justify-center gap-3 px-6 py-3.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full font-medium transition-colors duration-200 mb-4">
            <Mail className="w-5 h-5" />
            Continue with Email
          </button>

          {/* Terms */}
          <p className="text-xs text-gray-500 mt-2">
            By continuing, you agree to our
          </p>
          <p className="text-xs text-gray-500">
            <a href="#" className="underline hover:text-gray-700 transition-colors">Terms of Service</a>
            {' '}and{' '}
            <a href="#" className="underline hover:text-gray-700 transition-colors">Privacy Policy</a>.
          </p>
        </div>

        {/* Right - Showcase */}
        <div className="relative z-10 flex flex-col items-center">
          {/* Built for teams header */}
          <div className="text-center mb-6">
            <div className="flex items-center justify-center gap-2 mb-3">
              <div className="flex -space-x-2">
                <div className="w-9 h-9 rounded-full bg-gray-700 border-2 border-white flex items-center justify-center overflow-hidden">
                  <svg viewBox="0 0 36 36" className="w-full h-full"><circle cx="18" cy="12" r="7" fill="#bbb"/><ellipse cx="18" cy="32" rx="12" ry="10" fill="#bbb"/></svg>
                </div>
                <div className="w-9 h-9 rounded-full bg-blue-500 border-2 border-white flex items-center justify-center overflow-hidden">
                  <svg viewBox="0 0 36 36" className="w-full h-full"><circle cx="18" cy="12" r="7" fill="#93c5fd"/><ellipse cx="18" cy="32" rx="12" ry="10" fill="#93c5fd"/></svg>
                </div>
              </div>
              <h3 className="text-3xl font-bold text-gray-900">Built for teams</h3>
              <div className="flex -space-x-2">
                <div className="w-9 h-9 rounded-full bg-teal-500 border-2 border-white flex items-center justify-center overflow-hidden">
                  <svg viewBox="0 0 36 36" className="w-full h-full"><circle cx="18" cy="12" r="7" fill="#5eead4"/><ellipse cx="18" cy="32" rx="12" ry="10" fill="#5eead4"/></svg>
                </div>
                <div className="w-9 h-9 rounded-full bg-violet-500 border-2 border-white flex items-center justify-center overflow-hidden">
                  <svg viewBox="0 0 36 36" className="w-full h-full"><circle cx="18" cy="12" r="7" fill="#c4b5fd"/><ellipse cx="18" cy="32" rx="12" ry="10" fill="#c4b5fd"/></svg>
                </div>
              </div>
            </div>
            <p className="text-gray-600 text-sm max-w-md mx-auto">
              Build, test and deploy with your favourite people in real-time,
              from concept to launch.
            </p>
          </div>

          {/* Browser Mockup */}
          <div className="relative w-full max-w-xl">
            <div className="rounded-2xl overflow-hidden shadow-2xl bg-white border border-gray-200">
              {/* Browser Chrome */}
              <div className="flex items-center gap-2 px-4 py-2.5 bg-gray-100 border-b border-gray-200">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-400"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                  <div className="w-3 h-3 rounded-full bg-green-400"></div>
                </div>
                <div className="flex-1 flex items-center justify-center">
                  <div className="bg-white rounded-md px-4 py-1 text-xs text-gray-400 border border-gray-200 w-64 text-center">
                    maligeeai.com
                  </div>
                </div>
              </div>
              {/* Content Area - Slide */}
              <div className="relative overflow-hidden" style={{ height: '360px' }}>
                {items.map((item, index) => (
                  <div
                    key={item.id}
                    className="absolute inset-0 transition-all duration-500 ease-in-out flex items-center justify-center"
                    style={{
                      opacity: index === currentSlide ? 1 : 0,
                      transform: `translateX(${(index - currentSlide) * 100}%)`,
                    }}
                  >
                    <img
                      src={item.laptop}
                      alt={`Showcase ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Floating user cursors */}
            <div className="absolute -right-4 top-20 bg-blue-600 text-white text-xs px-3 py-1.5 rounded-full shadow-lg font-medium animate-bounce" style={{ animationDuration: '3s' }}>
              Chris
            </div>
            <div className="absolute left-8 bottom-32 bg-emerald-500 text-white text-xs px-3 py-1.5 rounded-full shadow-lg font-medium animate-bounce" style={{ animationDuration: '2.5s', animationDelay: '0.5s' }}>
              Jane
            </div>
          </div>

          {/* Carousel Controls */}
          <div className="flex items-center gap-4 mt-6">
            <button
              onClick={prevSlide}
              className="w-10 h-10 rounded-full bg-gray-800 hover:bg-gray-700 flex items-center justify-center transition-colors duration-200"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M15 18l-6-6 6-6" />
              </svg>
            </button>
            <div className="flex gap-2">
              {items.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentSlide(index)}
                  className={`transition-all duration-300 rounded-full ${
                    index === currentSlide
                      ? 'w-8 h-2 bg-gray-800'
                      : 'w-2 h-2 bg-gray-300 hover:bg-gray-400'
                  }`}
                />
              ))}
            </div>
            <button
              onClick={nextSlide}
              className="w-10 h-10 rounded-full bg-gray-800 hover:bg-gray-700 flex items-center justify-center transition-colors duration-200"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M9 18l6-6-6-6" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
