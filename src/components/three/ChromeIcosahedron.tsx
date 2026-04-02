'use client';

import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface ChromeIcosahedronProps {
  position?: [number, number, number];
  scale?: number;
  speed?: number;
}

export default function ChromeIcosahedron({ position = [0, 0, 0], scale = 1, speed = 1 }: ChromeIcosahedronProps) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (!meshRef.current) return;
    meshRef.current.rotation.x += 0.002 * speed;
    meshRef.current.rotation.y += 0.004 * speed;
    meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 0.5 * speed + 0.5) * 0.25;
  });

  return (
    <mesh ref={meshRef} position={position} scale={scale}>
      <icosahedronGeometry args={[1, 0]} />
      <meshPhysicalMaterial metalness={1} roughness={0.03} clearcoat={1} clearcoatRoughness={0.1} envMapIntensity={2.5} color="#d0d0d0" />
    </mesh>
  );
}
