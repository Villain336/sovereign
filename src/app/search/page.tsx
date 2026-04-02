'use client';

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { products } from '@/lib/products';
import ProductCard from '@/components/product/ProductCard';
import SceneLoader from '@/components/three/SceneLoader';

export default function SearchPage() {
  const [query, setQuery] = useState('');

  const results = useMemo(() => {
    if (!query.trim()) return [];
    const q = query.toLowerCase();
    return products.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        p.collection.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q) ||
        p.tags.some((t) => t.includes(q))
    );
  }, [query]);

  return (
    <div className="pt-28 pb-20 md:pb-32 min-h-screen">
      <div className="max-w-7xl mx-auto px-6 md:px-16">
        {/* Search input */}
        <div className="mb-16">
          <span className="font-mono text-[10px] tracking-[0.5em] text-sovereign-chrome block mb-4">SEARCH</span>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="WHAT ARE YOU LOOKING FOR?"
            autoFocus
            className="w-full bg-transparent border-b-2 border-sovereign-carbon pb-4 font-display text-3xl md:text-5xl font-light tracking-wide text-sovereign-carbon placeholder-sovereign-silver outline-none"
          />
          {query && (
            <span className="font-mono text-[10px] tracking-[0.2em] text-sovereign-graphite mt-3 block">
              {results.length} {results.length === 1 ? 'RESULT' : 'RESULTS'}
            </span>
          )}
        </div>

        {/* Results */}
        <AnimatePresence mode="wait">
          {results.length > 0 ? (
            <motion.div
              key="results"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6"
            >
              {results.map((product) => (
                <motion.div
                  key={product.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <ProductCard product={product} />
                </motion.div>
              ))}
            </motion.div>
          ) : query.trim() ? (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-20"
            >
              <div className="w-32 h-32 mx-auto mb-6 opacity-30">
                <SceneLoader variant="minimal" />
              </div>
              <p className="font-mono text-xs text-sovereign-graphite tracking-[0.2em]">
                NO RESULTS FOUND
              </p>
            </motion.div>
          ) : (
            <motion.div
              key="browse"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-20"
            >
              <p className="font-mono text-[10px] text-sovereign-chrome tracking-[0.3em]">
                START TYPING TO SEARCH ALL PRODUCTS
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
