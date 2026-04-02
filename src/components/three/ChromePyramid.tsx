'use client';

import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface ChromePyramidProps {
  position?: [number, number, number];
  scale?: number;
  speed?: number;
}

export default function ChromePyramid({ position = [0, 0, 0], scale = 1, speed = 1 }: ChromePyramidProps) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (!meshRef.current) return;
    meshRef.current.rotation.y += 0.004 * speed;
    meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 0.3 * speed + 1) * 0.15;
  });

  return (
    <mesh ref={meshRef} position={position} scale={scale}>
      <coneGeometry args={[1, 1.4, 4]} />
      <meshPhysicalMaterial metalness={1} roughness={0.03} clearcoat={1} clearcoatRoughness={0.1} envMapIntensity={2.5} color="#c8c8c8" />
    </mesh>
  );
}
