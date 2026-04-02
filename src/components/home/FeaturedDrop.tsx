'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import GradientPlaceholder from '@/components/ui/GradientPlaceholder';
import Button from '@/components/ui/Button';
import ScrollReveal from '@/components/ui/ScrollReveal';
import { getFeaturedProducts } from '@/lib/products';

export default function FeaturedDrop() {
  const featured = getFeaturedProducts();
  const highlight = featured[2] ?? featured[0];
  if (!highlight) return null;

  return (
    <section className="w-full max-w-7xl mx-auto px-6 md:px-16 py-20 md:py-32">
      <ScrollReveal>
        <span className="font-mono text-[10px] tracking-[0.5em] text-sovereign-graphite block mb-10">
          FEATURED DROP
        </span>
      </ScrollReveal>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8">
        {/* Product image */}
        <ScrollReveal direction="left">
          <Link href={`/product/${highlight.id}`} className="group block">
            <div className="relative overflow-hidden aspect-[3/4]">
              <GradientPlaceholder
                gradient={highlight.gradient}
                className="absolute inset-0 transition-transform duration-1000 group-hover:scale-105"
              />
            </div>
          </Link>
        </ScrollReveal>

        {/* Product info */}
        <ScrollReveal direction="right" className="flex flex-col justify-center">
          <div className="md:pl-8 lg:pl-16">
            <span className="font-mono text-[9px] tracking-[0.4em] text-sovereign-chrome">
              {highlight.collection.toUpperCase()}
            </span>
            <h2 className="font-display text-4xl md:text-5xl lg:text-6xl font-light tracking-wide mt-3">
              {highlight.name}
            </h2>
            <p className="font-mono text-[11px] text-sovereign-graphite tracking-[0.15em] mt-6 leading-relaxed max-w-md">
              {highlight.description}
            </p>
            <p className="font-mono text-lg tracking-[0.1em] mt-6">${highlight.price}</p>

            {/* Color options */}
            <div className="flex gap-3 mt-6">
              {highlight.colors.map((color) => (
                <motion.div
                  key={color}
                  whileHover={{ scale: 1.2 }}
                  className="w-6 h-6 rounded-full border border-sovereign-silver cursor-pointer"
                  style={{
                    background: color === 'sand' ? '#C2B280' : color === 'olive' ? '#708238' : color === 'slate' ? '#6E7B8B' : color === 'charcoal' ? '#36454F' : color === 'cream' ? '#FFFDD0' : color === 'clay' ? '#B66A50' : color === 'stone' ? '#928E85' : '#8A9A5B',
                  }}
                />
              ))}
            </div>

            <div className="mt-10">
              <Link href={`/product/${highlight.id}`}>
                <Button variant="filled" size="lg">VIEW PRODUCT</Button>
              </Link>
            </div>
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
}
