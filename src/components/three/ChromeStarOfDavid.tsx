'use client';

import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface ChromeStarOfDavidProps {
  position?: [number, number, number];
  scale?: number;
  speed?: number;
}

export default function ChromeStarOfDavid({ position = [0, 0, 0], scale = 1, speed = 1 }: ChromeStarOfDavidProps) {
  const meshRef = useRef<THREE.Group>(null);

  const extrudeSettings = useMemo(() => ({ depth: 0.15, bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.02, bevelSegments: 3 }), []);

  const triangle1 = useMemo(() => {
    const shape = new THREE.Shape();
    shape.moveTo(0, 1);
    shape.lineTo(-0.866, -0.5);
    shape.lineTo(0.866, -0.5);
    shape.closePath();
    return shape;
  }, []);

  const triangle2 = useMemo(() => {
    const shape = new THREE.Shape();
    shape.moveTo(0, -1);
    shape.lineTo(0.866, 0.5);
    shape.lineTo(-0.866, 0.5);
    shape.closePath();
    return shape;
  }, []);

  useFrame((state) => {
    if (!meshRef.current) return;
    meshRef.current.rotation.y += 0.004 * speed;
    meshRef.current.rotation.z += 0.001 * speed;
    meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 0.4 * speed + 2) * 0.2;
  });

  return (
    <group ref={meshRef} position={position} scale={scale}>
      <mesh>
        <extrudeGeometry args={[triangle1, extrudeSettings]} />
        <meshPhysicalMaterial metalness={1} roughness={0.03} clearcoat={1} clearcoatRoughness={0.1} envMapIntensity={2.5} color="#c0c0c0" />
      </mesh>
      <mesh>
        <extrudeGeometry args={[triangle2, extrudeSettings]} />
        <meshPhysicalMaterial metalness={1} roughness={0.03} clearcoat={1} clearcoatRoughness={0.1} envMapIntensity={2.5} color="#c0c0c0" />
      </mesh>
    </group>
  );
}
