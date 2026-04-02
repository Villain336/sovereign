'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useScrollPosition } from '@/hooks/useScrollPosition';

export default function BackToTop() {
  const { isScrolled } = useScrollPosition();

  const scrollToTop = () => window.scrollTo({ top: 0, behavior: 'smooth' });

  return (
    <AnimatePresence>
      {isScrolled && (
        <motion.button
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          onClick={scrollToTop}
          className="fixed bottom-6 right-6 z-40 w-10 h-10 rounded-full chrome-gradient flex items-center justify-center hover:scale-110 transition-transform shadow-lg"
          aria-label="Back to top"
        >
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" className="text-sovereign-carbon">
            <path d="M6 10V2M6 2L2 6M6 2L10 6" stroke="currentColor" strokeWidth="1.5" />
          </svg>
        </motion.button>
      )}
    </AnimatePresence>
  );
}
