'use client';

import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface ChromeHumanProps {
  position?: [number, number, number];
  scale?: number;
  speed?: number;
}

export default function ChromeHuman({ position = [0, 0, 0], scale = 1, speed = 1 }: ChromeHumanProps) {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (!groupRef.current) return;
    groupRef.current.rotation.y += 0.003 * speed;
    const breathe = 1 + Math.sin(state.clock.elapsedTime * 1.5 * speed) * 0.02;
    groupRef.current.scale.set(scale * breathe, scale * breathe, scale * breathe);
    groupRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 0.4 * speed) * 0.15;
  });

  const mat = <meshPhysicalMaterial metalness={1} roughness={0.03} clearcoat={1} clearcoatRoughness={0.1} envMapIntensity={2.5} color="#c0c0c0" />;

  return (
    <group ref={groupRef} position={position} scale={scale}>
      {/* Head */}
      <mesh position={[0, 1.1, 0]}>
        <sphereGeometry args={[0.22, 32, 32]} />
        {mat}
      </mesh>
      {/* Torso */}
      <mesh position={[0, 0.5, 0]}>
        <capsuleGeometry args={[0.2, 0.6, 16, 32]} />
        {mat}
      </mesh>
      {/* Left arm */}
      <mesh position={[-0.35, 0.6, 0]} rotation={[0, 0, 0.3]}>
        <capsuleGeometry args={[0.07, 0.5, 8, 16]} />
        {mat}
      </mesh>
      {/* Right arm */}
      <mesh position={[0.35, 0.6, 0]} rotation={[0, 0, -0.3]}>
        <capsuleGeometry args={[0.07, 0.5, 8, 16]} />
        {mat}
      </mesh>
      {/* Left leg */}
      <mesh position={[-0.12, -0.15, 0]}>
        <capsuleGeometry args={[0.08, 0.55, 8, 16]} />
        {mat}
      </mesh>
      {/* Right leg */}
      <mesh position={[0.12, -0.15, 0]}>
        <capsuleGeometry args={[0.08, 0.55, 8, 16]} />
        {mat}
      </mesh>
    </group>
  );
}
