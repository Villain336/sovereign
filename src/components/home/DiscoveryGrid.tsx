'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { products } from '@/lib/products';
import SceneLoader from '@/components/three/SceneLoader';
import { collections } from '@/lib/collections';
import GradientPlaceholder from '@/components/ui/GradientPlaceholder';
import Badge from '@/components/ui/Badge';
import ScrollReveal from '@/components/ui/ScrollReveal';

export default function DiscoveryGrid() {
  const featured = products.filter((p) => p.tags.includes('featured'));
  const newArrivals = products.filter((p) => p.tags.includes('new'));

  return (
    <section className="w-full max-w-7xl mx-auto px-6 md:px-16 py-24 md:py-40 relative overflow-hidden">
      {/* Background chrome shape */}
      <div className="absolute -right-32 top-1/3 w-[400px] h-[500px] opacity-8 pointer-events-none hidden lg:block">
        <SceneLoader variant="cube" />
      </div>

      {/* Section label */}
      <ScrollReveal>
        <span className="font-mono text-[10px] tracking-[0.5em] text-sovereign-graphite">
          DISCOVER
        </span>
      </ScrollReveal>

      {/* Main discovery grid */}
      <div className="relative z-10 mt-12 grid grid-cols-4 md:grid-cols-12 gap-4 md:gap-5">
        {/* Large featured product — 6 cols */}
        <ScrollReveal className="col-span-4 md:col-span-6 md:row-span-2">
          <Link href={`/product/${featured[0]?.id}`} className="group block h-full">
            <div className="relative overflow-hidden h-full min-h-[400px] md:min-h-[600px]">
              <GradientPlaceholder gradient={featured[0]?.gradient ?? ['#928E85', '#C2B280']} className="absolute inset-0 transition-transform duration-700 group-hover:scale-105" />
              <div className="relative z-10 p-6 flex flex-col justify-end h-full">
                {featured[0]?.tags.includes('featured') && <Badge className="self-start mb-3">FEATURED</Badge>}
                <h3 className="font-display text-2xl md:text-3xl text-white font-light tracking-wide">
                  {featured[0]?.name}
                </h3>
                <span className="font-mono text-xs text-white/80 tracking-[0.2em] mt-2">
                  ${featured[0]?.price}
                </span>
              </div>
            </div>
          </Link>
        </ScrollReveal>

        {/* Two small product cards — 3 cols each */}
        {newArrivals.slice(0, 2).map((product, i) => (
          <ScrollReveal key={product.id} className="col-span-2 md:col-span-3" delay={0.1 * (i + 1)}>
            <Link href={`/product/${product.id}`} className="group block">
              <div className="relative overflow-hidden aspect-[3/4]">
                <GradientPlaceholder gradient={product.gradient} className="absolute inset-0 transition-transform duration-700 group-hover:scale-105" />
                <div className="relative z-10 p-4 flex flex-col justify-end h-full">
                  <Badge className="self-start mb-2">NEW</Badge>
                  <h4 className="font-display text-sm text-white tracking-wide">{product.name}</h4>
                  <span className="font-mono text-[10px] text-white/80 tracking-[0.2em] mt-1">${product.price}</span>
                </div>
              </div>
            </Link>
          </ScrollReveal>
        ))}

        {/* Medium collection card — 6 cols */}
        <ScrollReveal className="col-span-4 md:col-span-6" delay={0.2}>
          <Link href={`/collections/${collections[0]?.slug}`} className="group block">
            <div className="relative overflow-hidden aspect-[16/9]">
              <GradientPlaceholder gradient={collections[0]?.gradient ?? ['#928E85', '#C2B280']} className="absolute inset-0 transition-transform duration-700 group-hover:scale-105" />
              <div className="relative z-10 p-6 flex flex-col justify-end h-full">
                <span className="font-mono text-[9px] tracking-[0.3em] text-white/60">COLLECTION</span>
                <h3 className="font-display text-3xl md:text-4xl text-white font-light tracking-wide mt-1">
                  {collections[0]?.name}
                </h3>
                <p className="font-mono text-[10px] text-white/70 tracking-[0.15em] mt-2 max-w-sm">
                  {collections[0]?.description}
                </p>
              </div>
            </div>
          </Link>
        </ScrollReveal>

        {/* Text block — 4 cols */}
        <ScrollReveal className="col-span-4 md:col-span-4 flex items-center" delay={0.1}>
          <div className="p-6 md:p-8">
            <span className="font-mono text-[9px] tracking-[0.4em] text-sovereign-chrome">001</span>
            <h3 className="font-display text-2xl md:text-3xl font-light tracking-wide mt-3 leading-tight">
              Designed for the age of less.
            </h3>
            <p className="font-mono text-[10px] text-sovereign-graphite tracking-[0.15em] mt-4 leading-relaxed">
              Every piece is a study in restraint. Neutral tones. Clean lines. Zero compromise on quality.
            </p>
          </div>
        </ScrollReveal>

        {/* Wide featured product — 8 cols */}
        <ScrollReveal className="col-span-4 md:col-span-8" delay={0.15}>
          <Link href={`/product/${featured[1]?.id}`} className="group block">
            <div className="relative overflow-hidden aspect-[2/1] min-h-[200px]">
              <GradientPlaceholder gradient={featured[1]?.gradient ?? ['#36454F', '#928E85']} className="absolute inset-0 transition-transform duration-700 group-hover:scale-105" />
              <div className="relative z-10 p-6 md:p-8 flex flex-col justify-end h-full">
                <h3 className="font-display text-2xl md:text-4xl text-white font-light tracking-wide">
                  {featured[1]?.name}
                </h3>
                <span className="font-mono text-xs text-white/80 tracking-[0.2em] mt-2">
                  ${featured[1]?.price}
                </span>
              </div>
            </div>
          </Link>
        </ScrollReveal>

        {/* Two collection cards — 6 cols each */}
        {collections.slice(1, 3).map((collection, i) => (
          <ScrollReveal key={collection.slug} className="col-span-4 md:col-span-6" delay={0.1 * (i + 1)}>
            <Link href={`/collections/${collection.slug}`} className="group block">
              <div className="relative overflow-hidden aspect-[4/3]">
                <GradientPlaceholder gradient={collection.gradient} className="absolute inset-0 transition-transform duration-700 group-hover:scale-105" />
                <div className="relative z-10 p-6 flex flex-col justify-end h-full">
                  <span className="font-mono text-[9px] tracking-[0.3em] text-white/60">COLLECTION</span>
                  <h3 className="font-display text-2xl md:text-3xl text-white font-light tracking-wide mt-1">
                    {collection.name}
                  </h3>
                </div>
              </div>
            </Link>
          </ScrollReveal>
        ))}
      </div>
    </section>
  );
}
