import { collections } from '@/lib/collections';
import CollectionGrid from '@/components/collections/CollectionGrid';
import ScrollReveal from '@/components/ui/ScrollReveal';
import Divider from '@/components/ui/Divider';
import SceneLoader from '@/components/three/SceneLoader';

export const metadata = {
  title: 'Collections — SOVEREIGN',
};

export default function CollectionsPage() {
  return (
    <div className="pt-32 pb-20 md:pb-32 relative overflow-hidden">
      {/* Large background chrome shapes */}
      <div className="absolute -top-10 -right-24 w-[450px] h-[550px] opacity-12 pointer-events-none">
        <SceneLoader variant="knot" />
      </div>
      <div className="absolute bottom-20 -left-20 w-[350px] h-[400px] opacity-8 pointer-events-none hidden md:block">
        <SceneLoader variant="pyramid" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 md:px-16">
        <ScrollReveal>
          <span className="font-mono text-[10px] tracking-[0.5em] text-sovereign-chrome">
            ALL COLLECTIONS
          </span>
          <h1 className="font-display text-5xl md:text-7xl font-light tracking-tight mt-6 leading-[0.95]">
            COLLECTIONS
          </h1>
          <p className="font-mono text-[11px] text-sovereign-graphite tracking-[0.15em] mt-6 max-w-lg leading-[2]">
            CURATED CATEGORIES OF PRECISION-ENGINEERED ESSENTIALS.
            EACH COLLECTION SERVES A PURPOSE.
          </p>
        </ScrollReveal>

        <Divider className="my-14 md:my-16" />

        <CollectionGrid collections={collections} />
      </div>
    </div>
  );
}
