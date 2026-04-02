'use client';

import AnimatedText from '@/components/ui/AnimatedText';
import ScrollReveal from '@/components/ui/ScrollReveal';
import Divider from '@/components/ui/Divider';
import SceneLoader from '@/components/three/SceneLoader';
import { BRAND } from '@/lib/constants';

export default function ManifestoBlock() {
  return (
    <section className="w-full bg-sovereign-snow relative overflow-hidden">
      <Divider />

      {/* Background chrome shapes */}
      <div className="absolute -right-16 top-1/2 -translate-y-1/2 w-[400px] h-[500px] opacity-10 pointer-events-none">
        <SceneLoader variant="star" />
      </div>

      <div className="relative z-10 max-w-5xl mx-auto px-6 md:px-16 py-28 md:py-48">
        <ScrollReveal>
          <span className="font-mono text-[10px] tracking-[0.5em] text-sovereign-chrome block mb-12">
            MANIFESTO
          </span>
        </ScrollReveal>

        <AnimatedText
          text={BRAND.manifesto}
          as="p"
          className="font-display text-xl md:text-3xl lg:text-4xl font-light leading-[1.6] md:leading-[1.7] tracking-wide text-sovereign-carbon"
        />

        <ScrollReveal delay={0.5}>
          <div className="mt-20 flex items-center gap-4">
            <div className="w-8 h-px bg-sovereign-chrome" />
            <span className="font-mono text-[10px] tracking-[0.4em] text-sovereign-graphite">
              EST. 2026
            </span>
          </div>
        </ScrollReveal>
      </div>
      <Divider />
    </section>
  );
}
