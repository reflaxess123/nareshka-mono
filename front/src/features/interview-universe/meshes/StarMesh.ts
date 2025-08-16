import * as THREE from 'three';

interface UniverseNode {
  id: string;
  name: string;
  size: number;
  color: string;
  metadata: Record<string, any>;
}

export function createStarMesh(node: UniverseNode, glowIntensity: number = 0.5): THREE.Object3D {
  const group = new THREE.Group();
  
  // Temperature-based color (from metadata)
  const temperature = node.metadata?.temperature || 5;
  const starColor = getStarColorByTemperature(temperature);
  
  // Main star sphere
  const starGeometry = new THREE.SphereGeometry(node.size, 24, 24);
  const starMaterial = new THREE.MeshPhongMaterial({
    color: starColor,
    emissive: starColor,
    emissiveIntensity: 0.7,
    shininess: 100
  });
  const star = new THREE.Mesh(starGeometry, starMaterial);
  
  // Corona effect (larger transparent sphere)
  const coronaGeometry = new THREE.SphereGeometry(node.size * 2, 16, 16);
  const coronaMaterial = new THREE.MeshBasicMaterial({
    color: starColor,
    transparent: true,
    opacity: 0.15 * glowIntensity,
    side: THREE.BackSide
  });
  const corona = new THREE.Mesh(coronaGeometry, coronaMaterial);
  
  // Lens flare effect using sprites
  const flareTexture = createFlareTexture();
  const flareMaterial = new THREE.SpriteMaterial({
    map: flareTexture,
    color: starColor,
    blending: THREE.AdditiveBlending,
    opacity: 0.6 * glowIntensity
  });
  const flare = new THREE.Sprite(flareMaterial);
  flare.scale.set(node.size * 4, node.size * 4, 1);
  
  // Pulsing animation
  star.userData.update = () => {
    const time = Date.now() * 0.001;
    const pulse = 1 + Math.sin(time * 2) * 0.05;
    star.scale.setScalar(pulse);
    corona.scale.setScalar(pulse * 1.1);
  };
  
  // Add particle field around important stars
  if (node.metadata?.questions_count > 50) {
    const particleField = createStarParticleField(node.size, starColor);
    group.add(particleField);
  }
  
  group.add(star);
  group.add(corona);
  group.add(flare);
  
  // Store metadata
  group.userData = {
    nodeId: node.id,
    nodeName: node.name,
    nodeType: 'cluster',
    temperature: temperature,
    metadata: node.metadata
  };
  
  return group;
}

function getStarColorByTemperature(temperature: number): string {
  // Map temperature (1-10) to star colors
  const colors = [
    '#87CEEB', // 1 - Cool blue
    '#00BFFF', // 2 - Deep sky blue
    '#1E90FF', // 3 - Dodger blue
    '#00FF00', // 4 - Green
    '#ADFF2F', // 5 - Green yellow
    '#FFFF00', // 6 - Yellow
    '#FFD700', // 7 - Gold
    '#FFA500', // 8 - Orange
    '#FF4500', // 9 - Orange red
    '#FF0000'  // 10 - Red (hottest/hardest)
  ];
  
  const index = Math.max(0, Math.min(9, temperature - 1));
  return colors[index];
}

function createFlareTexture(): THREE.Texture {
  const canvas = document.createElement('canvas');
  canvas.width = 256;
  canvas.height = 256;
  const context = canvas.getContext('2d')!;
  
  // Create radial gradient
  const gradient = context.createRadialGradient(128, 128, 0, 128, 128, 128);
  gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
  gradient.addColorStop(0.2, 'rgba(255, 255, 255, 0.8)');
  gradient.addColorStop(0.4, 'rgba(255, 255, 200, 0.6)');
  gradient.addColorStop(0.6, 'rgba(255, 255, 150, 0.4)');
  gradient.addColorStop(0.8, 'rgba(255, 255, 100, 0.2)');
  gradient.addColorStop(1, 'rgba(255, 255, 50, 0)');
  
  context.fillStyle = gradient;
  context.fillRect(0, 0, 256, 256);
  
  const texture = new THREE.CanvasTexture(canvas);
  texture.needsUpdate = true;
  
  return texture;
}

function createStarParticleField(starSize: number, color: string): THREE.Points {
  const particleCount = 100;
  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array(particleCount * 3);
  
  for (let i = 0; i < particleCount; i++) {
    // Random position in sphere around star
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    const radius = starSize * (3 + Math.random() * 2);
    
    positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
    positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
    positions[i * 3 + 2] = radius * Math.cos(phi);
  }
  
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  
  const material = new THREE.PointsMaterial({
    color: color,
    size: 0.05,
    transparent: true,
    opacity: 0.4,
    blending: THREE.AdditiveBlending
  });
  
  const particles = new THREE.Points(geometry, material);
  
  // Rotation animation
  particles.userData.update = () => {
    particles.rotation.y += 0.002;
  };
  
  return particles;
}