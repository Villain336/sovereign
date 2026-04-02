'use client';

import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Sphere } from '@react-three/drei';
import * as THREE from 'three';

interface ChromeSphereProps {
  position?: [number, number, number];
  scale?: number;
  speed?: number;
}

export default function ChromeSphere({ position = [0, 0, 0], scale = 1, speed = 1 }: ChromeSphereProps) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (!meshRef.current) return;
    meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 0.5 * speed) * 0.3;
    meshRef.current.rotation.y += 0.003 * speed;
  });

  return (
    <Sphere ref={meshRef} args={[1, 64, 64]} position={position} scale={scale}>
      <meshPhysicalMaterial
        metalness={1}
        roughness={0.03}
        clearcoat={1}
        clearcoatRoughness={0.1}
        envMapIntensity={2.5}
        color="#c0c0c0"
      />
    </Sphere>
  );
}
