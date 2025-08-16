import { apiInstance } from './base';

interface UniverseNode {
  id: string;
  type: string;
  name: string;
  x: number;
  y: number;
  z: number;
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

interface UniverseInitialState {
  nodes: UniverseNode[];
  links: UniverseLink[];
  zoom_level: number;
  total_nodes_available: number;
}

export const universeApi = {
  async getInitialState(zoomLevel: number, cameraPosition: string) {
    const response = await apiInstance.get<UniverseInitialState>('/v2/universe/initial-state', {
      params: {
        zoom_level: zoomLevel,
        camera_position: cameraPosition
      }
    });
    return response.data;
  },
  
  async getGalaxies() {
    const response = await apiInstance.get('/v2/universe/galaxies');
    return response.data;
  },
  
  async getClustersByCategory(categoryId: string) {
    const response = await apiInstance.get(`/v2/universe/clusters/${categoryId}`);
    return response.data;
  },
  
  async searchSemantic(query: string, limit: number = 5) {
    const response = await apiInstance.get('/v2/universe/search', {
      params: { query, limit }
    });
    return response.data;
  },
  
  async getTimeline(startDate?: string, endDate?: string, granularity: string = 'month') {
    const response = await apiInstance.get('/v2/universe/timeline', {
      params: {
        start_date: startDate,
        end_date: endDate,
        granularity
      }
    });
    return response.data;
  },
  
  async getCareerPath(companyName: string) {
    const response = await apiInstance.get(`/v2/universe/career-path/${companyName}`);
    return response.data;
  },
  
  async getHeatMap(days: number = 30) {
    const response = await apiInstance.get('/v2/universe/heat-map', {
      params: { days }
    });
    return response.data;
  }
};