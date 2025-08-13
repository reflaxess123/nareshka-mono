import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import styles from './ClusterConstellation.module.scss';

interface ClusterNode {
  id: number;
  name: string;
  category_id: string;
  category_name: string;
  questions_count: number;
  interview_penetration: number;
  keywords: string[];
  example_question: string;
  size: number;
  // D3 добавит эти поля
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
}

interface ClusterLink {
  source: number | ClusterNode;
  target: number | ClusterNode;
  weight: number;
  strength: number;
}

interface ConstellationData {
  nodes: ClusterNode[];
  links: ClusterLink[];
  categories: Record<string, string>;
  stats: {
    total_clusters: number;
    total_links: number;
    avg_penetration: number;
    max_cluster_size: number;
    strongest_link: number;
  };
}

const categoryColors: Record<string, string> = {
  'javascript_core': '#f7df1e',
  'react': '#61dafb',
  'typescript': '#3178c6',
  'soft_skills': '#ff6b6b',
  'алгоритмы': '#dc143c',
  'сет': '#ff6b35',
  'верстка': '#e91e63',
  'браузеры': '#9c27b0',
  'архитектура': '#673ab7',
  'инструменты': '#3f51b5',
  'производителност': '#00bcd4',
  'тестирование': '#4caf50',
  'другое': '#9e9e9e'
};

