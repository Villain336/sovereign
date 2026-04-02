import { notFound } from 'next/navigation';
import { collections, getCollection, COLLECTION_CHROME_SHAPES } from '@/lib/collections';
import { getProductsByCollection } from '@/lib/products';
import ProductCard from '@/components/product/ProductCard';
import ScrollReveal from '@/components/ui/ScrollReveal';
import Divider from '@/components/ui/Divider';
import Breadcrumbs from '@/components/ui/Breadcrumbs';
import SceneLoader from '@/components/three/SceneLoader';

export function generateStaticParams() {
  return collections.map((c) => ({ slug: c.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const collection = getCollection(slug);
  return { title: collection ? `${collection.name} — SOVEREIGN` : 'Collection — SOVEREIGN' };
}

type SceneVariant = 'hero' | 'accent' | 'minimal' | 'knot' | 'icosahedron' | 'pyramid' | 'cube' | 'coin' | 'star' | 'menorah' | 'human' | 'ring';
const SHAPE_VARIANT_MAP: Record<string, SceneVariant> = {
  sphere: 'minimal',
  torus: 'accent',
  blob: 'accent',
  knot: 'knot',
  icosahedron: 'icosahedron',
  pyramid: 'pyramid',
  cube: 'cube',
  coin: 'coin',
  starOfDavid: 'star',
  menorah: 'menorah',
  human: 'human',
  ring: 'ring',
};

export default async function CollectionPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const collection = getCollection(slug);
  if (!collection) notFound();

  const products = getProductsByCollection(slug);
  const chromeShape = COLLECTION_CHROME_SHAPES[slug] || 'sphere';
  const sceneVariant = SHAPE_VARIANT_MAP[chromeShape] || 'minimal';

  return (
    <div className="pt-32 pb-20 md:pb-32 relative overflow-hidden">
      {/* Large chrome shape accent — background right */}
      <div className="absolute -top-10 -right-20 w-[400px] h-[500px] md:w-[500px] md:h-[600px] opacity-15 pointer-events-none">
        <SceneLoader variant={sceneVariant} />
      </div>

      {/* Secondary accent — bottom left */}
      <div className="absolute bottom-40 -left-16 w-[250px] h-[300px] opacity-8 pointer-events-none hidden md:block">
        <SceneLoader variant="minimal" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 md:px-16">
        <Breadcrumbs items={[
          { label: 'COLLECTIONS', href: '/collections' },
          { label: collection.name },
        ]} />

        <ScrollReveal>
          <span className="font-mono text-[10px] tracking-[0.5em] text-sovereign-chrome">
            COLLECTION
          </span>
          <h1 className="font-display text-5xl md:text-7xl font-light tracking-tight mt-6 leading-[0.95]">
            {collection.name}
          </h1>
          <p className="font-mono text-[11px] text-sovereign-graphite tracking-[0.15em] mt-6 max-w-lg leading-[2]">
            {collection.description.toUpperCase()}
          </p>
        </ScrollReveal>

        <Divider className="my-14 md:my-16" />

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5 md:gap-8">
          {products.map((product, i) => (
            <ScrollReveal key={product.id} delay={i * 0.08}>
              <ProductCard product={product} />
            </ScrollReveal>
          ))}
        </div>

        {products.length === 0 && (
          <p className="font-mono text-xs text-sovereign-graphite tracking-[0.2em] text-center py-24">
            COMING SOON
          </p>
        )}
      </div>
    </div>
  );
}
