import * as THREE from 'three';

interface UniverseNode {
  id: string;
  name: string;
  size: number;
  color: string;
  metadata: Record<string, any>;
}

export function createGalaxyMesh(node: UniverseNode, particleCount: number = 5000): THREE.Object3D {
  const group = new THREE.Group();
  
  // Central core of the galaxy
  const coreGeometry = new THREE.SphereGeometry(node.size, 32, 32);
  const coreMaterial = new THREE.MeshPhongMaterial({
    color: node.color,
    emissive: node.color,
    emissiveIntensity: 0.5,
    transparent: true,
    opacity: 0.8
  });
  const core = new THREE.Mesh(coreGeometry, coreMaterial);
  
  // Add glow effect to core
  const glowGeometry = new THREE.SphereGeometry(node.size * 1.5, 32, 32);
  const glowMaterial = new THREE.MeshBasicMaterial({
    color: node.color,
    transparent: true,
    opacity: 0.2,
    side: THREE.BackSide
  });
  const glow = new THREE.Mesh(glowGeometry, glowMaterial);
  
  // Spiral arms particle system
  const particlesGeometry = new THREE.BufferGeometry();
  const positions = new Float32Array(particleCount * 3);
  const colors = new Float32Array(particleCount * 3);
  const sizes = new Float32Array(particleCount);
  
  const color = new THREE.Color(node.color);
  const armCount = 3; // Number of spiral arms
  
  for(let i = 0; i < particleCount; i++) {
    // Create spiral pattern
    const armIndex = i % armCount;
    const armOffset = (armIndex / armCount) * Math.PI * 2;
    const distance = Math.sqrt(i / particleCount) * node.size * 8;
    const angle = (i / particleCount) * Math.PI * 10 + armOffset;
    
    // Add some randomness for natural look
    const randomRadius = distance + (Math.random() - 0.5) * node.size;
    const randomHeight = (Math.random() - 0.5) * node.size * 0.5;
    
    positions[i * 3] = Math.cos(angle) * randomRadius;
    positions[i * 3 + 1] = randomHeight;
    positions[i * 3 + 2] = Math.sin(angle) * randomRadius;
    
    // Color variation
    const brightness = 0.5 + Math.random() * 0.5;
    colors[i * 3] = color.r * brightness;
    colors[i * 3 + 1] = color.g * brightness;
    colors[i * 3 + 2] = color.b * brightness;
    
    // Size variation (smaller particles at edges)
    sizes[i] = Math.max(0.1, (1 - distance / (node.size * 8)) * 0.5);
  }
  
  particlesGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  particlesGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  particlesGeometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
  
  const particlesMaterial = new THREE.PointsMaterial({
    size: 0.3,
    vertexColors: true,
    transparent: true,
    opacity: 0.6,
    blending: THREE.AdditiveBlending,
    sizeAttenuation: true
  });
  
  const particles = new THREE.Points(particlesGeometry, particlesMaterial);
  
  // Add rotation animation
  particles.userData.update = () => {
    particles.rotation.y += 0.001;
  };
  
  // Assemble galaxy
  group.add(core);
  group.add(glow);
  group.add(particles);
  
  // Store metadata
  group.userData = {
    nodeId: node.id,
    nodeName: node.name,
    nodeType: 'galaxy',
    metadata: node.metadata
  };
  
  return group;
}