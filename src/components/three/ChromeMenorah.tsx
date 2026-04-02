'use client';

import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface ChromeMenorahProps {
  position?: [number, number, number];
  scale?: number;
  speed?: number;
}

export default function ChromeMenorah({ position = [0, 0, 0], scale = 1, speed = 1 }: ChromeMenorahProps) {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (!groupRef.current) return;
    groupRef.current.rotation.y += 0.003 * speed;
    groupRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 0.3 * speed + 0.7) * 0.12;
  });

  const branchPositions = [-0.9, -0.6, -0.3, 0, 0.3, 0.6, 0.9];
  const branchHeights = [0.5, 0.7, 0.85, 1.0, 0.85, 0.7, 0.5];

  return (
    <group ref={groupRef} position={position} scale={scale}>
      {/* Base */}
      <mesh position={[0, -0.5, 0]}>
        <cylinderGeometry args={[0.3, 0.4, 0.15, 32]} />
        <meshPhysicalMaterial metalness={1} roughness={0.03} clearcoat={1} clearcoatRoughness={0.1} envMapIntensity={2.5} color="#c0c0c0" />
      </mesh>
      {/* Center stem */}
      <mesh position={[0, 0, 0]}>
        <cylinderGeometry args={[0.04, 0.04, 1, 16]} />
        <meshPhysicalMaterial metalness={1} roughness={0.03} clearcoat={1} clearcoatRoughness={0.1} envMapIntensity={2.5} color="#c0c0c0" />
      </mesh>
      {/* Branches */}
      {branchPositions.map((x, i) => (
        <group key={i}>
          {/* Vertical branch */}
          <mesh position={[x, branchHeights[i] * 0.5 - 0.1, 0]}>
            <cylinderGeometry args={[0.025, 0.025, branchHeights[i], 8]} />
            <meshPhysicalMaterial metalness={1} roughness={0.03} clearcoat={1} clearcoatRoughness={0.1} envMapIntensity={2.5} color="#c0c0c0" />
          </mesh>
          {/* Flame/cup at top */}
          <mesh position={[x, branchHeights[i] - 0.05, 0]}>
            <sphereGeometry args={[0.06, 16, 16]} />
            <meshPhysicalMaterial metalness={1} roughness={0.03} clearcoat={1} clearcoatRoughness={0.1} envMapIntensity={2.5} color="#e0e0e0" />
          </mesh>
        </group>
      ))}
    </group>
  );
}
