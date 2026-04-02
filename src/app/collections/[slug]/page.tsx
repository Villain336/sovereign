import { notFound } from 'next/navigation';
import { collections, getCollection } from '@/lib/collections';
import { getProductsByCollection } from '@/lib/products';
import ProductCard from '@/components/product/ProductCard';
import ScrollReveal from '@/components/ui/ScrollReveal';
import Divider from '@/components/ui/Divider';

export function generateStaticParams() {
  return collections.map((c) => ({ slug: c.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const collection = getCollection(slug);
  return { title: collection ? `${collection.name} — SOVEREIGN` : 'Collection — SOVEREIGN' };
}

export default async function CollectionPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const collection = getCollection(slug);
  if (!collection) notFound();

  const products = getProductsByCollection(slug);

  return (
    <div className="pt-32 pb-20 md:pb-32">
      <div className="max-w-7xl mx-auto px-6 md:px-16">
        <ScrollReveal>
          <span className="font-mono text-[10px] tracking-[0.5em] text-sovereign-chrome">
            COLLECTION
          </span>
          <h1 className="font-display text-5xl md:text-7xl font-light tracking-tight mt-4">
            {collection.name}
          </h1>
          <p className="font-mono text-[11px] text-sovereign-graphite tracking-[0.15em] mt-4 max-w-md leading-relaxed">
            {collection.description.toUpperCase()}
          </p>
        </ScrollReveal>

        <Divider className="my-12" />

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">
          {products.map((product, i) => (
            <ScrollReveal key={product.id} delay={i * 0.08}>
              <ProductCard product={product} />
            </ScrollReveal>
          ))}
        </div>

        {products.length === 0 && (
          <p className="font-mono text-xs text-sovereign-graphite tracking-[0.2em] text-center py-20">
            COMING SOON
          </p>
        )}
      </div>
    </div>
  );
}
