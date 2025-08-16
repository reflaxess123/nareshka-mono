import React from 'react';
import './InfoPanel.scss';

interface UniverseNode {
  id: string;
  type: string;
  name: string;
  metadata: Record<string, any>;
}

interface InfoPanelProps {
  node: UniverseNode;
  onClose: () => void;
}

export const InfoPanel: React.FC<InfoPanelProps> = ({ node, onClose }) => {
  return (
    <div className="info-panel">
      <div className="info-panel-header">
        <h3>{node.name}</h3>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>
      
      <div className="info-panel-content">
        <div className="info-type">
          <span className="label">Type:</span>
          <span className="value">{node.type}</span>
        </div>
        
        {node.type === 'galaxy' && (
          <>
            <div className="info-stat">
              <span className="label">Questions:</span>
              <span className="value">{node.metadata.questions_count || 0}</span>
            </div>
            <div className="info-stat">
              <span className="label">Clusters:</span>
              <span className="value">{node.metadata.clusters_count || 0}</span>
            </div>
            <div className="info-stat">
              <span className="label">Coverage:</span>
              <span className="value">{node.metadata.percentage || 0}%</span>
            </div>
          </>
        )}
        
        {node.type === 'cluster' && (
          <>
            <div className="info-stat">
              <span className="label">Questions:</span>
              <span className="value">{node.metadata.questions_count || 0}</span>
            </div>
            <div className="info-stat">
              <span className="label">Difficulty:</span>
              <span className="value">{node.metadata.temperature || 5}/10</span>
            </div>
            <div className="info-stat">
              <span className="label">Importance:</span>
              <span className="value">{node.metadata.mass?.toFixed(2) || 0}</span>
            </div>
          </>
        )}
        
        {node.type === 'company' && (
          <>
            <div className="info-stat">
              <span className="label">Questions:</span>
              <span className="value">{node.metadata.question_count || 0}</span>
            </div>
            <div className="info-stat">
              <span className="label">Categories:</span>
              <span className="value">{node.metadata.categories?.length || 0}</span>
            </div>
          </>
        )}
        
        {node.type === 'question' && (
          <>
            <div className="info-text">
              <span className="label">Full Text:</span>
              <p className="question-text">{node.metadata.full_text || node.name}</p>
            </div>
            <div className="info-stat">
              <span className="label">Company:</span>
              <span className="value">{node.metadata.company || 'Unknown'}</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
};