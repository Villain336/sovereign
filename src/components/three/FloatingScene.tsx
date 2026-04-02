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
        camera={{ position: [0, 0, 7], fov: 45 }}
        style={{ background: 'transparent' }}
        gl={{ alpha: true, antialias: true }}
      >
        <Suspense fallback={null}>
          <Environment preset="studio" />
          <ambientLight intensity={0.3} />
          <directionalLight position={[5, 5, 5]} intensity={0.5} />

          {variant === 'hero' && (
            <>
              <ChromeSphere position={[0.5, 0, 0]} scale={2.0} speed={0.6} />
              <ChromeTorus position={[3, -1.2, -2]} scale={0.8} speed={1.0} />
              <ChromeBlob position={[-2.8, 1.5, -1.5]} scale={0.65} speed={0.5} />
              <ChromeIcosahedron position={[-1.5, -2, -2]} scale={0.4} speed={0.7} />
              <ChromeCoin position={[3.2, 1.8, -1]} scale={0.3} speed={1.5} />
            </>
          )}

          {variant === 'accent' && (
            <>
              <ChromeSphere position={[0, 0, 0]} scale={1.2} speed={0.4} />
              <ChromeTorus position={[2, 0.8, -1]} scale={0.5} speed={0.7} />
              <ChromePyramid position={[-1.8, -0.8, -1.5]} scale={0.35} speed={0.5} />
            </>
          )}

          {variant === 'minimal' && (
            <>
              <ChromeSphere position={[0, 0, 0]} scale={1.0} speed={0.4} />
              <ChromeRing position={[0, 0, -0.5]} scale={0.35} speed={0.8} />
            </>
          )}

          {variant === 'knot' && (
            <>
              <ChromeKnot position={[0, 0, 0]} scale={0.9} speed={0.4} />
              <ChromeSphere position={[1.8, -1, -1]} scale={0.3} speed={0.6} />
            </>
          )}
          {variant === 'icosahedron' && (
            <>
              <ChromeIcosahedron position={[0, 0, 0]} scale={1.1} speed={0.4} />
              <ChromeRing position={[0, 0, -0.3]} scale={0.4} speed={0.6} />
            </>
          )}
          {variant === 'pyramid' && (
            <>
              <ChromePyramid position={[0, 0, 0]} scale={1.1} speed={0.35} />
              <ChromeCube position={[1.5, -0.8, -1]} scale={0.3} speed={0.5} />
            </>
          )}
          {variant === 'cube' && (
            <>
              <ChromeCube position={[0, 0, 0]} scale={1.0} speed={0.4} />
              <ChromeSphere position={[-1.5, 0.8, -1]} scale={0.25} speed={0.6} />
            </>
          )}
          {variant === 'coin' && (
            <>
              <ChromeCoin position={[0, 0, 0]} scale={1.0} speed={0.7} />
              <ChromeRing position={[1.2, 0.5, -0.5]} scale={0.3} speed={1.0} />
            </>
          )}
          {variant === 'star' && (
            <>
              <ChromeStarOfDavid position={[0, 0, 0]} scale={0.85} speed={0.35} />
              <ChromeSphere position={[1.5, -0.8, -1]} scale={0.25} speed={0.5} />
            </>
          )}
          {variant === 'menorah' && (
            <>
              <ChromeMenorah position={[0, -0.2, 0]} scale={0.8} speed={0.3} />
              <ChromeTorus position={[0, 1.2, -1]} scale={0.25} speed={0.6} />
            </>
          )}
          {variant === 'human' && (
            <>
              <ChromeHuman position={[0, -0.5, 0]} scale={0.9} speed={0.25} />
              <ChromeSphere position={[1.5, 0.5, -1]} scale={0.2} speed={0.5} />
            </>
          )}
          {variant === 'ring' && (
            <>
              <ChromeRing position={[0, 0, 0]} scale={0.8} speed={1.2} />
              <ChromeSphere position={[0, 0, 0]} scale={0.3} speed={0.4} />
            </>
          )}
        </Suspense>
      </Canvas>
    </div>
  );
}
