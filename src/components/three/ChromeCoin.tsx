'use client';

import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface ChromeCoinProps {
  position?: [number, number, number];
  scale?: number;
  speed?: number;
}

export default function ChromeCoin({ position = [0, 0, 0], scale = 1, speed = 1 }: ChromeCoinProps) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (!meshRef.current) return;
    meshRef.current.rotation.y += 0.02 * speed;
    meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 0.6 * speed) * 0.15;
  });

  return (
    <mesh ref={meshRef} position={position} scale={scale}>
      <cylinderGeometry args={[1, 1, 0.12, 64]} />
      <meshPhysicalMaterial metalness={1} roughness={0.03} clearcoat={1} clearcoatRoughness={0.1} envMapIntensity={2.5} color="#d4d4d4" />
    </mesh>
  );
}
