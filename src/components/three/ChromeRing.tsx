'use client';

import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface ChromeRingProps {
  position?: [number, number, number];
  scale?: number;
  speed?: number;
}

export default function ChromeRing({ position = [0, 0, 0], scale = 1, speed = 1 }: ChromeRingProps) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame(() => {
    if (!meshRef.current) return;
    meshRef.current.rotation.z += 0.02 * speed;
  });

  return (
    <mesh ref={meshRef} position={position} scale={scale}>
      <torusGeometry args={[1, 0.08, 16, 64]} />
      <meshPhysicalMaterial metalness={1} roughness={0.03} clearcoat={1} clearcoatRoughness={0.1} envMapIntensity={2.5} color="#d4d4d4" />
    </mesh>
  );
}
