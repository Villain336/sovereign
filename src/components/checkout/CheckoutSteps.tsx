'use client';

import { CheckoutStep } from '@/types';

const STEPS: { key: CheckoutStep; label: string; number: string }[] = [
  { key: 'information', label: 'INFORMATION', number: '01' },
  { key: 'shipping', label: 'SHIPPING', number: '02' },
  { key: 'payment', label: 'PAYMENT', number: '03' },
  { key: 'confirmation', label: 'CONFIRMATION', number: '04' },
];

export default function CheckoutSteps({ current }: { current: CheckoutStep }) {
  const currentIndex = STEPS.findIndex((s) => s.key === current);

  return (
    <div className="flex items-center gap-2 md:gap-4">
      {STEPS.map((step, i) => (
        <div key={step.key} className="flex items-center gap-2 md:gap-4">
          <div className="flex items-center gap-2">
            <span className={`font-mono text-[10px] tracking-[0.3em] ${i <= currentIndex ? 'text-sovereign-carbon' : 'text-sovereign-chrome'}`}>
              {step.number}
            </span>
            <span className={`font-mono text-[9px] tracking-[0.2em] hidden md:block ${i <= currentIndex ? 'text-sovereign-carbon' : 'text-sovereign-chrome'}`}>
              {step.label}
            </span>
          </div>
          {i < STEPS.length - 1 && (
            <div className={`w-8 md:w-16 h-px ${i < currentIndex ? 'chrome-gradient' : 'bg-sovereign-silver'}`} />
          )}
        </div>
      ))}
    </div>
  );
}
