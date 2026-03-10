import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars, Text } from '@react-three/drei';
import * as THREE from 'three';

interface Props {
  forestId: number;
  metrics?: any;
  riskLevel?: string;
}

const getTreeColor = (riskLevel: string) => {
  switch (riskLevel?.toLowerCase()) {
    case 'critical': return '#8B0000';
    case 'high':     return '#CC4400';
    case 'medium':   return '#8B8B00';
    default:         return '#228B22';
  }
};

function Tree({ position, scale, riskLevel }: { position: [number,number,number], scale: number, riskLevel: string }) {
  const treeColor = getTreeColor(riskLevel);
  return (
    <group position={position}>
      <mesh position={[0, scale * 0.5, 0]}>
        <cylinderGeometry args={[0.15 * scale, 0.2 * scale, scale, 8]} />
        <meshStandardMaterial color="#4a2f1a" roughness={0.8} />
      </mesh>
      <mesh position={[0, scale * 1.4, 0]}>
        <coneGeometry args={[0.7 * scale, 1.4 * scale, 8]} />
        <meshStandardMaterial color={treeColor} roughness={0.6} />
      </mesh>
      <mesh position={[0, scale * 2.1, 0]}>
        <coneGeometry args={[0.5 * scale, 1.1 * scale, 8]} />
        <meshStandardMaterial color={treeColor} roughness={0.6} />
      </mesh>
    </group>
  );
}

function Forest({ riskLevel }: { riskLevel: string }) {
  const trees = useMemo(() => {
    const result = [];
    for (let i = 0; i < 60; i++) {
      const x = (Math.random() - 0.5) * 18;
      const z = (Math.random() - 0.5) * 18;
      const scale = 0.5 + Math.random() * 0.8;
      result.push({ position: [x, 0, z] as [number,number,number], scale });
    }
    return result;
  }, []);

  return (
    <>
      {trees.map((t, i) => (
        <Tree key={i} position={t.position} scale={t.scale} riskLevel={riskLevel} />
      ))}
    </>
  );
}

function Ground({ riskLevel }: { riskLevel: string }) {
  const color = riskLevel === 'critical' ? '#3d1a00' : riskLevel === 'high' ? '#4a2800' : '#2d4a1e';
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.1, 0]}>
      <planeGeometry args={[25, 25]} />
      <meshStandardMaterial color={color} roughness={1} />
    </mesh>
  );
}

function MetricsPanel({ metrics, riskLevel }: { metrics: any, riskLevel: string }) {
  if (!metrics) return null;
  return (
    <group position={[12, 4, 0]}>
      <Text position={[0, 2, 0]} fontSize={0.5} color="#4ade80" anchorX="center">
        🌡️ {metrics.avg_temperature?.toFixed(1)}°C
      </Text>
      <Text position={[0, 1, 0]} fontSize={0.5} color="#60a5fa" anchorX="center">
        💧 {metrics.avg_humidity?.toFixed(1)}%
      </Text>
      <Text position={[0, 0, 0]} fontSize={0.5} color="#a3e635" anchorX="center">
        NDVI {metrics.avg_ndvi?.toFixed(3)}
      </Text>
    </group>
  );
}

function RotatingLight() {
  const lightRef = useRef<THREE.DirectionalLight>(null);
  useFrame(({ clock }) => {
    if (lightRef.current) {
      lightRef.current.position.x = Math.sin(clock.getElapsedTime() * 0.3) * 10;
      lightRef.current.position.z = Math.cos(clock.getElapsedTime() * 0.3) * 10;
    }
  });
  return <directionalLight ref={lightRef} intensity={1.5} castShadow />;
}

const Forest3D: React.FC<Props> = ({ forestId, metrics, riskLevel = 'normal' }) => {
  return (
    <Canvas
      className="h-full w-full"
      camera={{ position: [15, 10, 15], fov: 50 }}
      shadows
    >
      <color attach="background" args={['#0a1628']} />
      <Stars radius={100} depth={50} count={3000} factor={4} />
      <ambientLight intensity={0.4} />
      <RotatingLight />
      <Ground riskLevel={riskLevel} />
      <Forest riskLevel={riskLevel} />
      <MetricsPanel metrics={metrics} riskLevel={riskLevel} />
      <OrbitControls
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        minDistance={5}
        maxDistance={40}
      />
    </Canvas>
  );
};

export default Forest3D;