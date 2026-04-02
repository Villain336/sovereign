'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import GradientPlaceholder from '@/components/ui/GradientPlaceholder';
import Button from '@/components/ui/Button';
import ScrollReveal from '@/components/ui/ScrollReveal';
import SceneLoader from '@/components/three/SceneLoader';
import { getFeaturedProducts } from '@/lib/products';
import { EARTH_COLORS } from '@/lib/constants';

export default function FeaturedDrop() {
  const featured = getFeaturedProducts();
  const highlight = featured[2] ?? featured[0];
  if (!highlight) return null;

  return (
    <section className="w-full max-w-7xl mx-auto px-6 md:px-16 py-24 md:py-40 relative overflow-hidden">
      {/* Background chrome accent */}
      <div className="absolute -left-20 top-20 w-[350px] h-[400px] opacity-10 pointer-events-none hidden md:block">
        <SceneLoader variant="icosahedron" />
      </div>

      <ScrollReveal>
        <span className="font-mono text-[10px] tracking-[0.5em] text-sovereign-graphite block mb-12">
          FEATURED DROP
        </span>
      </ScrollReveal>

      <div className="relative z-10 grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-16">
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
            <h2 className="font-display text-4xl md:text-5xl lg:text-6xl font-light tracking-wide mt-4 leading-[1.05]">
              {highlight.name}
            </h2>
            <p className="font-mono text-[11px] text-sovereign-graphite tracking-[0.15em] mt-8 leading-[2] max-w-md">
              {highlight.description.toUpperCase()}
            </p>
            <p className="font-mono text-xl tracking-[0.1em] mt-8">${highlight.price}</p>

            {/* Color options */}
            <div className="flex gap-3 mt-8">
              {highlight.colors.map((color) => (
                <motion.div
                  key={color}
                  whileHover={{ scale: 1.2 }}
                  className="w-7 h-7 rounded-full border border-sovereign-silver cursor-pointer"
                  style={{ background: EARTH_COLORS[color] }}
                />
              ))}
            </div>

            <div className="mt-12">
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
