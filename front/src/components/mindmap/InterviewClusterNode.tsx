import React from 'react';
import { Handle, Position } from '@xyflow/react';
import styles from './InterviewClusterNode.module.scss';

interface InterviewClusterNodeData {
  id: number;
  name: string;
  questionsCount: number;
  keywords?: string[];
  exampleQuestion?: string;
}

interface InterviewClusterNodeProps {
  data: InterviewClusterNodeData;
}

const InterviewClusterNode: React.FC<InterviewClusterNodeProps> = ({ data }) => {
  // Цвет узла в зависимости от размера кластера
  const getNodeColor = (count: number) => {
    if (count >= 100) return '#f87171'; // красный для больших
    if (count >= 50) return '#fb923c';  // оранжевый для средних
    if (count >= 25) return '#fbbf24';  // желтый
    return '#a3e635';                    // зеленый для маленьких
  };

  const nodeColor = getNodeColor(data.questionsCount);

  return (
    <div 
      className={styles.clusterNode}
      style={{
        background: `linear-gradient(135deg, ${nodeColor}20 0%, ${nodeColor}10 100%)`,
        borderColor: nodeColor,
      }}
    >
      <Handle type="target" position={Position.Top} />
      
      <div className={styles.clusterHeader}>
        <h4 className={styles.clusterName}>
          {data.name}
        </h4>
        <span 
          className={styles.questionCount}
          style={{ backgroundColor: nodeColor }}
        >
          {data.questionsCount}
        </span>
      </div>

      {data.keywords && data.keywords.length > 0 && (
        <div className={styles.keywords}>
          {data.keywords.slice(0, 3).map((keyword, idx) => (
            <span key={idx} className={styles.keyword}>
              {keyword}
            </span>
          ))}
        </div>
      )}

      {data.exampleQuestion && (
        <div className={styles.exampleQuestion} title={data.exampleQuestion}>
          {data.exampleQuestion.length > 80 
            ? data.exampleQuestion.substring(0, 80) + '...'
            : data.exampleQuestion
          }
        </div>
      )}
      
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
};

export default InterviewClusterNode;