import { Collection } from '@/types';

export const collections: Collection[] = [
  {
    slug: 'essentials',
    name: 'ESSENTIALS',
    description: 'The foundation. Tees, tanks, and basics engineered for daily wear.',
    gradient: ['#928E85', '#C2B280'],
  },
  {
    slug: 'outerwear',
    name: 'OUTERWEAR',
    description: 'Structured silhouettes for layering. Minimal, functional, decisive.',
    gradient: ['#36454F', '#6E7B8B'],
  },
  {
    slug: 'bottoms',
    name: 'BOTTOMS',
    description: 'Relaxed and tailored fits. From utility trousers to sculpted joggers.',
    gradient: ['#708238', '#8A9A5B'],
  },
  {
    slug: 'tops',
    name: 'TOPS',
    description: 'Elevated staples. Oversized crews, mock necks, and half-zips.',
    gradient: ['#B66A50', '#C2B280'],
  },
  {
    slug: 'accessories',
    name: 'ACCESSORIES',
    description: 'The finishing details. Caps, bags, and socks built to last.',
    gradient: ['#6E7B8B', '#928E85'],
  },
];

export function getCollection(slug: string): Collection | undefined {
  return collections.find((c) => c.slug === slug);
}
