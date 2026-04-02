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
        </div>

        <div className="mt-4">
          <h3 className="font-display text-sm tracking-wide">{product.name}</h3>
          <div className="flex items-center justify-between mt-2">
            <span className="font-mono text-xs tracking-[0.15em] text-sovereign-graphite">
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
            </div>
          </div>
        </div>
      </motion.div>
    </Link>
  );
}
