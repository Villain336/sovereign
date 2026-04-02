'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import GradientPlaceholder from '@/components/ui/GradientPlaceholder';

interface ProductGalleryProps {
  gradient: [string, string];
  name: string;
}

export default function ProductGallery({ gradient, name }: ProductGalleryProps) {
  const [activeIndex, setActiveIndex] = useState(0);

  // Generate slight gradient variations for "multiple views"
  const views = [
    gradient,
    [gradient[1], gradient[0]] as [string, string],
    [gradient[0], '#f5f5f5'] as [string, string],
  ];

  return (
    <div className="flex flex-col gap-3">
      {/* Main image */}
      <div className="relative overflow-hidden aspect-[3/4]">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeIndex}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="absolute inset-0"
          >
            <GradientPlaceholder gradient={views[activeIndex]} className="w-full h-full" />
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Thumbnails */}
      <div className="flex gap-2">
        {views.map((view, i) => (
          <button
            key={i}
            onClick={() => setActiveIndex(i)}
            className={`w-16 h-20 flex-shrink-0 transition-opacity ${
              i === activeIndex ? 'opacity-100 ring-1 ring-sovereign-carbon' : 'opacity-50 hover:opacity-75'
            }`}
            aria-label={`View ${i + 1} of ${name}`}
          >
            <GradientPlaceholder gradient={view} className="w-full h-full" />
          </button>
        ))}
      </div>
    </div>
  );
}
