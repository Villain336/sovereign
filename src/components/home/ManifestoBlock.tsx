'use client';

import AnimatedText from '@/components/ui/AnimatedText';
import ScrollReveal from '@/components/ui/ScrollReveal';
import Divider from '@/components/ui/Divider';
import { BRAND } from '@/lib/constants';

export default function ManifestoBlock() {
  return (
    <section className="w-full bg-sovereign-snow">
      <Divider />
      <div className="max-w-5xl mx-auto px-6 md:px-16 py-24 md:py-40">
        <ScrollReveal>
          <span className="font-mono text-[10px] tracking-[0.5em] text-sovereign-chrome block mb-10">
            MANIFESTO
          </span>
        </ScrollReveal>

        <AnimatedText
          text={BRAND.manifesto}
          as="p"
          className="font-display text-xl md:text-3xl lg:text-4xl font-light leading-relaxed tracking-wide text-sovereign-carbon"
        />

        <ScrollReveal delay={0.5}>
          <div className="mt-16 flex items-center gap-4">
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
