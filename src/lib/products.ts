import { Product } from '@/types';

export const products: Product[] = [
  {
    id: 'essential-tee-01',
    name: 'Essential Tee',
    slug: 'essential-tee',
    collection: 'essentials',
    price: 35,
    colors: ['sand', 'charcoal', 'cream', 'stone'],
    sizes: ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
    description: 'Heavyweight 240gsm cotton. Dropped shoulder. Boxy fit. The only tee you need.',
    gradient: ['#C2B280', '#928E85'],
    tags: ['new'],
  },
  {
    id: 'oversized-hoodie-01',
    name: 'Oversized Hoodie',
    slug: 'oversized-hoodie',
    collection: 'tops',
    price: 89,
    colors: ['charcoal', 'cream', 'moss', 'clay'],
    sizes: ['S', 'M', 'L', 'XL'],
    description: '380gsm brushed fleece. Double-layered hood. Kangaroo pocket. Ribbed cuffs.',
    gradient: ['#36454F', '#928E85'],
    tags: ['featured'],
  },
  {
    id: 'utility-trouser-01',
    name: 'Utility Trouser',
    slug: 'utility-trouser',
    collection: 'bottoms',
    price: 75,
    colors: ['olive', 'charcoal', 'stone', 'sand'],
    sizes: ['S', 'M', 'L', 'XL', 'XXL'],
    description: 'Ripstop cotton blend. Articulated knees. Six-pocket utility design.',
    gradient: ['#708238', '#C2B280'],
    tags: ['new'],
  },
  {
    id: 'mock-neck-01',
    name: 'Mock Neck Long Sleeve',
    slug: 'mock-neck',
    collection: 'tops',
    price: 55,
    colors: ['cream', 'charcoal', 'slate', 'sand'],
    sizes: ['XS', 'S', 'M', 'L', 'XL'],
    description: 'Ribbed cotton jersey. Slim fit. Mock turtle neck. Understated layering piece.',
    gradient: ['#FFFDD0', '#6E7B8B'],
    tags: [],
  },
  {
    id: 'field-jacket-01',
    name: 'Field Jacket',
    slug: 'field-jacket',
    collection: 'outerwear',
    price: 145,
    colors: ['olive', 'charcoal', 'stone'],
    sizes: ['S', 'M', 'L', 'XL'],
    description: 'Water-resistant nylon shell. Concealed hood. Clean front with hidden snap closure.',
    gradient: ['#708238', '#36454F'],
    tags: ['featured'],
  },
  {
    id: 'relaxed-short-01',
    name: 'Relaxed Short',
    slug: 'relaxed-short',
    collection: 'bottoms',
    price: 55,
    colors: ['sand', 'olive', 'slate', 'cream'],
    sizes: ['S', 'M', 'L', 'XL'],
    description: '7-inch inseam. Elastic waist with internal drawcord. Side seam pockets.',
    gradient: ['#C2B280', '#FFFDD0'],
    tags: [],
  },
  {
    id: 'puffer-vest-01',
    name: 'Puffer Vest',
    slug: 'puffer-vest',
    collection: 'outerwear',
    price: 120,
    colors: ['charcoal', 'stone', 'moss'],
    sizes: ['S', 'M', 'L', 'XL'],
    description: 'Recycled down fill. Stand collar. Two-way zip. Weightless warmth.',
    gradient: ['#36454F', '#8A9A5B'],
    tags: ['new'],
  },
  {
    id: 'heavyweight-crew-01',
    name: 'Heavyweight Crew',
    slug: 'heavyweight-crew',
    collection: 'tops',
    price: 75,
    colors: ['cream', 'clay', 'charcoal', 'moss'],
    sizes: ['S', 'M', 'L', 'XL', 'XXL'],
    description: '400gsm French terry. Raglan sleeves. Minimal branding. Built to fade beautifully.',
    gradient: ['#B66A50', '#928E85'],
    tags: ['featured'],
  },
  {
    id: 'essential-tank-01',
    name: 'Essential Tank',
    slug: 'essential-tank',
    collection: 'essentials',
    price: 28,
    colors: ['cream', 'sand', 'charcoal', 'stone'],
    sizes: ['XS', 'S', 'M', 'L', 'XL'],
    description: 'Lightweight 180gsm cotton. Relaxed armhole. Extended length.',
    gradient: ['#FFFDD0', '#C2B280'],
    tags: [],
  },
  {
    id: 'tech-jogger-01',
    name: 'Tech Jogger',
    slug: 'tech-jogger',
    collection: 'bottoms',
    price: 85,
    colors: ['charcoal', 'slate', 'olive', 'stone'],
    sizes: ['S', 'M', 'L', 'XL'],
    description: 'Four-way stretch woven fabric. Tapered leg. Zip pockets. Travel-ready.',
    gradient: ['#6E7B8B', '#36454F'],
    tags: ['new'],
  },
  {
    id: 'canvas-cap-01',
    name: 'Canvas Cap',
    slug: 'canvas-cap',
    collection: 'accessories',
    price: 32,
    colors: ['sand', 'charcoal', 'olive', 'stone'],
    sizes: ['S', 'L'],
    description: 'Washed canvas. Unstructured crown. Leather strap closure. No logos.',
    gradient: ['#928E85', '#C2B280'],
    tags: [],
  },
  {
    id: 'wool-overcoat-01',
    name: 'Wool Overcoat',
    slug: 'wool-overcoat',
    collection: 'outerwear',
    price: 195,
    colors: ['charcoal', 'stone', 'cream'],
    sizes: ['S', 'M', 'L', 'XL'],
    description: 'Italian wool blend. Single-breasted. Below-knee length. Timeless construction.',
    gradient: ['#36454F', '#FFFDD0'],
    tags: ['featured'],
  },
];

export function getProduct(id: string): Product | undefined {
  return products.find((p) => p.id === id);
}

export function getProductsByCollection(collectionSlug: string): Product[] {
  return products.filter((p) => p.collection === collectionSlug);
}

export function getFeaturedProducts(): Product[] {
  return products.filter((p) => p.tags.includes('featured'));
}

export function getNewProducts(): Product[] {
  return products.filter((p) => p.tags.includes('new'));
}
