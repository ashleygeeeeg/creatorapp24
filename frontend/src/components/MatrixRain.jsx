import React, { useEffect, useRef } from 'react';

const MatrixRain = () => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = document.documentElement.scrollHeight || window.innerHeight * 4;
    };
    resizeCanvas();

    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-=*&$#@!?<>{}[]|/~';
    const fontSize = 18;
    const colSpacing = fontSize * 2;
    const columns = Math.floor(canvas.width / colSpacing);
    
    // Initialize drops at random positions
    const drops = [];
    const speeds = [];
    const charOpacities = [];
    
    for (let i = 0; i < columns; i++) {
      drops.push(Math.random() * -50);
      speeds.push(0.2 + Math.random() * 0.5);
      charOpacities.push(0.04 + Math.random() * 0.07);
    }

    // Static character grid
    const staticChars = [];
    const rows = Math.floor(canvas.height / fontSize);
    for (let r = 0; r < rows; r++) {
      staticChars[r] = [];
      for (let c = 0; c < columns; c++) {
        staticChars[r][c] = chars[Math.floor(Math.random() * chars.length)];
      }
    }

    // Draw static background chars once
    const drawStaticBg = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.font = `${fontSize}px "Courier New", monospace`;
      
      for (let r = 0; r < rows; r++) {
        for (let c = 0; c < columns; c++) {
          const x = c * colSpacing;
          const y = r * fontSize;
          // Only draw on left portion (60% of width)
          if (x < canvas.width * 0.55) {
            ctx.fillStyle = `rgba(200, 200, 210, ${0.12 + Math.random() * 0.08})`;
            ctx.fillText(staticChars[r][c], x, y);
          }
        }
      }
    };

    drawStaticBg();

    // Animate falling highlights
    let frame = 0;
    const animate = () => {
      frame++;
      if (frame % 4 === 0) { // Slow down animation
        for (let i = 0; i < drops.length; i++) {
          const x = i * colSpacing;
          if (x >= canvas.width * 0.55) continue;
          
          const row = Math.floor(drops[i]);
          if (row >= 0 && row < rows) {
            // Briefly brighten the character at drop position
            const y = row * fontSize;
            // Clear previous character area
            ctx.fillStyle = 'rgba(255, 255, 255, 1)';
            ctx.fillRect(x - 2, y - fontSize + 2, fontSize * 1.5, fontSize + 2);
            // Redraw with slightly higher opacity
            ctx.font = `${fontSize}px "Courier New", monospace`;
            ctx.fillStyle = `rgba(180, 185, 195, ${0.2 + Math.random() * 0.1})`;
            const char = chars[Math.floor(Math.random() * chars.length)];
            ctx.fillText(char, x, y);
          }
          
          drops[i] += speeds[i];
          
          if (drops[i] * fontSize > canvas.height) {
            drops[i] = Math.random() * -20;
            speeds[i] = 0.2 + Math.random() * 0.5;
          }
        }
      }
      requestAnimationFrame(animate);
    };

    const animId = requestAnimationFrame(animate);

    const handleResize = () => {
      resizeCanvas();
      drawStaticBg();
    };
    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute top-0 left-0 w-full pointer-events-none"
      style={{ zIndex: 0, opacity: 0.7 }}
    />
  );
};

export default MatrixRain;
