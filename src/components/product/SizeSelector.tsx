'use client';

import { Size } from '@/types';

interface SizeSelectorProps {
  sizes: Size[];
  selected: Size | null;
  onSelect: (size: Size) => void;
}

export default function SizeSelector({ sizes, selected, onSelect }: SizeSelectorProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {sizes.map((size) => (
        <button
          key={size}
          onClick={() => onSelect(size)}
          className={`min-w-[44px] h-11 px-3 font-mono text-[11px] tracking-[0.2em] border transition-all duration-200 ${
            selected === size
              ? 'border-sovereign-carbon bg-sovereign-carbon text-sovereign-white'
              : 'border-sovereign-silver text-sovereign-carbon hover:border-sovereign-carbon'
          }`}
        >
          {size}
        </button>
      ))}
    </div>
  );
}
