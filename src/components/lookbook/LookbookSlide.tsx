'use client';

import { motion } from 'framer-motion';
import GradientPlaceholder from '@/components/ui/GradientPlaceholder';
import SceneLoader from '@/components/three/SceneLoader';
import { Look } from '@/types';
import { getProduct } from '@/lib/products';
import Link from 'next/link';

export default function LookbookSlide({ look, index }: { look: Look; index: number }) {
  const lookProducts = look.products.map(getProduct).filter(Boolean);

  return (
    <div className="w-screen h-screen flex-shrink-0 relative overflow-hidden snap-center">
      {/* Gradient background */}
      <GradientPlaceholder gradient={look.gradient} className="absolute inset-0" />

      {/* 3D Chrome accent */}
      <div className="absolute top-0 right-0 w-1/3 h-full opacity-40 pointer-events-none">
        <SceneLoader variant="minimal" />
      </div>

      {/* Content */}
      <div className="relative z-10 h-full flex flex-col justify-end p-8 md:p-16 max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <span className="font-mono text-[10px] tracking-[0.5em] text-white/50">
            LOOK {String(index + 1).padStart(3, '0')}
          </span>
          <h2 className="font-display text-5xl md:text-7xl lg:text-8xl font-light text-white tracking-tight mt-2">
            {look.title}
          </h2>
          <p className="font-mono text-[11px] tracking-[0.2em] text-white/60 mt-4 max-w-md leading-relaxed">
            {look.description.toUpperCase()}
          </p>

          {/* Products in this look */}
          <div className="flex flex-wrap gap-3 mt-8">
            {lookProducts.map((product) => product && (
              <Link
                key={product.id}
                href={`/product/${product.id}`}
                className="font-mono text-[10px] tracking-[0.2em] text-white/70 hover:text-white border border-white/20 hover:border-white/50 px-3 py-2 transition-colors"
              >
                {product.name.toUpperCase()} — ${product.price}
              </Link>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Slide number */}
      <div className="absolute top-8 right-8 md:top-16 md:right-16 z-10">
        <span className="font-mono text-6xl md:text-8xl font-bold text-white/10">
          {String(index + 1).padStart(2, '0')}
        </span>
      </div>
    </div>
  );
}
