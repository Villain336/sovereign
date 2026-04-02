export const BRAND = {
  name: 'SOVEREIGN',
  tagline: 'The Future of Essential Clothing',
  manifesto: 'We believe in the quiet power of simplicity. No logos. No noise. Just precision-engineered garments for the modern human. Sovereign exists at the intersection of utility and beauty — where every stitch serves a purpose and every silhouette tells a story of restraint.',
} as const;

export const EARTH_COLORS: Record<string, string> = {
  sand: '#C2B280',
  olive: '#708238',
  slate: '#6E7B8B',
  charcoal: '#36454F',
  cream: '#FFFDD0',
  clay: '#B66A50',
  stone: '#928E85',
  moss: '#8A9A5B',
} as const;

export const NAV_LINKS = [
  { href: '/collections', label: 'COLLECTIONS' },
  { href: '/collections/essentials', label: 'ESSENTIALS' },
  { href: '/collections/outerwear', label: 'OUTERWEAR' },
  { href: '/about', label: 'ABOUT' },
] as const;
