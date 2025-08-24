"""
Universe Calculator for computing 3D positions of galaxies, clusters, and questions
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

# Optional imports - will work without them
try:
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    from sklearn.preprocessing import StandardScaler

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not installed, some features will be limited")


class UniverseCalculator:
    """Calculate 3D positions for Interview Universe visualization"""

    def __init__(self):
        self.golden_ratio = (1 + np.sqrt(5)) / 2
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None

    def calculate_galaxy_positions(
        self, categories: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Calculate spiral galaxy positions for categories
        Uses golden ratio spiral for optimal distribution
        """
        positions = []
        total_questions = sum(cat.get("questions_count", 0) for cat in categories)

        for i, category in enumerate(categories):
            # Golden ratio spiral for even distribution
            angle = 2 * np.pi * i / self.golden_ratio

            # Radius based on relative importance (question count)
            question_ratio = category.get("questions_count", 0) / max(
                total_questions, 1
            )
            radius = 50 + (question_ratio * 150)  # 50-200 units

            # Vertical spread for 3D effect
            z = (i - len(categories) / 2) * 20

            # Calculate luminosity based on activity
            luminosity = self._calculate_luminosity(category)

            positions.append(
                {
                    "id": category.get("id"),
                    "name": category.get("name"),
                    "galaxy_x": float(radius * np.cos(angle)),
                    "galaxy_y": float(radius * np.sin(angle)),
                    "galaxy_z": float(z),
                    "spiral_arm_angle": float(angle),
                    "luminosity": float(luminosity),
                    "spiral_arm": i % 3,  # 3 spiral arms
                    "metadata": {
                        "questions_count": category.get("questions_count", 0),
                        "clusters_count": category.get("clusters_count", 0),
                        "percentage": category.get("percentage", 0),
                    },
                }
            )

        return positions

    def calculate_cluster_positions(
        self,
        clusters: List[Dict[str, Any]],
        embeddings: Optional[np.ndarray] = None,
        use_tsne: bool = True,
    ) -> np.ndarray:
        """
        Calculate 3D positions for clusters using embeddings
        Falls back to random distribution if embeddings not available
        """
        n_clusters = len(clusters)

        if (
            embeddings is not None
            and embeddings.shape[0] == n_clusters
            and SKLEARN_AVAILABLE
        ):
            # Use actual embeddings for semantic positioning
            if use_tsne and n_clusters > 30:
                # t-SNE for better local structure preservation
                perplexity = min(30, n_clusters - 1)
                tsne = TSNE(
                    n_components=3,
                    perplexity=perplexity,
                    n_iter=1000,
                    random_state=42,
                    learning_rate="auto",
                    init="pca",
                )
                coords_3d = tsne.fit_transform(embeddings)
            else:
                # PCA for smaller datasets or faster computation
                pca = PCA(n_components=3)
                coords_3d = pca.fit_transform(embeddings)

            # Normalize and scale
            if self.scaler:
                coords_3d = self.scaler.fit_transform(coords_3d) * 100
            else:
                # Manual normalization if sklearn not available
                coords_3d = (
                    (coords_3d - coords_3d.mean(axis=0))
                    / (coords_3d.std(axis=0) + 1e-8)
                    * 100
                )

        else:
            # Fallback: Distribute clusters in spherical pattern
            logger.warning("No embeddings provided, using spherical distribution")
            coords_3d = self._generate_spherical_distribution(n_clusters)

        # Add orbital motion parameters
        positions = []
        for i, cluster in enumerate(clusters):
            # Calculate temperature (difficulty) based on keywords
            temperature = self._estimate_difficulty(cluster)

            # Mass represents importance (based on question count)
            mass = float(np.log1p(cluster.get("questions_count", 1)) * 10)

            # Orbital parameters for animation
            category_idx = self._get_category_index(cluster.get("category_id"))
            orbit_radius = float(30 + (i % 5) * 15)  # Varying orbital radii
            orbit_speed = float(0.5 + (np.random.random() * 0.5))  # Varying speeds

            positions.append(
                {
                    "id": cluster.get("id"),
                    "name": cluster.get("name"),
                    "star_x": float(coords_3d[i, 0]),
                    "star_y": float(coords_3d[i, 1]),
                    "star_z": float(coords_3d[i, 2]),
                    "temperature": int(temperature),
                    "mass": mass,
                    "orbit_radius": orbit_radius,
                    "orbit_speed": orbit_speed,
                    "category_id": cluster.get("category_id"),
                    "questions_count": cluster.get("questions_count", 0),
                }
            )

        return positions

    def calculate_company_positions(
        self, companies: List[Dict[str, Any]], clusters: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Calculate positions for companies as planets orbiting clusters
        """
        positions = []
        cluster_map = {c["id"]: c for c in clusters}

        for company in companies:
            # Find primary cluster for this company
            primary_cluster = self._find_primary_cluster(company, cluster_map)

            if primary_cluster:
                # Calculate orbital position around cluster
                orbit_angle = np.random.random() * 2 * np.pi
                orbit_distance = 10 + np.random.random() * 20

                planet_x = primary_cluster["star_x"] + orbit_distance * np.cos(
                    orbit_angle
                )
                planet_y = primary_cluster["star_y"] + orbit_distance * np.sin(
                    orbit_angle
                )
                planet_z = primary_cluster["star_z"] + (np.random.random() - 0.5) * 10

                positions.append(
                    {
                        "id": company.get("id"),
                        "name": company.get("company_name"),
                        "x": planet_x,
                        "y": planet_y,
                        "z": planet_z,
                        "primary_cluster_id": primary_cluster["id"],
                        "orbit_angle": orbit_angle,
                        "orbit_distance": orbit_distance,
                        "size": np.log1p(company.get("questions_count", 1)) * 2,
                        "metadata": {
                            "questions_count": company.get("questions_count", 0),
                            "categories": company.get("categories", []),
                        },
                    }
                )

        return positions

    def calculate_question_positions(
        self,
        questions: List[Dict[str, Any]],
        company_positions: Dict[str, Dict[str, float]],
    ) -> List[Dict[str, Any]]:
        """
        Calculate positions for questions as satellites around companies
        """
        positions = []

        for question in questions:
            company_id = question.get("company")
            if company_id and company_id in company_positions:
                company_pos = company_positions[company_id]

                # Random satellite position around company
                sat_angle = np.random.random() * 2 * np.pi
                sat_phi = np.random.random() * np.pi
                sat_distance = 2 + np.random.random() * 3

                sat_x = company_pos["x"] + sat_distance * np.sin(sat_phi) * np.cos(
                    sat_angle
                )
                sat_y = company_pos["y"] + sat_distance * np.sin(sat_phi) * np.sin(
                    sat_angle
                )
                sat_z = company_pos["z"] + sat_distance * np.cos(sat_phi)

                positions.append(
                    {
                        "id": question.get("id"),
                        "x": sat_x,
                        "y": sat_y,
                        "z": sat_z,
                        "satellite_orbit_angle": sat_angle,
                        "satellite_distance": sat_distance,
                        "glow_intensity": self._calculate_question_glow(question),
                        "company_id": company_id,
                        "cluster_id": question.get("cluster_id"),
                    }
                )

        return positions

    def calculate_connections(
        self, clusters: List[Dict[str, Any]], min_weight: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Calculate semantic and co-occurrence connections between clusters
        """
        connections = []

        # This would typically query the database for co-occurrence data
        # For now, returning placeholder structure
        for i, source in enumerate(clusters):
            for j, target in enumerate(clusters[i + 1 :], i + 1):
                # Simulate connection weight based on shared keywords
                source_keywords = set(source.get("keywords", []))
                target_keywords = set(target.get("keywords", []))
                shared = len(source_keywords & target_keywords)

                if shared >= 2:  # At least 2 shared keywords
                    connections.append(
                        {
                            "source_cluster_id": source["id"],
                            "target_cluster_id": target["id"],
                            "connection_weight": float(shared * 5),
                            "connection_type": "semantic",
                        }
                    )

        return connections

    def calculate_heat_signatures(
        self,
        nodes: List[Dict[str, Any]],
        activity_data: List[Dict[str, Any]],
        time_window_days: int = 30,
    ) -> Dict[str, float]:
        """
        Calculate heat signatures based on recent activity
        """
        heat_map = {}
        cutoff_date = datetime.now() - timedelta(days=time_window_days)

        for activity in activity_data:
            if activity.get("date") and activity["date"] > cutoff_date:
                node_id = activity.get("node_id")
                if node_id:
                    heat_map[node_id] = heat_map.get(node_id, 0) + 1

        # Normalize heat values to 0-1 range
        if heat_map:
            max_heat = max(heat_map.values())
            heat_map = {k: v / max_heat for k, v in heat_map.items()}

        return heat_map

    # Helper methods
    def _calculate_luminosity(self, category: Dict[str, Any]) -> float:
        """Calculate galaxy luminosity based on activity and size"""
        base_luminosity = 0.5
        size_factor = min(category.get("questions_count", 0) / 1000, 1.0) * 0.3
        activity_factor = 0.2  # Would be calculated from recent activity
        return base_luminosity + size_factor + activity_factor

    def _estimate_difficulty(self, cluster: Dict[str, Any]) -> int:
        """Estimate difficulty level (1-10) based on keywords"""
        keywords = cluster.get("keywords", [])
        difficulty_keywords = {
            "advanced": 3,
            "complex": 3,
            "optimization": 2,
            "algorithm": 2,
            "architecture": 3,
            "design pattern": 2,
            "performance": 2,
            "senior": 3,
            "expert": 3,
        }

        score = 5  # Base difficulty
        for keyword in keywords:
            for diff_key, points in difficulty_keywords.items():
                if diff_key in keyword.lower():
                    score = min(10, score + points)

        return score

    def _generate_spherical_distribution(self, n_points: int) -> np.ndarray:
        """Generate points distributed on a sphere"""
        indices = np.arange(0, n_points, dtype=float) + 0.5

        phi = np.arccos(1 - 2 * indices / n_points)
        theta = np.pi * (1 + 5**0.5) * indices

        x = np.sin(phi) * np.cos(theta) * 100
        y = np.sin(phi) * np.sin(theta) * 100
        z = np.cos(phi) * 100

        return np.column_stack([x, y, z])

    def _get_category_index(self, category_id: str) -> int:
        """Map category ID to index for consistent positioning"""
        category_map = {
            "javascript_core": 0,
            "react": 1,
            "typescript": 2,
            "soft_skills": 3,
            "сеть": 4,
            "алгоритмы": 5,
            "верстка": 6,
            "браузеры": 7,
            "архитектура": 8,
            "инструменты": 9,
            "производительность": 10,
            "тестирование": 11,
            "другое": 12,
        }
        return category_map.get(category_id, 0)

    def _find_primary_cluster(
        self, company: Dict[str, Any], cluster_map: Dict[int, Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Find the primary cluster for a company based on question distribution"""
        # This would typically analyze actual question distribution
        # For now, return random cluster
        if cluster_map:
            return list(cluster_map.values())[0]
        return None

    def _calculate_question_glow(self, question: Dict[str, Any]) -> float:
        """Calculate glow intensity based on question popularity/difficulty"""
        # This would be based on actual metrics
        return np.random.random() * 0.5 + 0.5
