import * as THREE from 'three';

interface UniverseNode {
  id: string;
  name: string;
  size: number;
  color: string;
  metadata: Record<string, any>;
}

export function createPlanetMesh(node: UniverseNode): THREE.Object3D {
  const group = new THREE.Group();
  
  // Main planet sphere with texture
  const planetGeometry = new THREE.SphereGeometry(node.size, 32, 32);
  
  // Create procedural planet texture
  const planetTexture = createPlanetTexture(node.color);
  
  const planetMaterial = new THREE.MeshPhongMaterial({
    map: planetTexture,
    bumpMap: planetTexture,
    bumpScale: 0.05,
    specularMap: planetTexture,
    specular: new THREE.Color('#333333'),
    shininess: 5
  });
  
  const planet = new THREE.Mesh(planetGeometry, planetMaterial);
  
  // Atmosphere
  const atmosphereGeometry = new THREE.SphereGeometry(node.size * 1.1, 32, 32);
  const atmosphereMaterial = new THREE.MeshPhongMaterial({
    color: node.color,
    transparent: true,
    opacity: 0.1,
    side: THREE.BackSide
  });
  const atmosphere = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial);
  
  // Rings for companies with many questions
  if (node.metadata?.questions_count > 100) {
    const rings = createPlanetRings(node.size, node.color);
    group.add(rings);
  }
  
  // Cloud layer
  const cloudGeometry = new THREE.SphereGeometry(node.size * 1.02, 32, 32);
  const cloudMaterial = new THREE.MeshPhongMaterial({
    map: createCloudTexture(),
    transparent: true,
    opacity: 0.3,
    depthWrite: false
  });
  const clouds = new THREE.Mesh(cloudGeometry, cloudMaterial);
  
  // Rotation animations
  planet.userData.update = () => {
    planet.rotation.y += 0.002;
    clouds.rotation.y += 0.003;
    clouds.rotation.x += 0.0005;
  };
  
  // City lights on dark side (represents activity)
  if (node.metadata?.recent_activity) {
    const cityLights = createCityLights(node.size);
    group.add(cityLights);
  }
  
  group.add(planet);
  group.add(atmosphere);
  group.add(clouds);
  
  // Store metadata
  group.userData = {
    nodeId: node.id,
    nodeName: node.name,
    nodeType: 'company',
    metadata: node.metadata
  };
  
  return group;
}

function createPlanetTexture(baseColor: string): THREE.Texture {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 256;
  const ctx = canvas.getContext('2d')!;
  
  // Base color
  const color = new THREE.Color(baseColor);
  ctx.fillStyle = `rgb(${color.r * 255}, ${color.g * 255}, ${color.b * 255})`;
  ctx.fillRect(0, 0, 512, 256);
  
  // Add some surface features
  for (let i = 0; i < 50; i++) {
    const x = Math.random() * 512;
    const y = Math.random() * 256;
    const radius = Math.random() * 20 + 5;
    const opacity = Math.random() * 0.3;
    
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(${Math.random() * 100}, ${Math.random() * 100}, ${Math.random() * 100}, ${opacity})`;
    ctx.fill();
  }
  
  // Add some bands
  for (let i = 0; i < 5; i++) {
    const y = Math.random() * 256;
    const height = Math.random() * 20 + 5;
    const opacity = Math.random() * 0.2;
    
    ctx.fillStyle = `rgba(255, 255, 255, ${opacity})`;
    ctx.fillRect(0, y, 512, height);
  }
  
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  
  return texture;
}

function createCloudTexture(): THREE.Texture {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 256;
  const ctx = canvas.getContext('2d')!;
  
  // Create cloud pattern
  ctx.fillStyle = 'transparent';
  ctx.fillRect(0, 0, 512, 256);
  
  for (let i = 0; i < 100; i++) {
    const x = Math.random() * 512;
    const y = Math.random() * 256;
    const radius = Math.random() * 30 + 10;
    
    const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
    gradient.addColorStop(0, 'rgba(255, 255, 255, 0.4)');
    gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
    
    ctx.fillStyle = gradient;
    ctx.fillRect(x - radius, y - radius, radius * 2, radius * 2);
  }
  
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  
  return texture;
}

function createPlanetRings(planetSize: number, color: string): THREE.Mesh {
  const innerRadius = planetSize * 1.5;
  const outerRadius = planetSize * 2.5;
  
  const geometry = new THREE.RingGeometry(innerRadius, outerRadius, 64);
  
  // Create ring texture
  const canvas = document.createElement('canvas');
  canvas.width = 256;
  canvas.height = 64;
  const ctx = canvas.getContext('2d')!;
  
  const gradient = ctx.createLinearGradient(0, 0, 256, 0);
  const ringColor = new THREE.Color(color);
  
  gradient.addColorStop(0, `rgba(${ringColor.r * 255}, ${ringColor.g * 255}, ${ringColor.b * 255}, 0.1)`);
  gradient.addColorStop(0.5, `rgba(${ringColor.r * 255}, ${ringColor.g * 255}, ${ringColor.b * 255}, 0.6)`);
  gradient.addColorStop(1, `rgba(${ringColor.r * 200}, ${ringColor.g * 200}, ${ringColor.b * 200}, 0.1)`);
  
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 256, 64);
  
  const ringTexture = new THREE.CanvasTexture(canvas);
  
  const material = new THREE.MeshBasicMaterial({
    map: ringTexture,
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.7
  });
  
  const rings = new THREE.Mesh(geometry, material);
  rings.rotation.x = Math.PI / 2;
  
  return rings;
}

function createCityLights(planetSize: number): THREE.Points {
  const lightCount = 200;
  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array(lightCount * 3);
  const colors = new Float32Array(lightCount * 3);
  
  for (let i = 0; i < lightCount; i++) {
    // Place lights on planet surface
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    const radius = planetSize * 1.01;
    
    positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
    positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
    positions[i * 3 + 2] = radius * Math.cos(phi);
    
    // Warm yellow/orange lights
    colors[i * 3] = 1;
    colors[i * 3 + 1] = 0.8 + Math.random() * 0.2;
    colors[i * 3 + 2] = 0.4 + Math.random() * 0.2;
  }
  
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  
  const material = new THREE.PointsMaterial({
    size: 0.02,
    vertexColors: true,
    transparent: true,
    opacity: 0.8,
    blending: THREE.AdditiveBlending
  });
  
  return new THREE.Points(geometry, material);
}