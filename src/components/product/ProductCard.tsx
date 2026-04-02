'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import GradientPlaceholder from '@/components/ui/GradientPlaceholder';
import { Product } from '@/types';
import { EARTH_COLORS } from '@/lib/constants';

export default function ProductCard({ product }: { product: Product }) {
  return (
    <Link href={`/product/${product.id}`} className="group block">
      <motion.div
        whileHover={{ y: -4 }}
        transition={{ duration: 0.3 }}
      >
        <div className="relative overflow-hidden aspect-[3/4]">
          <GradientPlaceholder
            gradient={product.gradient}
            className="absolute inset-0 transition-transform duration-700 group-hover:scale-105"
          />

          {/* Badges */}
          <div className="absolute top-3 left-3 z-10 flex flex-col gap-1.5">
            {product.tags.includes('new') && (
              <span className="font-mono text-[8px] tracking-[0.3em] bg-sovereign-white text-sovereign-carbon px-2 py-1">
                NEW
              </span>
            )}
            {product.tags.includes('featured') && (
              <span className="font-mono text-[8px] tracking-[0.3em] bg-sovereign-carbon text-sovereign-white px-2 py-1">
                FEATURED
              </span>
            )}
          </div>

          {/* Hover overlay — quick view CTA */}
          <div className="absolute inset-x-0 bottom-0 z-10 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out">
            <div className="bg-sovereign-white/95 backdrop-blur-sm px-4 py-3 flex items-center justify-between">
              <span className="font-mono text-[9px] tracking-[0.2em] text-sovereign-carbon">QUICK VIEW</span>
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none" className="text-sovereign-carbon">
                <path d="M1 7H13M13 7L8 2M13 7L8 12" stroke="currentColor" strokeWidth="1" />
              </svg>
            </div>
          </div>
        </div>

        <div className="mt-4">
          <h3 className="font-display text-sm tracking-wide leading-snug">{product.name}</h3>
          <div className="flex items-center justify-between mt-2.5">
            <span className="font-mono text-xs tracking-[0.15em] text-sovereign-carbon">
              ${product.price}
            </span>
            <div className="flex gap-1.5">
              {product.colors.slice(0, 4).map((color) => (
                <span
                  key={color}
                  className="w-3 h-3 rounded-full border border-sovereign-silver"
                  style={{ background: EARTH_COLORS[color] }}
                />
              ))}
              {product.colors.length > 4 && (
                <span className="font-mono text-[8px] text-sovereign-graphite self-center">
                  +{product.colors.length - 4}
                </span>
              )}
            </div>
          </div>
          {/* Sizes available */}
          <p className="font-mono text-[8px] tracking-[0.15em] text-sovereign-chrome mt-2">
            {product.sizes.join(' / ')}
          </p>
        </div>
      </motion.div>
    </Link>
  );
}
