'use client';

import { useRef, useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { looks } from '@/lib/lookbook';
import LookbookSlide from '@/components/lookbook/LookbookSlide';

export default function LookbookPage() {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    const container = scrollRef.current;
    if (!container) return;
    const handleScroll = () => {
      const index = Math.round(container.scrollLeft / window.innerWidth);
      setActiveIndex(index);
    };
    container.addEventListener('scroll', handleScroll, { passive: true });
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollTo = (index: number) => {
    scrollRef.current?.scrollTo({ left: index * window.innerWidth, behavior: 'smooth' });
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' && activeIndex < looks.length - 1) scrollTo(activeIndex + 1);
      if (e.key === 'ArrowLeft' && activeIndex > 0) scrollTo(activeIndex - 1);
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeIndex]);

  return (
    <div className="relative">
      {/* Horizontal scroll container */}
      <div
        ref={scrollRef}
        className="flex overflow-x-auto snap-x snap-mandatory no-scrollbar"
        style={{ scrollSnapType: 'x mandatory' }}
      >
        {looks.map((look, i) => (
          <LookbookSlide key={look.id} look={look} index={i} />
        ))}
      </div>

      {/* Dot navigation */}
      <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 flex gap-3">
        {looks.map((_, i) => (
          <button
            key={i}
            onClick={() => scrollTo(i)}
            className={`transition-all duration-300 ${
              i === activeIndex ? 'w-8 h-2 bg-white' : 'w-2 h-2 bg-white/30 hover:bg-white/50'
            }`}
            aria-label={`Go to look ${i + 1}`}
          />
        ))}
      </div>

      {/* Instruction */}
      <motion.div
        initial={{ opacity: 1 }}
        animate={{ opacity: activeIndex > 0 ? 0 : 1 }}
        className="fixed bottom-8 right-8 z-50"
      >
        <span className="font-mono text-[9px] tracking-[0.3em] text-white/40">
          SCROLL OR USE ARROW KEYS
        </span>
      </motion.div>
    </div>
  );
}
