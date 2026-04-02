import { drops } from '@/lib/drops';
import { getProduct } from '@/lib/products';
import CountdownTimer from '@/components/drops/CountdownTimer';
import ProductCard from '@/components/product/ProductCard';
import ScrollReveal from '@/components/ui/ScrollReveal';
import Divider from '@/components/ui/Divider';
import GradientPlaceholder from '@/components/ui/GradientPlaceholder';
import SceneLoader from '@/components/three/SceneLoader';
import Button from '@/components/ui/Button';
import Link from 'next/link';

export const metadata = { title: 'Drops — SOVEREIGN' };

export default function DropsPage() {
  return (
    <div className="pt-28 pb-20 md:pb-32">
      {/* Hero */}
      <div className="relative max-w-7xl mx-auto px-6 md:px-16 mb-20">
        <div className="absolute top-0 right-0 w-64 h-64 opacity-30 pointer-events-none">
          <SceneLoader variant="accent" />
        </div>
        <ScrollReveal>
          <span className="font-mono text-[10px] tracking-[0.5em] text-sovereign-chrome">THE DROP</span>
          <h1 className="font-display text-6xl md:text-8xl font-light tracking-tight mt-4">
            DROPS
          </h1>
          <p className="font-mono text-[11px] text-sovereign-graphite tracking-[0.15em] mt-4 max-w-lg leading-relaxed">
            LIMITED RELEASES. CURATED COLLECTIONS. WHEN THEY DROP, THEY DROP.
          </p>
        </ScrollReveal>
      </div>

      {/* Drops list */}
      {drops.map((drop, i) => {
        const dropProducts = drop.products.map(getProduct).filter(Boolean);
        return (
          <div key={drop.id}>
            <Divider />
            <section className="max-w-7xl mx-auto px-6 md:px-16 py-16 md:py-24">
              <ScrollReveal>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
                  <div>
                    <div className="relative overflow-hidden aspect-[16/9] mb-6">
                      <GradientPlaceholder gradient={drop.gradient} className="absolute inset-0" />
                      <div className="relative z-10 p-6 flex flex-col justify-end h-full">
                        <span className="font-mono text-[9px] tracking-[0.3em] text-white/50">
                          {drop.isLive ? 'LIVE NOW' : 'UPCOMING'}
                        </span>
                        <h2 className="font-display text-3xl md:text-4xl text-white font-light tracking-wide mt-1">
                          {drop.name}
                        </h2>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-col justify-center">
                    <p className="font-mono text-[11px] text-sovereign-graphite tracking-[0.15em] leading-relaxed mb-6">
                      {drop.description.toUpperCase()}
                    </p>
                    {!drop.isLive && (
                      <>
                        <span className="font-mono text-[9px] tracking-[0.3em] text-sovereign-chrome mb-3">DROPS IN</span>
                        <CountdownTimer targetDate={drop.date} />
                        <div className="mt-6">
                          <Button variant="outline" size="md">NOTIFY ME</Button>
                        </div>
                      </>
                    )}
                    {drop.isLive && (
                      <Link href="/collections">
                        <Button variant="filled" size="lg">SHOP NOW</Button>
                      </Link>
                    )}
                  </div>
                </div>
              </ScrollReveal>

              {/* Products in this drop */}
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">
                {dropProducts.map((product, j) => product && (
                  <ScrollReveal key={product.id} delay={j * 0.08}>
                    <ProductCard product={product} />
                  </ScrollReveal>
                ))}
              </div>
            </section>
          </div>
        );
      })}
    </div>
  );
}
