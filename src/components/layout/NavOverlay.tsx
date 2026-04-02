'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { NAV_LINKS } from '@/lib/constants';

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
      className="fixed inset-0 z-40 bg-sovereign-carbon flex items-center"
    >
      <div className="w-full max-w-7xl mx-auto px-6 md:px-16">
        <nav className="flex flex-col gap-2">
          {NAV_LINKS.map((link, i) => (
            <motion.div
              key={link.href}
              initial={{ opacity: 0, x: -40 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 + i * 0.08, duration: 0.5 }}
            >
              <Link
                href={link.href}
                onClick={onClose}
                className="block text-sovereign-white font-display text-5xl md:text-7xl lg:text-8xl tracking-tight hover:text-sovereign-chrome transition-colors duration-300 py-2"
              >
                {link.label}
              </Link>
            </motion.div>
          ))}
        </nav>

        {/* Bottom info */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-16 flex gap-12 font-mono text-xs text-sovereign-graphite tracking-[0.2em]"
        >
          <span>INSTAGRAM</span>
          <span>CONTACT</span>
          <span>SHIPPING</span>
        </motion.div>
      </div>
    </motion.div>
  );
}
