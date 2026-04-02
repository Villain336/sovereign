import { notFound } from 'next/navigation';
import { products, getProduct, getProductsByCollection } from '@/lib/products';
import { getCollection } from '@/lib/collections';
import ProductGallery from '@/components/product/ProductGallery';
import ProductInfo from '@/components/product/ProductInfo';
import ProductCard from '@/components/product/ProductCard';
import ScrollReveal from '@/components/ui/ScrollReveal';
import Divider from '@/components/ui/Divider';
import Breadcrumbs from '@/components/ui/Breadcrumbs';
import SceneLoader from '@/components/three/SceneLoader';

export function generateStaticParams() {
  return products.map((p) => ({ id: p.id }));
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const product = getProduct(id);
  return { title: product ? `${product.name} — SOVEREIGN` : 'Product — SOVEREIGN' };
}

export default async function ProductPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const product = getProduct(id);
  if (!product) notFound();

  const collection = getCollection(product.collection);
  const related = getProductsByCollection(product.collection)
    .filter((p) => p.id !== product.id)
    .slice(0, 4);

  return (
    <div className="pt-28 pb-20 md:pb-32 relative">
      {/* Chrome accent */}
      <div className="absolute top-20 right-0 w-40 h-40 opacity-15 pointer-events-none hidden lg:block">
        <SceneLoader variant="minimal" />
      </div>

      <div className="max-w-7xl mx-auto px-6 md:px-16">
        <Breadcrumbs items={[
          { label: 'COLLECTIONS', href: '/collections' },
          ...(collection ? [{ label: collection.name, href: `/collections/${collection.slug}` }] : []),
          { label: product.name.toUpperCase() },
        ]} />

        {/* Main product layout */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-16">
          <ScrollReveal direction="left">
            <ProductGallery gradient={product.gradient} name={product.name} />
          </ScrollReveal>

          <ScrollReveal direction="right">
            <div className="md:sticky md:top-28">
              <ProductInfo product={product} />
            </div>
          </ScrollReveal>
        </div>

        {/* Related products */}
        {related.length > 0 && (
          <div className="mt-24 md:mt-40">
            <Divider className="mb-12" />
            <ScrollReveal>
              <span className="font-mono text-[10px] tracking-[0.5em] text-sovereign-graphite block mb-8">
                YOU MAY ALSO LIKE
              </span>
            </ScrollReveal>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
              {related.map((p, i) => (
                <ScrollReveal key={p.id} delay={i * 0.08}>
                  <ProductCard product={p} />
                </ScrollReveal>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
