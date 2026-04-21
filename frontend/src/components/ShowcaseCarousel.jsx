import React, { useRef, useEffect, useState } from 'react';
import { showcaseItems } from '../data/mockData';

const ShowcaseCarousel = () => {
  const scrollRef = useRef(null);
  const [isPaused, setIsPaused] = useState(false);

  // Double the items for infinite scroll effect
  const doubledItems = [...showcaseItems, ...showcaseItems];

  useEffect(() => {
    const scrollContainer = scrollRef.current;
    if (!scrollContainer) return;

    let animationId;
    let scrollPos = 0;
    const speed = 0.5;

    const animate = () => {
      if (!isPaused) {
        scrollPos += speed;
        const halfWidth = scrollContainer.scrollWidth / 2;
        if (scrollPos >= halfWidth) {
          scrollPos = 0;
        }
        scrollContainer.scrollLeft = scrollPos;
      }
      animationId = requestAnimationFrame(animate);
    };

    animationId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationId);
  }, [isPaused]);

  return (
    <section className="py-16 overflow-hidden relative">
      <div className="text-center mb-8">
        <p className="text-gray-500 text-lg">
          <span className="font-bold text-gray-900 text-2xl">3M+</span>{' '}
          <span className="text-gray-500">users worldwide building & launching</span>
        </p>
        <p className="text-gray-500 text-lg">real applications in minutes.</p>
      </div>

      <div
        ref={scrollRef}
        className="flex gap-6 overflow-hidden px-6 cursor-grab"
        onMouseEnter={() => setIsPaused(true)}
        onMouseLeave={() => setIsPaused(false)}
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        {doubledItems.map((item, index) => (
          <div
            key={`${item.id}-${index}`}
            className="flex-shrink-0 flex gap-4 items-end"
          >
            {/* Mobile mockup */}
            <div className="w-32 rounded-2xl overflow-hidden shadow-lg border-2 border-gray-800 bg-black flex-shrink-0">
              <img
                src={item.mobile}
                alt="Mobile app"
                className="w-full h-56 object-cover"
                loading="lazy"
              />
            </div>
            {/* Laptop mockup */}
            <div className="w-80 rounded-xl overflow-hidden shadow-lg bg-white border border-gray-200 flex-shrink-0">
              <div className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 border-b border-gray-200">
                <div className="w-2 h-2 rounded-full bg-red-400"></div>
                <div className="w-2 h-2 rounded-full bg-yellow-400"></div>
                <div className="w-2 h-2 rounded-full bg-green-400"></div>
              </div>
              <img
                src={item.laptop}
                alt="Laptop app"
                className="w-full h-48 object-cover"
                loading="lazy"
              />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default ShowcaseCarousel;
