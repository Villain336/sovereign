'use client';

import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface ChromeCubeProps {
  position?: [number, number, number];
  scale?: number;
  speed?: number;
}

export default function ChromeCube({ position = [0, 0, 0], scale = 1, speed = 1 }: ChromeCubeProps) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (!meshRef.current) return;
    meshRef.current.rotation.x += 0.003 * speed;
    meshRef.current.rotation.y += 0.004 * speed;
    meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 0.4 * speed + 1.5) * 0.2;
  });

  return (
    <mesh ref={meshRef} position={position} scale={scale}>
      <boxGeometry args={[1, 1, 1]} />
      <meshPhysicalMaterial metalness={1} roughness={0.03} clearcoat={1} clearcoatRoughness={0.1} envMapIntensity={2.5} color="#c0c0c0" />
    </mesh>
  );
}
