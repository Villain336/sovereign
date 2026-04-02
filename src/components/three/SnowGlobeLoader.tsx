'use client';

import dynamic from 'next/dynamic';

const SnowGlobeScene = dynamic(() => import('./SnowGlobeScene'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center">
      <div className="w-40 h-40 rounded-full chrome-gradient animate-pulse opacity-30" />
    </div>
  ),
});

export default function SnowGlobeLoader({ className = '' }: { className?: string }) {
  return <SnowGlobeScene className={className} />;
}
