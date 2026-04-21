import React, { useState, useEffect } from 'react';
import { MonitorSmartphone, Bot, Link2 } from 'lucide-react';
import { features as mockFeatures } from '../data/mockData';
import { fetchFeatures } from '../services/api';

const iconMap = {
  'monitor-smartphone': MonitorSmartphone,
  'bot': Bot,
  'link': Link2,
};

// Feature mockup images mapped by type
const mockupImages = {
  library: {
    laptop: "https://assets.emergent.sh/assets/showcase/Laptop1.webp",
    mobile: "https://assets.emergent.sh/assets/showcase/Mob1.webp"
  },
  agent: {
    laptop: "https://assets.emergent.sh/assets/showcase/Laptop2.webp",
    mobile: "https://assets.emergent.sh/assets/showcase/Mob2.webp"
  },
  integration: {
    laptop: "https://assets.emergent.sh/assets/showcase/Laptop3.webp",
    mobile: "https://assets.emergent.sh/assets/showcase/Mob3.webp"
  }
};

const FeaturesSection = () => {
  const [activeFeature, setActiveFeature] = useState(0);
  const [features, setFeatures] = useState(mockFeatures);

  useEffect(() => {
    fetchFeatures().then(data => {
      if (data && data.length > 0) setFeatures(data);
    });
  }, []);

  const currentMockup = mockupImages[features[activeFeature].mockupType];

  return (
    <section className="relative py-24 px-6">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            What can maligeeAi do for you?
          </h2>
          <p className="text-gray-500 text-lg max-w-2xl mx-auto">
            From concept to deployment, maligeeAi handles every aspect of software
            development so you can focus on what matters most - your vision!
          </p>
        </div>

        {/* Features Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          {/* Left - Accordion */}
          <div className="space-y-0">
            {features.map((feature, index) => {
              const Icon = iconMap[feature.icon];
              const isActive = index === activeFeature;

              return (
                <div
                  key={feature.id}
                  className="border-b border-gray-200 last:border-b-0"
                >
                  <button
                    onClick={() => setActiveFeature(index)}
                    className="w-full flex items-center gap-4 py-6 text-left group transition-all duration-200"
                  >
                    <div
                      className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-300 ${
                        isActive
                          ? 'bg-gray-900 text-white'
                          : 'bg-gray-100 text-gray-500 group-hover:bg-gray-200'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                    </div>
                    <span
                      className={`text-xl font-semibold transition-colors duration-200 ${
                        isActive ? 'text-gray-900' : 'text-gray-400 group-hover:text-gray-600'
                      }`}
                    >
                      {feature.title}
                    </span>
                  </button>
                  <div
                    className={`overflow-hidden transition-all duration-500 ease-in-out ${
                      isActive ? 'max-h-40 opacity-100 pb-6' : 'max-h-0 opacity-0'
                    }`}
                  >
                    <p className="text-gray-500 pl-14 leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Right - Mockup Display */}
          <div className="relative">
            <div className="relative">
              {/* Laptop mockup */}
              <div className="rounded-2xl overflow-hidden shadow-2xl bg-white border border-gray-200 transition-all duration-500">
                <div className="flex items-center gap-2 px-4 py-2.5 bg-gray-100 border-b border-gray-200">
                  <div className="flex gap-1.5">
                    <div className="w-3 h-3 rounded-full bg-red-400"></div>
                    <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                    <div className="w-3 h-3 rounded-full bg-green-400"></div>
                  </div>
                  <div className="flex-1 flex items-center justify-center">
                    <div className="bg-white rounded-md px-4 py-1 text-xs text-gray-400 border border-gray-200 w-48 text-center">
                      app.maligeeai.com
                    </div>
                  </div>
                </div>
                <div className="relative overflow-hidden" style={{ height: '380px' }}>
                  {features.map((feature, index) => (
                    <img
                      key={feature.id}
                      src={mockupImages[feature.mockupType].laptop}
                      alt={feature.title}
                      className="absolute inset-0 w-full h-full object-cover transition-all duration-500"
                      style={{
                        opacity: index === activeFeature ? 1 : 0,
                        transform: `scale(${index === activeFeature ? 1 : 1.05})`,
                      }}
                    />
                  ))}
                </div>
              </div>

              {/* Phone mockup */}
              <div
                className="absolute -left-8 bottom-0 w-36 rounded-2xl overflow-hidden shadow-2xl border-4 border-gray-800 bg-black transition-all duration-500"
                style={{ transform: 'translateY(20%)' }}
              >
                <div className="relative" style={{ height: '260px' }}>
                  {features.map((feature, index) => (
                    <img
                      key={feature.id}
                      src={mockupImages[feature.mockupType].mobile}
                      alt={feature.title}
                      className="absolute inset-0 w-full h-full object-cover transition-all duration-500"
                      style={{
                        opacity: index === activeFeature ? 1 : 0,
                      }}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;
