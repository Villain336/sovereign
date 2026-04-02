'use client';

import { Canvas } from '@react-three/fiber';
import { Environment } from '@react-three/drei';
import { Suspense } from 'react';
import ChromeSphere from './ChromeSphere';
import ChromeTorus from './ChromeTorus';
import ChromeBlob from './ChromeBlob';
import ChromeKnot from './ChromeKnot';
import ChromeIcosahedron from './ChromeIcosahedron';
import ChromePyramid from './ChromePyramid';
import ChromeCube from './ChromeCube';
import ChromeCoin from './ChromeCoin';
import ChromeStarOfDavid from './ChromeStarOfDavid';
import ChromeMenorah from './ChromeMenorah';
import ChromeHuman from './ChromeHuman';
import ChromeRing from './ChromeRing';

interface FloatingSceneProps {
  variant?: 'hero' | 'accent' | 'minimal' | 'knot' | 'icosahedron' | 'pyramid' | 'cube' | 'coin' | 'star' | 'menorah' | 'human' | 'ring';
  className?: string;
}

export default function FloatingScene({ variant = 'hero', className = '' }: FloatingSceneProps) {
  return (
    <div className={`w-full h-full ${className}`}>
      <Canvas
        camera={{ position: [0, 0, 5], fov: 45 }}
        style={{ background: 'transparent' }}
        gl={{ alpha: true, antialias: true }}
      >
        <Suspense fallback={null}>
          <Environment preset="studio" />
          <ambientLight intensity={0.3} />
          <directionalLight position={[5, 5, 5]} intensity={0.5} />

          {variant === 'hero' && (
            <>
              <ChromeSphere position={[0, 0.2, 0]} scale={1.4} speed={0.8} />
              <ChromeTorus position={[2.5, -0.5, -1]} scale={0.5} speed={1.2} />
              <ChromeBlob position={[-2.2, 1, -1.5]} scale={0.4} speed={0.6} />
            </>
          )}

          {variant === 'accent' && (
            <>
              <ChromeSphere position={[0, 0, 0]} scale={0.8} speed={0.5} />
              <ChromeTorus position={[1.5, 0.5, -0.5]} scale={0.3} speed={0.8} />
            </>
          )}

          {variant === 'minimal' && <ChromeSphere position={[0, 0, 0]} scale={0.6} speed={0.4} />}
          {variant === 'knot' && <ChromeKnot position={[0, 0, 0]} scale={0.6} speed={0.5} />}
          {variant === 'icosahedron' && <ChromeIcosahedron position={[0, 0, 0]} scale={0.7} speed={0.5} />}
          {variant === 'pyramid' && <ChromePyramid position={[0, 0, 0]} scale={0.7} speed={0.4} />}
          {variant === 'cube' && <ChromeCube position={[0, 0, 0]} scale={0.6} speed={0.5} />}
          {variant === 'coin' && <ChromeCoin position={[0, 0, 0]} scale={0.6} speed={0.8} />}
          {variant === 'star' && <ChromeStarOfDavid position={[0, 0, 0]} scale={0.5} speed={0.4} />}
          {variant === 'menorah' && <ChromeMenorah position={[0, 0, 0]} scale={0.5} speed={0.4} />}
          {variant === 'human' && <ChromeHuman position={[0, -0.3, 0]} scale={0.6} speed={0.3} />}
          {variant === 'ring' && <ChromeRing position={[0, 0, 0]} scale={0.5} speed={1.5} />}
        </Suspense>
      </Canvas>
    </div>
  );
}
