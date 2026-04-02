'use client';

import dynamic from 'next/dynamic';

const FloatingScene = dynamic(() => import('./FloatingScene'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center">
      <div className="w-32 h-32 rounded-full chrome-gradient animate-pulse" />
    </div>
  ),
});

interface SceneLoaderProps {
  variant?: 'hero' | 'accent' | 'minimal' | 'knot' | 'icosahedron' | 'pyramid' | 'cube' | 'coin' | 'star' | 'menorah' | 'human' | 'ring';
  className?: string;
}

export default function SceneLoader({ variant = 'hero', className = '' }: SceneLoaderProps) {
  return <FloatingScene variant={variant} className={className} />;
}
