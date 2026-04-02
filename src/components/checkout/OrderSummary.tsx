'use client';

import { useCart } from '@/hooks/useCart';
import { getProduct } from '@/lib/products';
import { EARTH_COLORS } from '@/lib/constants';
import Divider from '@/components/ui/Divider';

export default function OrderSummary() {
  const { items } = useCart();

  const subtotal = items.reduce((sum, item) => {
    const product = getProduct(item.productId);
    return sum + (product?.price ?? 0) * item.quantity;
  }, 0);

  return (
    <div className="bg-sovereign-white/80 backdrop-blur-md p-6 border border-sovereign-silver">
      <span className="font-mono text-[10px] tracking-[0.3em] text-sovereign-graphite">ORDER SUMMARY</span>

      <div className="mt-4 flex flex-col gap-4">
        {items.map((item) => {
          const product = getProduct(item.productId);
          if (!product) return null;
          return (
            <div key={`${item.productId}-${item.size}-${item.color}`} className="flex gap-3">
              <div className="w-12 h-14 flex-shrink-0" style={{ background: `linear-gradient(145deg, ${product.gradient[0]}, ${product.gradient[1]})` }} />
              <div className="flex-1">
                <p className="font-display text-xs tracking-wide">{product.name}</p>
                <div className="flex items-center gap-1 mt-1">
                  <span className="w-2 h-2 rounded-full" style={{ background: EARTH_COLORS[item.color] }} />
                  <span className="font-mono text-[9px] text-sovereign-graphite tracking-[0.15em]">
                    {item.color.toUpperCase()} / {item.size} x{item.quantity}
                  </span>
                </div>
              </div>
              <span className="font-mono text-xs">${product.price * item.quantity}</span>
            </div>
          );
        })}
      </div>

      <Divider className="my-4" />

      <div className="flex flex-col gap-2">
        <div className="flex justify-between">
          <span className="font-mono text-[10px] tracking-[0.2em] text-sovereign-graphite">SUBTOTAL</span>
          <span className="font-mono text-xs">${subtotal}</span>
        </div>
        <div className="flex justify-between">
          <span className="font-mono text-[10px] tracking-[0.2em] text-sovereign-graphite">SHIPPING</span>
          <span className="font-mono text-xs">{subtotal >= 100 ? 'FREE' : '$12'}</span>
        </div>
      </div>

      <Divider className="my-4" />

      <div className="flex justify-between">
        <span className="font-mono text-xs tracking-[0.2em]">TOTAL</span>
        <span className="font-mono text-sm font-bold">${subtotal >= 100 ? subtotal : subtotal + 12}</span>
      </div>
    </div>
  );
}