export const ClusterConstellation: React.FC = () => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [data, setData] = useState<ConstellationData | null>(null);
  const [selectedNode, setSelectedNode] = useState<ClusterNode | null>(null);
  const [hoveredNode, setHoveredNode] = useState<ClusterNode | null>(null);
  const [loading, setLoading] = useState(true);
  const [dimensions, setDimensions] = useState({ width: 1200, height: 800 });
  const [needsReset, setNeedsReset] = useState(false);

  // Загрузка данных
  useEffect(() => {
    fetch('/api/v2/cluster-visualization/constellation')
      .then(res => res.json())
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  // Обновление размеров при ресайзе
  useEffect(() => {
    const handleResize = () => {
      const container = svgRef.current?.parentElement;
      if (container) {
        setDimensions({
          width: container.clientWidth,
          height: container.clientHeight || 800
        });
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Функция сброса позиций
  const resetPositions = () => {
    setNeedsReset(true);
  };

  // D3 визуализация
  useEffect(() => {
    if (!data || !svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const { width, height } = dimensions;

    // Создаем группы для слоев
    const g = svg.append('g');
    const linksGroup = g.append('g').attr('class', 'links');
    const nodesGroup = g.append('g').attr('class', 'nodes');
    const labelsGroup = g.append('g').attr('class', 'labels');

    // Zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.5, 3])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);

    // Force simulation - с быстрой остановкой
    const simulation = d3.forceSimulation<ClusterNode>(data.nodes)
      .force('link', d3.forceLink<ClusterNode, ClusterLink>(data.links)
        .id(d => d.id)
        .distance(200) // Фиксированное расстояние
        .strength(0.5))
      .force('charge', d3.forceManyBody()
        .strength(-800) // Сильное отталкивание для четкости
        .distanceMax(500))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide<ClusterNode>()
        .radius(d => 30 + Math.sqrt(d.questions_count) * 2)
        .strength(1))
      .force('x', d3.forceX(width / 2).strength(0.1))
      .force('y', d3.forceY(height / 2).strength(0.1))
      .velocityDecay(0.3) // Быстрое затухание
      .alphaDecay(0.05); // Быстрая остановка симуляции

    // Создаем линии связей - более наглядные
    const links = linksGroup.selectAll('line')
      .data(data.links)
      .join('line')
      .attr('stroke', '#61dafb')
      .attr('stroke-opacity', d => 0.3 + d.strength * 0.6) // Более видимые связи
      .attr('stroke-width', d => Math.max(1, d.strength * 4))
      .style('filter', 'drop-shadow(0 0 3px rgba(97, 218, 251, 0.4))');

    // Создаем узлы
    const nodes = nodesGroup.selectAll('g')
      .data(data.nodes)
      .join('g')
      .attr('class', 'node')
      .call(drag(simulation) as any);

    // Круги для узлов - более крупные и четкие
    nodes.append('circle')
      .attr('r', d => Math.max(15, 20 + Math.sqrt(d.questions_count) * 1.5)) // Больше размер
      .attr('fill', d => categoryColors[d.category_id] || '#999')
      .attr('stroke', '#ffffff')
      .attr('stroke-width', 3)
      .style('cursor', 'pointer')
      .style('filter', d => `drop-shadow(0 0 10px ${categoryColors[d.category_id] || '#999'})`);

    // Дополнительное кольцо для популярных кластеров (без анимации)
    nodes.filter(d => d.interview_penetration > 10)
      .append('circle')
      .attr('r', d => Math.max(15, 20 + Math.sqrt(d.questions_count) * 1.5) + 5)
      .attr('fill', 'none')
      .attr('stroke', d => categoryColors[d.category_id] || '#999')
      .attr('stroke-width', 1)
      .attr('opacity', 0.6)
      .style('pointer-events', 'none');

    // Лейблы для узлов - более читаемые
    const labels = labelsGroup.selectAll('text')
      .data(data.nodes)
      .join('text')
      .text(d => d.name.length > 25 ? d.name.substring(0, 22) + '...' : d.name)
      .attr('font-size', d => Math.max(11, 12 + d.size * 3)) // Меньше разброс размеров
      .attr('font-weight', 'bold')
      .attr('fill', '#ffffff')
      .attr('text-anchor', 'middle')
      .attr('dy', d => -(Math.max(15, 20 + Math.sqrt(d.questions_count) * 1.5) + 8))
      .style('pointer-events', 'none')
      .style('user-select', 'none')
      .style('text-shadow', '2px 2px 4px rgba(0,0,0,0.8)');

    // Интерактивность
    nodes
      .on('mouseover', function(event, d) {
        setHoveredNode(d);
        // Подсвечиваем связанные узлы
        const connectedNodeIds = new Set<number>();
        data.links.forEach(link => {
          const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
          const targetId = typeof link.target === 'object' ? link.target.id : link.target;
          if (sourceId === d.id) connectedNodeIds.add(targetId as number);
          if (targetId === d.id) connectedNodeIds.add(sourceId as number);
        });

        nodes.style('opacity', n => 
          n.id === d.id || connectedNodeIds.has(n.id) ? 1 : 0.3
        );
        links.style('opacity', l => {
          const sourceId = typeof l.source === 'object' ? l.source.id : l.source;
          const targetId = typeof l.target === 'object' ? l.target.id : l.target;
          return sourceId === d.id || targetId === d.id ? 1 : 0.1;
        });
        labels.style('opacity', n => 
          n.id === d.id || connectedNodeIds.has(n.id) ? 1 : 0.3
        );
      })
      .on('mouseout', function() {
        setHoveredNode(null);
        nodes.style('opacity', 1);
        links.style('opacity', d => 0.2 + d.strength * 0.5);
        labels.style('opacity', 1);
      })
      .on('click', function(event, d) {
        event.stopPropagation();
        setSelectedNode(d);
      });

    // Click на фон для сброса выделения
    svg.on('click', () => setSelectedNode(null));

    // Обновление позиций при симуляции - с автостопом
    let tickCount = 0;
    simulation.on('tick', () => {
      tickCount++;
      
      links
        .attr('x1', d => (d.source as ClusterNode).x!)
        .attr('y1', d => (d.source as ClusterNode).y!)
        .attr('x2', d => (d.target as ClusterNode).x!)
        .attr('y2', d => (d.target as ClusterNode).y!);

      nodes.attr('transform', d => `translate(${d.x},${d.y})`);
      labels.attr('x', d => d.x!).attr('y', d => d.y!);

      // Автостоп после 300 тиков или когда alpha очень маленький
      if (tickCount > 300 || simulation.alpha() < 0.01) {
        simulation.stop();
      }
    });

    // Drag behavior - без перезапуска симуляции
    function drag(simulation: d3.Simulation<ClusterNode, undefined>) {
      function dragstarted(event: any, d: ClusterNode) {
        // НЕ перезапускаем симуляцию - просто фиксируем узел
        d.fx = d.x;
        d.fy = d.y;
      }

      function dragged(event: any, d: ClusterNode) {
        d.fx = event.x;
        d.fy = event.y;
        
        // Обновляем позиции без симуляции
        d.x = event.x;
        d.y = event.y;
        
        // Обновляем визуально
        d3.select(event.sourceEvent.target.parentNode).attr('transform', `translate(${d.x},${d.y})`);
        
        // Обновляем связанные линии
        links
          .filter(l => (l.source as ClusterNode).id === d.id || (l.target as ClusterNode).id === d.id)
          .attr('x1', l => (l.source as ClusterNode).x!)
          .attr('y1', l => (l.source as ClusterNode).y!)
          .attr('x2', l => (l.target as ClusterNode).x!)
          .attr('y2', l => (l.target as ClusterNode).y!);
        
        // Обновляем лейбл
        labels
          .filter(n => n.id === d.id)
          .attr('x', d.x!)
          .attr('y', d.y!);
      }

      function dragended(event: any, d: ClusterNode) {
        // НЕ отпускаем фиксацию - узел остается на новом месте
        // d.fx = null;
        // d.fy = null;
      }

      return d3.drag<SVGGElement, ClusterNode>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended);
    }

    // Обработка сброса позиций
    if (needsReset) {
      data.nodes.forEach(node => {
        node.fx = null;
        node.fy = null;
      });
      simulation.alpha(1).restart();
      tickCount = 0;
      setNeedsReset(false);
    }

    return () => {
      simulation.stop();
    };
  }, [data, dimensions, needsReset]);

  if (loading) {
    return <div className={styles.loading}>Загрузка созвездия кластеров...</div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2>🌌 Созвездие кластеров</h2>
        <div className={styles.controls}>
          <button className={styles.resetButton} onClick={resetPositions}>
            🔄 Сбросить позиции
          </button>
        </div>
        <div className={styles.stats}>
          <span>Кластеров: {data?.stats.total_clusters}</span>
          <span>Связей: {data?.stats.total_links}</span>
          <span>Средняя популярность: {data?.stats.avg_penetration.toFixed(1)}%</span>
        </div>
      </div>

      <div className={styles.visualization}>
        <svg ref={svgRef} width={dimensions.width} height={dimensions.height} />
        
        {hoveredNode && (
          <div className={styles.tooltip}>
            <h3>{hoveredNode.name}</h3>
            <p className={styles.category}>{hoveredNode.category_name}</p>
            <p>Вопросов: {hoveredNode.questions_count}</p>
            <p>Появляется в {hoveredNode.interview_penetration.toFixed(1)}% интервью</p>
            <div className={styles.keywords}>
              {hoveredNode.keywords.slice(0, 5).map(k => (
                <span key={k} className={styles.keyword}>{k}</span>
              ))}
            </div>
          </div>
        )}

        {selectedNode && (
          <div className={styles.details}>
            <button className={styles.close} onClick={() => setSelectedNode(null)}>×</button>
            <h3>{selectedNode.name}</h3>
            <p className={styles.category}>{selectedNode.category_name}</p>
            <div className={styles.info}>
              <p><strong>Вопросов:</strong> {selectedNode.questions_count}</p>
              <p><strong>Популярность:</strong> {selectedNode.interview_penetration.toFixed(1)}%</p>
              <p><strong>Пример вопроса:</strong></p>
              <blockquote>{selectedNode.example_question}</blockquote>
              <p><strong>Ключевые слова:</strong></p>
              <div className={styles.keywords}>
                {selectedNode.keywords.map(k => (
                  <span key={k} className={styles.keyword}>{k}</span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      <div className={styles.legend}>
        <h4>Категории:</h4>
        <div className={styles.categories}>
          {Object.entries(categoryColors).map(([id, color]) => (
            <div key={id} className={styles.category}>
              <span className={styles.dot} style={{ backgroundColor: color }} />
              <span>{data?.categories[id] || id}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};