export type EarthColor = 'sand' | 'olive' | 'slate' | 'charcoal' | 'cream' | 'clay' | 'stone' | 'moss';
export type Size = 'XS' | 'S' | 'M' | 'L' | 'XL' | 'XXL';

export interface Product {
  id: string;
  name: string;
  slug: string;
  collection: string;
  price: number;
  colors: EarthColor[];
  sizes: Size[];
  description: string;
  gradient: [string, string];
  tags: string[];
}

export interface Collection {
  slug: string;
  name: string;
  description: string;
  gradient: [string, string];
}

export interface CartItem {
  productId: string;
  color: EarthColor;
  size: Size;
  quantity: number;
}

export interface CartState {
  items: CartItem[];
  isOpen: boolean;
}

export type CartAction =
  | { type: 'ADD_ITEM'; payload: Omit<CartItem, 'quantity'> }
  | { type: 'REMOVE_ITEM'; payload: { productId: string; size: string; color: string } }
  | { type: 'UPDATE_QUANTITY'; payload: { productId: string; size: string; color: string; quantity: number } }
  | { type: 'TOGGLE_CART' }
  | { type: 'CLOSE_CART' }
  | { type: 'CLEAR_CART' };

export type ChromeShape = 'sphere' | 'torus' | 'blob' | 'knot' | 'icosahedron' | 'pyramid' | 'cube' | 'coin' | 'starOfDavid' | 'menorah' | 'human' | 'ring';

export interface Look {
  id: string;
  title: string;
  description: string;
  products: string[];
  gradient: [string, string];
  chromeShape: ChromeShape;
}

export interface Drop {
  id: string;
  name: string;
  description: string;
  date: string;
  products: string[];
  isLive: boolean;
  gradient: [string, string];
}

export type CheckoutStep = 'information' | 'shipping' | 'payment' | 'confirmation';
