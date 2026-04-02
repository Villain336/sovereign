'use client';

import { useState } from 'react';
import { Product, Size, EarthColor } from '@/types';
import { useCart } from '@/hooks/useCart';
import SizeSelector from './SizeSelector';
import ColorSwatch from './ColorSwatch';
import Button from '@/components/ui/Button';

export default function ProductInfo({ product }: { product: Product }) {
  const [selectedSize, setSelectedSize] = useState<Size | null>(null);
  const [selectedColor, setSelectedColor] = useState<EarthColor>(product.colors[0]);
  const { addItem } = useCart();

  const handleAddToCart = () => {
    if (!selectedSize) return;
    addItem(product.id, selectedSize, selectedColor);
  };

  return (
    <div className="flex flex-col gap-6">
      <div>
        <span className="font-mono text-[9px] tracking-[0.4em] text-sovereign-chrome">
          {product.collection.toUpperCase()}
        </span>
        <h1 className="font-display text-3xl md:text-4xl lg:text-5xl font-light tracking-wide mt-2">
          {product.name}
        </h1>
      </div>

      <span className="font-mono text-lg tracking-[0.1em]">${product.price}</span>

      <p className="font-mono text-[11px] text-sovereign-graphite tracking-[0.15em] leading-relaxed max-w-md">
        {product.description.toUpperCase()}
      </p>

      {/* Color */}
      <div>
        <span className="font-mono text-[10px] tracking-[0.3em] text-sovereign-graphite block mb-3">
          COLOR — {selectedColor.toUpperCase()}
        </span>
        <ColorSwatch colors={product.colors} selected={selectedColor} onSelect={setSelectedColor} />
      </div>

      {/* Size */}
      <div>
        <span className="font-mono text-[10px] tracking-[0.3em] text-sovereign-graphite block mb-3">
          SIZE {selectedSize ? `— ${selectedSize}` : ''}
        </span>
        <SizeSelector sizes={product.sizes} selected={selectedSize} onSelect={setSelectedSize} />
      </div>

      {/* Add to cart */}
      <Button
        variant="filled"
        size="lg"
        onClick={handleAddToCart}
        className={`w-full mt-2 ${!selectedSize ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        {selectedSize ? 'ADD TO BAG' : 'SELECT A SIZE'}
      </Button>

      {/* Details */}
      <div className="mt-4 pt-6 border-t border-sovereign-silver">
        <div className="flex flex-col gap-3">
          {['Free shipping over $100', 'Easy 30-day returns', 'Ethically manufactured'].map((detail) => (
            <div key={detail} className="flex items-center gap-3">
              <div className="w-1 h-1 rounded-full bg-sovereign-chrome" />
              <span className="font-mono text-[10px] tracking-[0.15em] text-sovereign-graphite">
                {detail.toUpperCase()}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
