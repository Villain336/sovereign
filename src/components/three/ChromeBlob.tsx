'use client';

import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { MeshDistortMaterial, Sphere } from '@react-three/drei';
import * as THREE from 'three';

interface ChromeBlobProps {
  position?: [number, number, number];
  scale?: number;
  speed?: number;
}

export default function ChromeBlob({ position = [0, 0, 0], scale = 1, speed = 1 }: ChromeBlobProps) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (!meshRef.current) return;
    meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 0.3 * speed + 2) * 0.15;
    meshRef.current.rotation.y += 0.002 * speed;
  });

  return (
    <Sphere ref={meshRef} args={[1, 64, 64]} position={position} scale={scale}>
      <MeshDistortMaterial
        metalness={1}
        roughness={0.05}
        clearcoat={1}
        clearcoatRoughness={0.1}
        envMapIntensity={2}
        color="#e0e0e0"
        distort={0.4}
        speed={2 * speed}
      />
    </Sphere>
  );
}
