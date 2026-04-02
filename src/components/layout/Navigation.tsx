'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useCart } from '@/hooks/useCart';
import NavOverlay from './NavOverlay';
import Link from 'next/link';

export default function Navigation() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { totalItems, toggleCart } = useCart();

  return (
    <>
      {/* Brand mark — top left */}
      <Link
        href="/"
        className="fixed top-6 left-6 z-50 nav-blend font-mono text-xs tracking-[0.4em] hover:opacity-70 transition-opacity"
      >
        SOVEREIGN
      </Link>

      {/* Right side controls */}
      <div className="fixed top-6 right-6 z-50 flex items-center gap-5 nav-blend">
        {/* Search */}
        <Link
          href="/search"
          className="font-mono text-xs tracking-[0.2em] hover:opacity-70 transition-opacity"
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" className="stroke-current">
            <circle cx="5.5" cy="5.5" r="4.5" strokeWidth="1.2" />
            <path d="M9 9L13 13" strokeWidth="1.2" />
          </svg>
        </Link>

        {/* Cart */}
        <button
          onClick={toggleCart}
          className="relative font-mono text-xs tracking-[0.2em] hover:opacity-70 transition-opacity"
        >
          BAG
          {totalItems > 0 && (
            <motion.span
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="absolute -top-2 -right-4 w-4 h-4 bg-white text-black rounded-full text-[9px] flex items-center justify-center font-mono mix-blend-normal"
            >
              {totalItems}
            </motion.span>
          )}
        </button>

        {/* Menu toggle */}
        <button
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          className="flex flex-col gap-[5px] hover:opacity-70 transition-opacity p-1"
          aria-label="Toggle menu"
        >
          <motion.span animate={isMenuOpen ? { rotate: 45, y: 7 } : { rotate: 0, y: 0 }} className="block w-6 h-px bg-current" />
          <motion.span animate={isMenuOpen ? { opacity: 0 } : { opacity: 1 }} className="block w-6 h-px bg-current" />
          <motion.span animate={isMenuOpen ? { rotate: -45, y: -7 } : { rotate: 0, y: 0 }} className="block w-6 h-px bg-current" />
        </button>
      </div>

      <AnimatePresence>
        {isMenuOpen && <NavOverlay onClose={() => setIsMenuOpen(false)} />}
      </AnimatePresence>
    </>
  );
}
