import { collections } from '@/lib/collections';
import CollectionGrid from '@/components/collections/CollectionGrid';
import ScrollReveal from '@/components/ui/ScrollReveal';
import Divider from '@/components/ui/Divider';

export const metadata = {
  title: 'Collections — SOVEREIGN',
};

export default function CollectionsPage() {
  return (
    <div className="pt-32 pb-20 md:pb-32">
      <div className="max-w-7xl mx-auto px-6 md:px-16">
        <ScrollReveal>
          <span className="font-mono text-[10px] tracking-[0.5em] text-sovereign-chrome">
            ALL COLLECTIONS
          </span>
          <h1 className="font-display text-5xl md:text-7xl font-light tracking-tight mt-4">
            COLLECTIONS
          </h1>
          <p className="font-mono text-[11px] text-sovereign-graphite tracking-[0.15em] mt-4 max-w-md leading-relaxed">
            CURATED CATEGORIES OF PRECISION-ENGINEERED ESSENTIALS.
            EACH COLLECTION SERVES A PURPOSE.
          </p>
        </ScrollReveal>

        <Divider className="my-12" />

        <CollectionGrid collections={collections} />
      </div>
    </div>
  );
}
