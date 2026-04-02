'use client';

import { motion } from 'framer-motion';
import SceneLoader from '@/components/three/SceneLoader';
import Button from '@/components/ui/Button';
import Link from 'next/link';

export default function HeroBlock() {
  return (
    <section className="relative w-full h-screen flex items-center overflow-hidden bg-sovereign-white">
      {/* 3D Chrome Scene — background layer */}
      <div className="absolute inset-0 z-0">
        <SceneLoader variant="hero" />
      </div>

      {/* Content overlay */}
      <div className="relative z-10 w-full max-w-7xl mx-auto px-6 md:px-16">
        <div className="max-w-2xl">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.5, ease: [0.25, 0.1, 0.25, 1] }}
          >
            <span className="font-mono text-[10px] tracking-[0.5em] text-sovereign-graphite block mb-6">
              SEASON 001
            </span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.7, ease: [0.25, 0.1, 0.25, 1] }}
            className="font-display text-6xl md:text-8xl lg:text-9xl font-light tracking-tight text-sovereign-carbon leading-[0.9]"
          >
            THE
            <br />
            FUTURE
            <br />
            IS
            <br />
            <span className="font-medium">QUIET</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 1.2 }}
            className="font-mono text-[11px] tracking-[0.2em] text-sovereign-graphite mt-8 max-w-sm leading-relaxed"
          >
            PRECISION-ENGINEERED GARMENTS FOR THE MODERN HUMAN.
            NO LOGOS. NO NOISE. JUST ESSENTIAL CLOTHING.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1.5 }}
            className="mt-10 flex gap-4"
          >
            <Link href="/collections">
              <Button variant="filled" size="lg">EXPLORE</Button>
            </Link>
            <Link href="/about">
              <Button variant="outline" size="lg">OUR STORY</Button>
            </Link>
          </motion.div>
        </div>
      </div>

      {/* Bottom scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 2, duration: 1 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10"
      >
        <motion.div
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="w-px h-12 bg-sovereign-chrome"
        />
      </motion.div>
    </section>
  );
}
