'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useCart } from '@/hooks/useCart';
import { getProduct } from '@/lib/products';
import { EARTH_COLORS } from '@/lib/constants';
import Button from '@/components/ui/Button';
import Link from 'next/link';

export default function CartSidebar() {
  const { items, isOpen, closeCart, removeItem, updateQuantity } = useCart();

  const total = items.reduce((sum, item) => {
    const product = getProduct(item.productId);
    return sum + (product?.price ?? 0) * item.quantity;
  }, 0);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closeCart}
            className="fixed inset-0 z-50 bg-black/20 backdrop-blur-sm"
          />

          {/* Sidebar */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="fixed top-0 right-0 bottom-0 z-50 w-full max-w-md bg-sovereign-white shadow-2xl flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-sovereign-silver">
              <span className="font-mono text-xs tracking-[0.3em]">BAG ({items.length})</span>
              <button
                onClick={closeCart}
                className="font-mono text-xs tracking-[0.2em] hover:text-sovereign-graphite transition-colors"
              >
                CLOSE
              </button>
            </div>

            {/* Items */}
            <div className="flex-1 overflow-y-auto p-6 no-scrollbar">
              {items.length === 0 ? (
                <p className="font-mono text-xs text-sovereign-graphite tracking-[0.2em] text-center mt-20">
                  YOUR BAG IS EMPTY
                </p>
              ) : (
                <div className="flex flex-col gap-6">
                  {items.map((item) => {
                    const product = getProduct(item.productId);
                    if (!product) return null;
                    return (
                      <div key={`${item.productId}-${item.size}-${item.color}`} className="flex gap-4">
                        {/* Color swatch as mini preview */}
                        <div
                          className="w-20 h-24 flex-shrink-0"
                          style={{
                            background: `linear-gradient(145deg, ${product.gradient[0]}, ${product.gradient[1]})`,
                          }}
                        />
                        <div className="flex-1 flex flex-col justify-between">
                          <div>
                            <p className="font-display text-sm tracking-wide">{product.name}</p>
                            <div className="flex items-center gap-2 mt-1">
                              <span
                                className="w-3 h-3 rounded-full border border-sovereign-silver"
                                style={{ background: EARTH_COLORS[item.color] }}
                              />
                              <span className="font-mono text-[10px] text-sovereign-graphite tracking-[0.2em]">
                                {item.color.toUpperCase()} / {item.size}
                              </span>
                            </div>
                          </div>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <button
                                onClick={() => updateQuantity(item.productId, item.size, item.color, item.quantity - 1)}
                                className="font-mono text-xs text-sovereign-graphite hover:text-sovereign-carbon"
                              >
                                -
                              </button>
                              <span className="font-mono text-xs">{item.quantity}</span>
                              <button
                                onClick={() => updateQuantity(item.productId, item.size, item.color, item.quantity + 1)}
                                className="font-mono text-xs text-sovereign-graphite hover:text-sovereign-carbon"
                              >
                                +
                              </button>
                            </div>
                            <span className="font-mono text-xs tracking-[0.1em]">
                              ${product.price * item.quantity}
                            </span>
                          </div>
                          <button
                            onClick={() => removeItem(item.productId, item.size, item.color)}
                            className="font-mono text-[9px] text-sovereign-graphite hover:text-sovereign-carbon tracking-[0.2em] self-start mt-1"
                          >
                            REMOVE
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Footer */}
            {items.length > 0 && (
              <div className="p-6 border-t border-sovereign-silver">
                <div className="flex justify-between mb-4">
                  <span className="font-mono text-xs tracking-[0.2em]">TOTAL</span>
                  <span className="font-mono text-sm tracking-[0.1em]">${total}</span>
                </div>
                <Link href="/checkout" onClick={closeCart}>
                  <Button variant="filled" size="lg" className="w-full">
                    CHECKOUT
                  </Button>
                </Link>
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
