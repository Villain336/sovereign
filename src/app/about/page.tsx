import AnimatedText from '@/components/ui/AnimatedText';
import ScrollReveal from '@/components/ui/ScrollReveal';
import Divider from '@/components/ui/Divider';
import SceneLoader from '@/components/three/SceneLoader';
import { BRAND } from '@/lib/constants';

export const metadata = {
  title: 'About — SOVEREIGN',
};

export default function AboutPage() {
  return (
    <div className="pt-32 pb-20 md:pb-32">
      {/* Hero section */}
      <div className="max-w-7xl mx-auto px-6 md:px-16">
        <ScrollReveal>
          <span className="font-mono text-[10px] tracking-[0.5em] text-sovereign-chrome">
            ABOUT
          </span>
        </ScrollReveal>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-12 md:gap-16">
          <div>
            <AnimatedText
              text="We exist to simplify your wardrobe."
              as="h1"
              className="font-display text-4xl md:text-5xl lg:text-6xl font-light tracking-wide leading-tight"
            />
          </div>

          <ScrollReveal delay={0.3} className="flex items-end">
            <p className="font-mono text-[11px] text-sovereign-graphite tracking-[0.15em] leading-relaxed">
              SOVEREIGN WAS FOUNDED ON A SIMPLE PREMISE: THE BEST CLOTHING GETS OUT OF YOUR WAY.
              WE STRIP AWAY THE UNNECESSARY — THE LOGOS, THE TRENDS, THE INFLATED PRICES — AND FOCUS ON WHAT MATTERS:
              FIT, FABRIC, AND FUNCTION.
            </p>
          </ScrollReveal>
        </div>
      </div>

      <Divider className="my-16 md:my-24" />

      {/* 3D + Values section */}
      <div className="max-w-7xl mx-auto px-6 md:px-16">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          {/* 3D Scene */}
          <ScrollReveal>
            <div className="aspect-square max-w-lg mx-auto">
              <SceneLoader variant="accent" />
            </div>
          </ScrollReveal>

          {/* Values */}
          <ScrollReveal delay={0.2}>
            <div className="flex flex-col gap-10">
              {[
                {
                  number: '01',
                  title: 'NO LOGOS',
                  desc: 'Your clothes should speak through quality, not branding. Every Sovereign piece is identifiable by its construction, not its label.',
                },
                {
                  number: '02',
                  title: 'ACCESSIBLE PRICING',
                  desc: 'Premium materials and construction at honest prices. We cut out the middlemen, not the corners. $28 to $195.',
                },
                {
                  number: '03',
                  title: 'NEUTRAL PALETTE',
                  desc: 'Earth tones that work together seamlessly. Build a wardrobe where everything pairs naturally.',
                },
                {
                  number: '04',
                  title: 'ENGINEERED FIT',
                  desc: 'Each silhouette is studied and refined. Relaxed where it should be, structured where it counts.',
                },
              ].map((value) => (
                <div key={value.number}>
                  <div className="flex items-center gap-3 mb-2">
                    <span className="font-mono text-[9px] tracking-[0.4em] text-sovereign-chrome">
                      {value.number}
                    </span>
                    <div className="w-4 h-px bg-sovereign-chrome" />
                    <span className="font-mono text-xs tracking-[0.3em]">{value.title}</span>
                  </div>
                  <p className="font-mono text-[10px] text-sovereign-graphite tracking-[0.15em] leading-relaxed ml-14">
                    {value.desc.toUpperCase()}
                  </p>
                </div>
              ))}
            </div>
          </ScrollReveal>
        </div>
      </div>

      <Divider className="my-16 md:my-24" />

      {/* Manifesto */}
      <div className="max-w-4xl mx-auto px-6 md:px-16">
        <ScrollReveal>
          <span className="font-mono text-[10px] tracking-[0.5em] text-sovereign-chrome block mb-8">
            MANIFESTO
          </span>
        </ScrollReveal>

        <AnimatedText
          text={BRAND.manifesto}
          as="p"
          className="font-display text-xl md:text-2xl lg:text-3xl font-light leading-relaxed tracking-wide"
        />

        <ScrollReveal delay={0.5}>
          <div className="mt-16 flex items-center gap-4">
            <div className="w-8 h-px bg-sovereign-chrome" />
            <span className="font-mono text-[10px] tracking-[0.4em] text-sovereign-graphite">
              SOVEREIGN — EST. 2026
            </span>
          </div>
        </ScrollReveal>
      </div>
    </div>
  );
}
