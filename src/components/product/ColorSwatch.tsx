'use client';

import { EarthColor } from '@/types';
import { EARTH_COLORS } from '@/lib/constants';

interface ColorSwatchProps {
  colors: EarthColor[];
  selected: EarthColor | null;
  onSelect: (color: EarthColor) => void;
}

export default function ColorSwatch({ colors, selected, onSelect }: ColorSwatchProps) {
  return (
    <div className="flex gap-3">
      {colors.map((color) => (
        <button
          key={color}
          onClick={() => onSelect(color)}
          className={`w-8 h-8 rounded-full border-2 transition-all duration-200 ${
            selected === color ? 'border-sovereign-carbon scale-110' : 'border-sovereign-silver hover:border-sovereign-graphite'
          }`}
          style={{ background: EARTH_COLORS[color] }}
          aria-label={color}
        />
      ))}
    </div>
  );
}
