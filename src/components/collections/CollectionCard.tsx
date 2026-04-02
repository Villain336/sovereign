'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import GradientPlaceholder from '@/components/ui/GradientPlaceholder';
import { Collection } from '@/types';
import { getProductsByCollection } from '@/lib/products';

export default function CollectionCard({ collection }: { collection: Collection }) {
  const productCount = getProductsByCollection(collection.slug).length;

  return (
    <Link href={`/collections/${collection.slug}`} className="group block">
      <motion.div whileHover={{ y: -4 }} transition={{ duration: 0.3 }}>
        <div className="relative overflow-hidden aspect-[4/3]">
          <GradientPlaceholder
            gradient={collection.gradient}
            className="absolute inset-0 transition-transform duration-700 group-hover:scale-105"
          />
          <div className="relative z-10 p-6 md:p-8 flex flex-col justify-end h-full">
            <span className="font-mono text-[9px] tracking-[0.3em] text-white/50">
              {productCount} {productCount === 1 ? 'PIECE' : 'PIECES'}
            </span>
            <h3 className="font-display text-2xl md:text-3xl text-white font-light tracking-wide mt-1">
              {collection.name}
            </h3>
            <p className="font-mono text-[10px] text-white/60 tracking-[0.15em] mt-2 max-w-sm">
              {collection.description}
            </p>
          </div>
        </div>
      </motion.div>
    </Link>
  );
}
