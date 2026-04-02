'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Product, Size, EarthColor } from '@/types';
import { useCart } from '@/hooks/useCart';
import SizeSelector from './SizeSelector';
import ColorSwatch from './ColorSwatch';
import Button from '@/components/ui/Button';

export default function ProductInfo({ product }: { product: Product }) {
  const [selectedSize, setSelectedSize] = useState<Size | null>(null);
  const [selectedColor, setSelectedColor] = useState<EarthColor>(product.colors[0]);
  const [openSection, setOpenSection] = useState<string | null>(null);
  const { addItem } = useCart();

  const handleAddToCart = () => {
    if (!selectedSize) return;
    addItem(product.id, selectedSize, selectedColor);
  };

  const toggleSection = (section: string) => {
    setOpenSection(openSection === section ? null : section);
  };

  return (
    <div className="flex flex-col gap-7">
      <div>
        <span className="font-mono text-[9px] tracking-[0.4em] text-sovereign-chrome">
          {product.collection.toUpperCase()}
        </span>
        <h1 className="font-display text-3xl md:text-4xl lg:text-5xl font-light tracking-wide mt-3 leading-[1.05]">
          {product.name}
        </h1>
      </div>

      <span className="font-mono text-xl tracking-[0.1em]">${product.price}</span>

      <p className="font-mono text-[11px] text-sovereign-graphite tracking-[0.15em] leading-[2.2] max-w-md">
        {product.description.toUpperCase()}
      </p>

      {/* Color */}
      <div>
        <span className="font-mono text-[10px] tracking-[0.3em] text-sovereign-graphite block mb-4">
          COLOR — {selectedColor.toUpperCase()}
        </span>
        <ColorSwatch colors={product.colors} selected={selectedColor} onSelect={setSelectedColor} />
      </div>

      {/* Size */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <span className="font-mono text-[10px] tracking-[0.3em] text-sovereign-graphite">
            SIZE {selectedSize ? `— ${selectedSize}` : ''}
          </span>
          <button className="font-mono text-[9px] tracking-[0.2em] text-sovereign-graphite hover:text-sovereign-carbon underline underline-offset-2 transition-colors">
            SIZE GUIDE
          </button>
        </div>
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

      {/* Expandable details sections */}
      <div className="mt-2 border-t border-sovereign-silver">
        {[
          {
            key: 'details',
            title: 'PRODUCT DETAILS',
            content: `${product.description.toUpperCase()} — DESIGNED FOR EVERYDAY WEAR WITH A FOCUS ON DURABILITY AND COMFORT. UNISEX SIZING. SEASONLESS DESIGN.`,
          },
          {
            key: 'materials',
            title: 'MATERIALS & CARE',
            content: 'OUTER: 100% ORGANIC COTTON / LINING: RECYCLED POLYESTER — MACHINE WASH COLD. TUMBLE DRY LOW. DO NOT BLEACH. IRON ON LOW HEAT IF NEEDED.',
          },
          {
            key: 'shipping',
            title: 'SHIPPING & RETURNS',
            content: 'FREE STANDARD SHIPPING ON ORDERS OVER $100. EXPRESS SHIPPING AVAILABLE ($12). FREE RETURNS WITHIN 30 DAYS. ITEMS MUST BE UNWORN WITH TAGS ATTACHED.',
          },
          {
            key: 'sustainability',
            title: 'SUSTAINABILITY',
            content: 'SOVEREIGN IS COMMITTED TO RESPONSIBLE MANUFACTURING. THIS GARMENT IS PRODUCED IN FACILITIES THAT MEET FAIR LABOR STANDARDS. PACKAGING IS 100% RECYCLABLE.',
          },
        ].map((section) => (
          <div key={section.key} className="border-b border-sovereign-silver">
            <button
              onClick={() => toggleSection(section.key)}
              className="w-full flex items-center justify-between py-5 group"
            >
              <span className="font-mono text-[10px] tracking-[0.25em] text-sovereign-carbon">
                {section.title}
              </span>
              <motion.span
                animate={{ rotate: openSection === section.key ? 45 : 0 }}
                className="text-sovereign-graphite text-sm"
              >
                +
              </motion.span>
            </button>
            <AnimatePresence>
              {openSection === section.key && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className="overflow-hidden"
                >
                  <p className="font-mono text-[10px] text-sovereign-graphite tracking-[0.15em] leading-[2.2] pb-5">
                    {section.content}
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        ))}
      </div>
    </div>
  );
}
