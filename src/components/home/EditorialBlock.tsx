'use client';

import ScrollReveal from '@/components/ui/ScrollReveal';
import SceneLoader from '@/components/three/SceneLoader';

export default function EditorialBlock() {
  return (
    <section className="w-full bg-sovereign-carbon text-sovereign-white py-24 md:py-40 relative overflow-hidden">
      {/* 3D accent in background */}
      <div className="absolute top-0 right-0 w-1/2 h-full opacity-30 pointer-events-none">
        <SceneLoader variant="accent" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 md:px-16">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-16">
          <ScrollReveal>
            <span className="font-mono text-[10px] tracking-[0.5em] text-sovereign-graphite block mb-6">
              PHILOSOPHY
            </span>
            <h2 className="font-display text-4xl md:text-5xl lg:text-6xl font-light tracking-wide leading-tight">
              Less is the
              <br />
              new luxury.
            </h2>
          </ScrollReveal>

          <ScrollReveal delay={0.2} className="flex items-end">
            <div>
              <p className="font-mono text-[11px] tracking-[0.15em] text-sovereign-graphite leading-relaxed">
                IN AN ERA OF OVERCONSUMPTION, WE CHOOSE RESTRAINT. SOVEREIGN IS BUILT ON THE BELIEF THAT
                GREAT DESIGN DOESN&apos;T SHOUT — IT WHISPERS. EVERY GARMENT IS CONSIDERED. EVERY DETAIL PURPOSEFUL.
                EVERY PRICE ACCESSIBLE.
              </p>
              <div className="flex items-center gap-4 mt-8">
                <div className="w-12 h-px bg-sovereign-graphite" />
                <span className="font-mono text-[9px] tracking-[0.4em] text-sovereign-graphite">
                  $28 — $195
                </span>
              </div>
            </div>
          </ScrollReveal>
        </div>
      </div>
    </section>
  );
}
