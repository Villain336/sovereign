'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { NAV_LINKS, CATEGORY_LINKS } from '@/lib/constants';

interface NavOverlayProps {
  onClose: () => void;
}

export default function NavOverlay({ onClose }: NavOverlayProps) {
  return (
    <motion.div
      initial={{ clipPath: 'circle(0% at calc(100% - 40px) 32px)' }}
      animate={{ clipPath: 'circle(150% at calc(100% - 40px) 32px)' }}
      exit={{ clipPath: 'circle(0% at calc(100% - 40px) 32px)' }}
      transition={{ duration: 0.6, ease: [0.25, 0.1, 0.25, 1] }}
      className="fixed inset-0 z-40 bg-sovereign-carbon overflow-y-auto"
    >
      <div className="w-full max-w-7xl mx-auto px-6 md:px-16 pt-24 pb-16">
        {/* Main nav links */}
        <nav className="flex flex-col gap-1 mb-12">
          {NAV_LINKS.map((link, i) => (
            <motion.div
              key={link.href}
              initial={{ opacity: 0, x: -40 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 + i * 0.06, duration: 0.5 }}
            >
              <Link
                href={link.href}
                onClick={onClose}
                className="block text-sovereign-white font-display text-4xl md:text-6xl lg:text-7xl tracking-tight hover:text-sovereign-chrome transition-colors duration-300 py-1"
              >
                {link.label}
              </Link>
            </motion.div>
          ))}
        </nav>

        {/* Category links */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <span className="font-mono text-[9px] tracking-[0.4em] text-sovereign-graphite block mb-4">
            CATEGORIES
          </span>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-x-8 gap-y-2">
            {CATEGORY_LINKS.map((link, i) => (
              <motion.div
                key={link.href}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.55 + i * 0.03 }}
              >
                <Link
                  href={link.href}
                  onClick={onClose}
                  className="font-mono text-sm tracking-[0.15em] text-sovereign-graphite hover:text-sovereign-white transition-colors duration-200 block py-1"
                >
                  {link.label}
                </Link>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Bottom info */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="mt-16 flex gap-8 font-mono text-xs text-sovereign-graphite tracking-[0.2em]"
        >
          <span>INSTAGRAM</span>
          <span>CONTACT</span>
          <span>SHIPPING</span>
        </motion.div>
      </div>
    </motion.div>
  );
}
