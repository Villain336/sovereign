'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function AnnouncementBar() {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) return null;

  const messages = [
    'FREE SHIPPING ON ORDERS OVER $100',
    'FREE 30-DAY RETURNS ON ALL ORDERS',
    'SUSTAINABLY MADE — ETHICALLY SOURCED',
  ];

  return (
    <div className="fixed top-0 left-0 right-0 z-[55] bg-sovereign-carbon text-sovereign-white">
      <div className="relative flex items-center justify-center h-8">
        <AnimatePresence mode="wait">
          <motion.span
            key={messages[0]}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="font-mono text-[9px] tracking-[0.35em]"
          >
            {messages[0]}
          </motion.span>
        </AnimatePresence>
        <button
          onClick={() => setIsVisible(false)}
          className="absolute right-4 font-mono text-[10px] text-sovereign-graphite hover:text-white transition-colors"
          aria-label="Close announcement"
        >
          ✕
        </button>
      </div>
    </div>
  );
}
