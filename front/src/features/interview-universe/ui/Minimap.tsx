import React, { useRef, useEffect } from 'react';
import './Minimap.scss';

interface MinimapProps {
  nodes: any[];
  currentPosition?: any;
  onNavigate: (position: { x: number; y: number; z: number }) => void;
}

export const Minimap: React.FC<MinimapProps> = ({ nodes, currentPosition, onNavigate }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw background
    ctx.fillStyle = 'rgba(0, 0, 17, 0.9)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw nodes
    nodes.forEach(node => {
      if (node.type === 'galaxy') {
        // Project 3D to 2D
        const x = (node.x / 400 + 0.5) * canvas.width;
        const y = (node.z / 400 + 0.5) * canvas.height;
        
        ctx.fillStyle = node.color || '#4a9eff';
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, Math.PI * 2);
        ctx.fill();
      }
    });
    
    // Draw current position
    if (currentPosition) {
      const x = (currentPosition.x / 400 + 0.5) * canvas.width;
      const y = (currentPosition.z / 400 + 0.5) * canvas.height;
      
      ctx.strokeStyle = '#00ff00';
      ctx.lineWidth = 2;
      ctx.strokeRect(x - 10, y - 10, 20, 20);
    }
  }, [nodes, currentPosition]);
  
  const handleClick = (e: React.MouseEvent) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / canvas.width - 0.5) * 400;
    const z = ((e.clientY - rect.top) / canvas.height - 0.5) * 400;
    
    onNavigate({ x, y: 0, z });
  };
  
  return (
    <div className="minimap">
      <div className="minimap-title">Navigation Map</div>
      <canvas
        ref={canvasRef}
        width={200}
        height={200}
        onClick={handleClick}
        className="minimap-canvas"
      />
    </div>
  );
};