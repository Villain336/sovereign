'use client';

import ScrollReveal from '@/components/ui/ScrollReveal';
import CollectionCard from './CollectionCard';
import { Collection } from '@/types';

export default function CollectionGrid({ collections }: { collections: Collection[] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
      {collections.map((collection, i) => (
        <ScrollReveal key={collection.slug} delay={i * 0.1}>
          <CollectionCard collection={collection} />
        </ScrollReveal>
      ))}
    </div>
  );
}
