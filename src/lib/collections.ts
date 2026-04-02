import { Collection, ChromeShape } from '@/types';

export const collections: Collection[] = [
  {
    slug: 'essentials',
    name: 'ESSENTIALS',
    description: 'The foundation. Tees, tanks, and basics engineered for daily wear.',
    gradient: ['#928E85', '#C2B280'],
  },
  {
    slug: 'tshirts',
    name: 'T-SHIRTS',
    description: 'Heavyweight cotton. Dropped shoulders. The only tees you need.',
    gradient: ['#C2B280', '#928E85'],
  },
  {
    slug: 'hoodies',
    name: 'HOODIES',
    description: 'Brushed fleece. Oversized fits. Warmth without compromise.',
    gradient: ['#36454F', '#6E7B8B'],
  },
  {
    slug: 'pants',
    name: 'PANTS',
    description: 'Utility trousers to tailored joggers. Every leg accounted for.',
    gradient: ['#708238', '#C2B280'],
  },
  {
    slug: 'shorts',
    name: 'SHORTS',
    description: 'Relaxed fits. Clean lines. Built for movement.',
    gradient: ['#FFFDD0', '#C2B280'],
  },
  {
    slug: 'outerwear',
    name: 'OUTERWEAR',
    description: 'Structured silhouettes for layering. Minimal, functional, decisive.',
    gradient: ['#36454F', '#928E85'],
  },
  {
    slug: 'accessories',
    name: 'ACCESSORIES',
    description: 'The finishing details. Caps, bags, and socks built to last.',
    gradient: ['#6E7B8B', '#928E85'],
  },
  {
    slug: 'outdoors',
    name: 'OUTDOORS',
    description: 'Engineered for elements. Technical fabrics. Quiet performance.',
    gradient: ['#708238', '#8A9A5B'],
  },
  {
    slug: 'tools',
    name: 'TOOLS',
    description: 'Utility meets design. Bags, belts, and everyday carry.',
    gradient: ['#36454F', '#1A1A1A'],
  },
];

export const COLLECTION_CHROME_SHAPES: Record<string, ChromeShape> = {
  essentials: 'sphere',
  tshirts: 'cube',
  hoodies: 'blob',
  pants: 'pyramid',
  shorts: 'coin',
  outerwear: 'knot',
  accessories: 'starOfDavid',
  outdoors: 'icosahedron',
  tools: 'menorah',
};

export function getCollection(slug: string): Collection | undefined {
  return collections.find((c) => c.slug === slug);
}
