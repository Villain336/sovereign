import { Product } from '@/types';

export const products: Product[] = [
  // ESSENTIALS
  { id: 'essential-tee-01', name: 'Essential Tee', slug: 'essential-tee', collection: 'essentials', price: 35, colors: ['sand', 'charcoal', 'cream', 'stone'], sizes: ['XS', 'S', 'M', 'L', 'XL', 'XXL'], description: 'Heavyweight 240gsm cotton. Dropped shoulder. Boxy fit. The only tee you need.', gradient: ['#C2B280', '#928E85'], tags: ['new'] },
  { id: 'essential-tank-01', name: 'Essential Tank', slug: 'essential-tank', collection: 'essentials', price: 28, colors: ['cream', 'sand', 'charcoal', 'stone'], sizes: ['XS', 'S', 'M', 'L', 'XL'], description: 'Lightweight 180gsm cotton. Relaxed armhole. Extended length.', gradient: ['#FFFDD0', '#C2B280'], tags: [] },
  { id: 'essential-long-01', name: 'Essential Long Sleeve', slug: 'essential-long', collection: 'essentials', price: 42, colors: ['stone', 'charcoal', 'cream'], sizes: ['S', 'M', 'L', 'XL'], description: 'Mid-weight jersey. Relaxed fit. Ribbed cuffs. Layering staple.', gradient: ['#928E85', '#C2B280'], tags: [] },

  // T-SHIRTS
  { id: 'boxy-tee-01', name: 'Boxy Crop Tee', slug: 'boxy-tee', collection: 'tshirts', price: 38, colors: ['cream', 'sand', 'slate'], sizes: ['XS', 'S', 'M', 'L', 'XL'], description: 'Cropped boxy silhouette. Raw hem. 260gsm cotton.', gradient: ['#FFFDD0', '#6E7B8B'], tags: ['new'] },
  { id: 'oversized-tee-01', name: 'Oversized Pocket Tee', slug: 'oversized-tee', collection: 'tshirts', price: 40, colors: ['charcoal', 'olive', 'cream', 'stone'], sizes: ['S', 'M', 'L', 'XL', 'XXL'], description: 'Oversized fit. Single chest pocket. Reinforced seams.', gradient: ['#36454F', '#C2B280'], tags: ['featured'] },
  { id: 'raglan-tee-01', name: 'Raglan Tee', slug: 'raglan-tee', collection: 'tshirts', price: 36, colors: ['sand', 'charcoal', 'moss'], sizes: ['S', 'M', 'L', 'XL'], description: 'Raglan sleeves for range of motion. Slightly tapered body.', gradient: ['#C2B280', '#8A9A5B'], tags: [] },

  // HOODIES
  { id: 'oversized-hoodie-01', name: 'Oversized Hoodie', slug: 'oversized-hoodie', collection: 'hoodies', price: 89, colors: ['charcoal', 'cream', 'moss', 'clay'], sizes: ['S', 'M', 'L', 'XL'], description: '380gsm brushed fleece. Double-layered hood. Kangaroo pocket. Ribbed cuffs.', gradient: ['#36454F', '#928E85'], tags: ['featured'] },
  { id: 'zip-hoodie-01', name: 'Half-Zip Hoodie', slug: 'zip-hoodie', collection: 'hoodies', price: 95, colors: ['stone', 'charcoal', 'olive'], sizes: ['S', 'M', 'L', 'XL'], description: 'Half-zip closure. Stand collar option. 360gsm French terry.', gradient: ['#928E85', '#708238'], tags: ['new'] },
  { id: 'pullover-01', name: 'Heavyweight Pullover', slug: 'pullover', collection: 'hoodies', price: 85, colors: ['cream', 'charcoal', 'slate'], sizes: ['S', 'M', 'L', 'XL', 'XXL'], description: '400gsm fleece. Mock neck. No drawstrings. Clean and minimal.', gradient: ['#FFFDD0', '#6E7B8B'], tags: [] },

  // PANTS
  { id: 'utility-trouser-01', name: 'Utility Trouser', slug: 'utility-trouser', collection: 'pants', price: 75, colors: ['olive', 'charcoal', 'stone', 'sand'], sizes: ['S', 'M', 'L', 'XL', 'XXL'], description: 'Ripstop cotton blend. Articulated knees. Six-pocket utility design.', gradient: ['#708238', '#C2B280'], tags: ['new'] },
  { id: 'tech-jogger-01', name: 'Tech Jogger', slug: 'tech-jogger', collection: 'pants', price: 85, colors: ['charcoal', 'slate', 'olive', 'stone'], sizes: ['S', 'M', 'L', 'XL'], description: 'Four-way stretch woven fabric. Tapered leg. Zip pockets. Travel-ready.', gradient: ['#6E7B8B', '#36454F'], tags: ['featured'] },
  { id: 'wide-trouser-01', name: 'Wide Leg Trouser', slug: 'wide-trouser', collection: 'pants', price: 80, colors: ['charcoal', 'cream', 'stone'], sizes: ['S', 'M', 'L', 'XL'], description: 'Relaxed wide leg. Pleated front. Cropped ankle length.', gradient: ['#36454F', '#FFFDD0'], tags: [] },

  // SHORTS
  { id: 'relaxed-short-01', name: 'Relaxed Short', slug: 'relaxed-short', collection: 'shorts', price: 55, colors: ['sand', 'olive', 'slate', 'cream'], sizes: ['S', 'M', 'L', 'XL'], description: '7-inch inseam. Elastic waist with internal drawcord. Side seam pockets.', gradient: ['#C2B280', '#FFFDD0'], tags: [] },
  { id: 'tech-short-01', name: 'Tech Short', slug: 'tech-short', collection: 'shorts', price: 60, colors: ['charcoal', 'olive', 'stone'], sizes: ['S', 'M', 'L', 'XL'], description: 'Stretch woven fabric. 6-inch inseam. Zip pocket. Lightweight.', gradient: ['#36454F', '#928E85'], tags: ['new'] },

  // OUTERWEAR
  { id: 'field-jacket-01', name: 'Field Jacket', slug: 'field-jacket', collection: 'outerwear', price: 145, colors: ['olive', 'charcoal', 'stone'], sizes: ['S', 'M', 'L', 'XL'], description: 'Water-resistant nylon shell. Concealed hood. Clean front with hidden snap closure.', gradient: ['#708238', '#36454F'], tags: ['featured'] },
  { id: 'puffer-vest-01', name: 'Puffer Vest', slug: 'puffer-vest', collection: 'outerwear', price: 120, colors: ['charcoal', 'stone', 'moss'], sizes: ['S', 'M', 'L', 'XL'], description: 'Recycled down fill. Stand collar. Two-way zip. Weightless warmth.', gradient: ['#36454F', '#8A9A5B'], tags: ['new'] },
  { id: 'wool-overcoat-01', name: 'Wool Overcoat', slug: 'wool-overcoat', collection: 'outerwear', price: 195, colors: ['charcoal', 'stone', 'cream'], sizes: ['S', 'M', 'L', 'XL'], description: 'Italian wool blend. Single-breasted. Below-knee length. Timeless construction.', gradient: ['#36454F', '#FFFDD0'], tags: ['featured'] },

  // ACCESSORIES
  { id: 'canvas-cap-01', name: 'Canvas Cap', slug: 'canvas-cap', collection: 'accessories', price: 32, colors: ['sand', 'charcoal', 'olive', 'stone'], sizes: ['S', 'L'], description: 'Washed canvas. Unstructured crown. Leather strap closure. No logos.', gradient: ['#928E85', '#C2B280'], tags: [] },
  { id: 'tote-bag-01', name: 'Canvas Tote', slug: 'tote-bag', collection: 'accessories', price: 45, colors: ['sand', 'charcoal', 'olive'], sizes: ['S'], description: 'Heavy canvas. Interior pocket. Reinforced handles. Carries everything.', gradient: ['#C2B280', '#36454F'], tags: ['new'] },
  { id: 'crew-socks-01', name: 'Crew Socks 3-Pack', slug: 'crew-socks', collection: 'accessories', price: 24, colors: ['charcoal', 'cream', 'stone'], sizes: ['S', 'L'], description: 'Combed cotton blend. Ribbed cuff. Cushioned sole. Three pairs.', gradient: ['#36454F', '#928E85'], tags: [] },

  // OUTDOORS
  { id: 'rain-shell-01', name: 'Rain Shell', slug: 'rain-shell', collection: 'outdoors', price: 135, colors: ['olive', 'charcoal', 'slate'], sizes: ['S', 'M', 'L', 'XL'], description: 'Waterproof 3-layer membrane. Sealed seams. Packable into chest pocket.', gradient: ['#708238', '#6E7B8B'], tags: ['featured'] },
  { id: 'hiking-short-01', name: 'Hiking Short', slug: 'hiking-short', collection: 'outdoors', price: 65, colors: ['olive', 'stone', 'charcoal'], sizes: ['S', 'M', 'L', 'XL'], description: 'Durable ripstop. Gusseted crotch. Belt loops. Built for trails.', gradient: ['#8A9A5B', '#928E85'], tags: ['new'] },
  { id: 'fleece-jacket-01', name: 'Fleece Jacket', slug: 'fleece-jacket', collection: 'outdoors', price: 110, colors: ['moss', 'charcoal', 'stone'], sizes: ['S', 'M', 'L', 'XL'], description: 'Polartec 300 weight. Full zip. Chest pocket. Layering essential.', gradient: ['#8A9A5B', '#36454F'], tags: [] },

  // TOOLS
  { id: 'tool-belt-01', name: 'Utility Belt', slug: 'tool-belt', collection: 'tools', price: 48, colors: ['charcoal', 'olive', 'stone'], sizes: ['S', 'L'], description: 'Nylon webbing. Quick-release buckle. Removable tool loops.', gradient: ['#36454F', '#708238'], tags: ['new'] },
  { id: 'crossbody-01', name: 'Crossbody Bag', slug: 'crossbody', collection: 'tools', price: 55, colors: ['charcoal', 'olive', 'sand'], sizes: ['S'], description: 'Ballistic nylon. Multiple compartments. Adjustable strap. Everyday carry.', gradient: ['#1A1A1A', '#36454F'], tags: ['featured'] },
  { id: 'dopp-kit-01', name: 'Dopp Kit', slug: 'dopp-kit', collection: 'tools', price: 38, colors: ['charcoal', 'sand', 'stone'], sizes: ['S'], description: 'Waxed canvas exterior. Water-resistant lining. YKK zip. Travel-ready.', gradient: ['#928E85', '#1A1A1A'], tags: [] },

  // TOPS (additional)
  { id: 'mock-neck-01', name: 'Mock Neck Long Sleeve', slug: 'mock-neck', collection: 'tshirts', price: 55, colors: ['cream', 'charcoal', 'slate', 'sand'], sizes: ['XS', 'S', 'M', 'L', 'XL'], description: 'Ribbed cotton jersey. Slim fit. Mock turtle neck. Understated layering piece.', gradient: ['#FFFDD0', '#6E7B8B'], tags: [] },
  { id: 'heavyweight-crew-01', name: 'Heavyweight Crew', slug: 'heavyweight-crew', collection: 'hoodies', price: 75, colors: ['cream', 'clay', 'charcoal', 'moss'], sizes: ['S', 'M', 'L', 'XL', 'XXL'], description: '400gsm French terry. Raglan sleeves. Minimal branding. Built to fade beautifully.', gradient: ['#B66A50', '#928E85'], tags: ['featured'] },
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
