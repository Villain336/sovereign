'use client';

import { useRef, useState, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Environment } from '@react-three/drei';
import { Suspense } from 'react';
import * as THREE from 'three';

const CHROME_MAT_PROPS = { metalness: 1, roughness: 0.03, clearcoat: 1, clearcoatRoughness: 0.1, envMapIntensity: 2.5 };
const BOUNDARY_RADIUS = 4.5;
const DAMPING = 0.998;

interface FloatingShape {
  id: number;
  geometry: 'sphere' | 'torus' | 'knot' | 'icosahedron' | 'pyramid' | 'cube' | 'coin' | 'star' | 'ring' | 'blob';
  position: THREE.Vector3;
  velocity: THREE.Vector3;
  rotation: THREE.Euler;
  rotationSpeed: THREE.Vector3;
  scale: number;
  color: string;
}

function generateShapes(): FloatingShape[] {
  const geometries: FloatingShape['geometry'][] = [
    'sphere', 'torus', 'knot', 'icosahedron', 'pyramid',
    'cube', 'coin', 'star', 'ring', 'blob',
    'sphere', 'cube', 'knot',
  ];
  const colors = ['#c0c0c0', '#d0d0d0', '#e0e0e0', '#b8b8b8', '#d4d4d4'];

  return geometries.map((geometry, i) => ({
    id: i,
    geometry,
    position: new THREE.Vector3(
      (Math.random() - 0.5) * 6,
      (Math.random() - 0.5) * 6,
      (Math.random() - 0.5) * 4,
    ),
    velocity: new THREE.Vector3(
      (Math.random() - 0.5) * 0.02,
      (Math.random() - 0.5) * 0.02,
      (Math.random() - 0.5) * 0.015,
    ),
    rotation: new THREE.Euler(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI),
    rotationSpeed: new THREE.Vector3(
      (Math.random() - 0.5) * 0.01,
      (Math.random() - 0.5) * 0.01,
      (Math.random() - 0.5) * 0.01,
    ),
    scale: 0.2 + Math.random() * 0.35,
    color: colors[i % colors.length],
  }));
}

function ShapeGeometry({ type }: { type: FloatingShape['geometry'] }) {
  switch (type) {
    case 'sphere': return <sphereGeometry args={[1, 32, 32]} />;
    case 'torus': return <torusGeometry args={[1, 0.35, 16, 32]} />;
    case 'knot': return <torusKnotGeometry args={[0.8, 0.25, 64, 16]} />;
    case 'icosahedron': return <icosahedronGeometry args={[1, 0]} />;
    case 'pyramid': return <coneGeometry args={[1, 1.4, 4]} />;
    case 'cube': return <boxGeometry args={[1, 1, 1]} />;
    case 'coin': return <cylinderGeometry args={[1, 1, 0.12, 32]} />;
    case 'ring': return <torusGeometry args={[1, 0.08, 8, 32]} />;
    case 'star': return <octahedronGeometry args={[1, 0]} />;
    case 'blob': return <dodecahedronGeometry args={[1, 0]} />;
    default: return <sphereGeometry args={[1, 32, 32]} />;
  }
}

function PhysicsShape({ shape, allShapes }: { shape: FloatingShape; allShapes: FloatingShape[] }) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame(() => {
    if (!meshRef.current) return;

    // Update position
    shape.position.add(shape.velocity);

    // Boundary collision — reflect off invisible sphere
    if (shape.position.length() > BOUNDARY_RADIUS) {
      const normal = shape.position.clone().normalize();
      shape.velocity.reflect(normal).multiplyScalar(0.9);
      shape.position.setLength(BOUNDARY_RADIUS - 0.1);
    }

    // Shape-to-shape collision (simple elastic)
    for (const other of allShapes) {
      if (other.id === shape.id) continue;
      const dist = shape.position.distanceTo(other.position);
      const minDist = (shape.scale + other.scale) * 1.2;
      if (dist < minDist && dist > 0) {
        const normal = shape.position.clone().sub(other.position).normalize();
        shape.velocity.add(normal.clone().multiplyScalar(0.003));
        other.velocity.sub(normal.clone().multiplyScalar(0.003));
        // Push apart
        const overlap = (minDist - dist) * 0.5;
        shape.position.add(normal.clone().multiplyScalar(overlap));
        other.position.sub(normal.clone().multiplyScalar(overlap));
      }
    }

    // Damping
    shape.velocity.multiplyScalar(DAMPING);

    // Update rotation
    shape.rotation.x += shape.rotationSpeed.x;
    shape.rotation.y += shape.rotationSpeed.y;
    shape.rotation.z += shape.rotationSpeed.z;

    // Apply to mesh
    meshRef.current.position.copy(shape.position);
    meshRef.current.rotation.copy(shape.rotation);
  });

  return (
    <mesh ref={meshRef} position={shape.position} rotation={shape.rotation} scale={shape.scale}>
      <ShapeGeometry type={shape.geometry} />
      <meshPhysicalMaterial {...CHROME_MAT_PROPS} color={shape.color} />
    </mesh>
  );
}

function SnowGlobeContent() {
  const [shapes] = useState(generateShapes);

  return (
    <>
      {shapes.map((shape) => (
        <PhysicsShape key={shape.id} shape={shape} allShapes={shapes} />
      ))}
    </>
  );
}

export default function SnowGlobeScene({ className = '' }: { className?: string }) {
  return (
    <div className={`w-full h-full ${className}`}>
      <Canvas
        camera={{ position: [0, 0, 8], fov: 50 }}
        style={{ background: 'transparent' }}
        gl={{ alpha: true, antialias: true }}
      >
        <Suspense fallback={null}>
          <Environment preset="studio" />
          <ambientLight intensity={0.3} />
          <directionalLight position={[5, 5, 5]} intensity={0.5} />
          <SnowGlobeContent />
        </Suspense>
      </Canvas>
    </div>
  );
}
