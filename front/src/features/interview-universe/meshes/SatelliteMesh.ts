import * as THREE from 'three';

interface UniverseNode {
  id: string;
  name: string;
  size: number;
  color: string;
  metadata: Record<string, any>;
}

export function createSatelliteMesh(node: UniverseNode): THREE.Object3D {
  const group = new THREE.Group();
  
  // Small spherical satellite
  const satelliteGeometry = new THREE.OctahedronGeometry(node.size, 0);
  const satelliteMaterial = new THREE.MeshPhongMaterial({
    color: node.color,
    emissive: node.color,
    emissiveIntensity: 0.3,
    flatShading: true
  });
  const satellite = new THREE.Mesh(satelliteGeometry, satelliteMaterial);
  
  // Glow effect based on importance
  const glowIntensity = node.metadata?.glow_intensity || 0.5;
  const glowGeometry = new THREE.SphereGeometry(node.size * 1.5, 8, 8);
  const glowMaterial = new THREE.MeshBasicMaterial({
    color: node.color,
    transparent: true,
    opacity: 0.3 * glowIntensity,
    side: THREE.BackSide
  });
  const glow = new THREE.Mesh(glowGeometry, glowMaterial);
  
  // Orbital ring indicator
  const ringGeometry = new THREE.TorusGeometry(node.size * 2, 0.02, 4, 32);
  const ringMaterial = new THREE.MeshBasicMaterial({
    color: node.color,
    transparent: true,
    opacity: 0.3
  });
  const ring = new THREE.Mesh(ringGeometry, ringMaterial);
  ring.rotation.x = Math.PI / 2;
  
  // Data stream particles (representing question connections)
  if (node.metadata?.cluster_id) {
    const dataStream = createDataStream(node.size, node.color);
    group.add(dataStream);
  }
  
  // Rotation and pulsing animation
  satellite.userData.update = () => {
    const time = Date.now() * 0.001;
    
    // Rotation
    satellite.rotation.x += 0.01;
    satellite.rotation.y += 0.02;
    
    // Pulsing glow
    const pulse = 1 + Math.sin(time * 3) * 0.1;
    glow.scale.setScalar(pulse);
    
    // Ring rotation
    ring.rotation.z += 0.005;
  };
  
  group.add(satellite);
  group.add(glow);
  group.add(ring);
  
  // Store metadata
  group.userData = {
    nodeId: node.id,
    nodeName: node.name,
    nodeType: 'question',
    metadata: node.metadata
  };
  
  return group;
}

function createDataStream(satelliteSize: number, color: string): THREE.Points {
  const particleCount = 20;
  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array(particleCount * 3);
  const opacities = new Float32Array(particleCount);
  
  for (let i = 0; i < particleCount; i++) {
    // Create trailing particles
    const distance = i * satelliteSize * 0.3;
    positions[i * 3] = -distance;
    positions[i * 3 + 1] = 0;
    positions[i * 3 + 2] = 0;
    
    // Fade out trail
    opacities[i] = 1 - (i / particleCount);
  }
  
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute('opacity', new THREE.BufferAttribute(opacities, 1));
  
  const material = new THREE.PointsMaterial({
    color: color,
    size: 0.05,
    transparent: true,
    opacity: 0.6,
    blending: THREE.AdditiveBlending,
    vertexColors: false
  });
  
  const dataStream = new THREE.Points(geometry, material);
  
  // Animation for data flow
  dataStream.userData.update = () => {
    const positions = geometry.attributes.position.array as Float32Array;
    
    // Move particles along trail
    for (let i = particleCount - 1; i > 0; i--) {
      positions[i * 3] = positions[(i - 1) * 3];
    }
    
    // Reset first particle
    positions[0] = 0;
    
    geometry.attributes.position.needsUpdate = true;
  };
  
  return dataStream;
}