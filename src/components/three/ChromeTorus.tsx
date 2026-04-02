'use client';

import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Torus } from '@react-three/drei';
import * as THREE from 'three';

interface ChromeTorusProps {
  position?: [number, number, number];
  scale?: number;
  speed?: number;
}

export default function ChromeTorus({ position = [0, 0, 0], scale = 1, speed = 1 }: ChromeTorusProps) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (!meshRef.current) return;
    meshRef.current.rotation.x += 0.005 * speed;
    meshRef.current.rotation.z += 0.003 * speed;
    meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 0.4 * speed + 1) * 0.2;
  });

  return (
    <Torus ref={meshRef} args={[1, 0.35, 32, 64]} position={position} scale={scale}>
      <meshPhysicalMaterial
        metalness={1}
        roughness={0.03}
        clearcoat={1}
        clearcoatRoughness={0.1}
        envMapIntensity={2.5}
        color="#d4d4d4"
      />
    </Torus>
  );
}
