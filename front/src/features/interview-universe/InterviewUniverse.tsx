import React, { useRef, useState, useCallback, useEffect, useMemo } from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import * as THREE from 'three';
import { useControls } from 'leva';
import { createGalaxyMesh } from './meshes/GalaxyMesh';
import { createStarMesh } from './meshes/StarMesh';
import { createPlanetMesh } from './meshes/PlanetMesh';
import { createSatelliteMesh } from './meshes/SatelliteMesh';
import { ZoomController } from './controllers/ZoomController';
import { WarpDrive } from './navigation/WarpDrive';
import { InfoPanel } from './ui/InfoPanel';
import { Minimap } from './ui/Minimap';
import { TimeMachine } from './ui/TimeMachine';
import { universeApi } from '../../shared/api/universeApi';
import './InterviewUniverse.scss';

interface UniverseNode {
  id: string;
  type: 'galaxy' | 'cluster' | 'company' | 'question';
  name: string;
  x?: number;
  y?: number;
  z?: number;
  size: number;
  color: string;
  metadata: Record<string, any>;
}

interface UniverseLink {
  source: string;
  target: string;
  weight: number;
  type: string;
}

export const InterviewUniverse: React.FC = () => {
  const fgRef = useRef<any>();
  const [graphData, setGraphData] = useState<{ nodes: UniverseNode[], links: UniverseLink[] }>({ 
    nodes: [], 
    links: [] 
  });
  const [zoomLevel, setZoomLevel] = useState(0.1);
  const [selectedNode, setSelectedNode] = useState<UniverseNode | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  
  const zoomController = useMemo(() => new ZoomController(), []);
  const warpDrive = useMemo(() => new WarpDrive(fgRef), []);
  
  // Debug controls
  const controls = useControls({
    showStats: true,
    particleCount: { value: 5000, min: 100, max: 10000, step: 100 },
    starGlow: { value: 0.5, min: 0, max: 1, step: 0.1 },
    autoRotate: false,
    rotationSpeed: { value: 0.001, min: 0, max: 0.01, step: 0.001 }
  });
  
  // Load initial data based on zoom level
  useEffect(() => {
    loadDataForZoomLevel(zoomLevel);
  }, [zoomLevel]);
  
  const loadDataForZoomLevel = async (zoom: number) => {
    try {
      setLoading(true);
      const cameraPos = fgRef.current ? 
        `${fgRef.current.camera().position.x},${fgRef.current.camera().position.y},${fgRef.current.camera().position.z}` 
        : '0,0,0';
      
      const response = await universeApi.getInitialState(zoom, cameraPos);
      setGraphData({
        nodes: response.nodes,
        links: response.links
      });
    } catch (error) {
      console.error('Failed to load universe data:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // Custom node rendering
  const nodeThreeObject = useCallback((node: UniverseNode) => {
    switch(node.type) {
      case 'galaxy':
        return createGalaxyMesh(node, controls.particleCount);
      case 'cluster':
        return createStarMesh(node, controls.starGlow);
      case 'company':
        return createPlanetMesh(node);
      case 'question':
        return createSatelliteMesh(node);
      default:
        const geometry = new THREE.SphereGeometry(node.size);
        const material = new THREE.MeshBasicMaterial({ color: node.color });
        return new THREE.Mesh(geometry, material);
    }
  }, [controls.particleCount, controls.starGlow]);
  
  // Handle node click
  const handleNodeClick = useCallback((node: UniverseNode) => {
    setSelectedNode(node);
    
    // Focus camera on node
    const distance = 40;
    const distRatio = 1 + distance / Math.hypot(node.x!, node.y!, node.z!);
    
    fgRef.current.cameraPosition(
      { 
        x: node.x! * distRatio, 
        y: node.y! * distRatio, 
        z: node.z! * distRatio 
      },
      node,
      3000
    );
    
    // Load detailed data for node
    loadNodeDetails(node);
  }, []);
  
  const loadNodeDetails = async (node: UniverseNode) => {
    if (node.type === 'galaxy') {
      // Load clusters for this galaxy
      const clusters = await universeApi.getClustersByCategory(node.metadata.category_id);
      // Merge with existing nodes
      setGraphData(prev => ({
        ...prev,
        nodes: [...prev.nodes, ...clusters.nodes]
      }));
    }
  };
  
  // Handle zoom changes
  const handleZoomChange = useCallback((zoom: number) => {
    setZoomLevel(zoom);
    zoomController.handleZoomChange(zoom, fgRef.current?.camera().position);
  }, [zoomController]);
  
  // Semantic search navigation
  const handleSearch = useCallback(async () => {
    if (searchQuery) {
      await warpDrive.warpTo(searchQuery);
      setSearchQuery('');
    }
  }, [searchQuery, warpDrive]);
  
  // Auto-rotation
  useEffect(() => {
    if (controls.autoRotate && fgRef.current) {
      const interval = setInterval(() => {
        fgRef.current.scene().rotation.y += controls.rotationSpeed;
      }, 16);
      return () => clearInterval(interval);
    }
  }, [controls.autoRotate, controls.rotationSpeed]);
  
  if (loading) {
    return (
      <div className="universe-loading">
        <div className="loading-spinner">
          <div className="spinner-orbit"></div>
          <div className="spinner-text">Initializing Universe...</div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="interview-universe">
      <div className="universe-container">
        <ForceGraph3D
          ref={fgRef}
          graphData={graphData}
          nodeThreeObject={nodeThreeObject}
          nodeLabel="name"
          onNodeClick={handleNodeClick}
          onZoom={handleZoomChange}
          enableNodeDrag={false}
          showNavInfo={false}
          backgroundColor="#000011"
          width={window.innerWidth}
          height={window.innerHeight}
          nodeOpacity={0.9}
          linkOpacity={0.6}
          linkWidth={link => Math.sqrt(link.weight) * 0.5}
          linkColor={() => '#4a9eff'}
        />
      </div>
      
      {/* UI Overlays */}
      <div className="universe-ui">
        {/* Search / Warp Drive */}
        <div className="warp-drive-panel">
          <input
            type="text"
            placeholder="Enter question to navigate..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            className="warp-input"
          />
          <button onClick={handleSearch} className="warp-button">
            <span className="warp-icon">🚀</span> Warp
          </button>
        </div>
        
        {/* Info Panel */}
        {selectedNode && (
          <InfoPanel 
            node={selectedNode} 
            onClose={() => setSelectedNode(null)}
          />
        )}
        
        {/* Minimap */}
        <Minimap 
          nodes={graphData.nodes}
          currentPosition={fgRef.current?.camera().position}
          onNavigate={(pos) => {
            fgRef.current?.cameraPosition(pos, null, 1000);
          }}
        />
        
        {/* Time Machine */}
        <TimeMachine 
          onTimeChange={(date) => {
            console.log('Time travel to:', date);
            // Reload data for specific time period
          }}
        />
        
        {/* Stats */}
        {controls.showStats && (
          <div className="universe-stats">
            <div>Nodes: {graphData.nodes.length}</div>
            <div>Links: {graphData.links.length}</div>
            <div>Zoom: {zoomLevel.toFixed(2)}</div>
            <div>Level: {zoomLevel < 0.3 ? 'Galaxies' : 
                        zoomLevel < 0.7 ? 'Clusters' :
                        zoomLevel < 1.5 ? 'Companies' : 'Questions'}</div>
          </div>
        )}
      </div>
    </div>
  );
};