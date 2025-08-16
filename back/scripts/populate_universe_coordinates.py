"""
Script to populate 3D coordinates for Interview Universe visualization
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from sqlalchemy import create_engine, select, update, text
from sqlalchemy.orm import sessionmaker
from app.shared.entities.interview_universe import (
    InterviewCategory,
    InterviewCluster,
    InterviewQuestion
)
from app.features.visualization.services.universe_calculator import UniverseCalculator
from app.core.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database connection
engine = create_engine(settings.database_url)
Session = sessionmaker(bind=engine)


def populate_galaxy_positions():
    """Populate 3D positions for categories (galaxies)"""
    session = Session()
    calculator = UniverseCalculator()
    
    try:
        # Get all categories
        categories = session.query(InterviewCategory).all()
        logger.info(f"Found {len(categories)} categories")
        
        # Prepare data for calculator
        category_data = []
        for cat in categories:
            category_data.append({
                'id': cat.id,
                'name': cat.name,
                'questions_count': cat.questions_count,
                'clusters_count': cat.clusters_count,
                'percentage': float(cat.percentage) if cat.percentage else 0
            })
        
        # Calculate positions
        positions = calculator.calculate_galaxy_positions(category_data)
        
        # Update database
        for pos in positions:
            stmt = (
                update(InterviewCategory)
                .where(InterviewCategory.id == pos['id'])
                .values(
                    galaxy_x=float(pos['galaxy_x']),
                    galaxy_y=float(pos['galaxy_y']),
                    galaxy_z=float(pos['galaxy_z']),
                    spiral_arm_angle=float(pos['spiral_arm_angle']),
                    luminosity=float(pos['luminosity'])
                )
            )
            session.execute(stmt)
        
        session.commit()
        logger.info(f"✅ Updated positions for {len(positions)} galaxies")
        
    except Exception as e:
        logger.error(f"Error updating galaxy positions: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def populate_cluster_positions():
    """Populate 3D positions for clusters (stars)"""
    session = Session()
    calculator = UniverseCalculator()
    
    try:
        # Get all clusters with their categories
        clusters = session.query(InterviewCluster).all()
        logger.info(f"Found {len(clusters)} clusters")
        
        # Group clusters by category for better positioning
        clusters_by_category = {}
        for cluster in clusters:
            if cluster.category_id not in clusters_by_category:
                clusters_by_category[cluster.category_id] = []
            clusters_by_category[cluster.category_id].append(cluster)
        
        # Process each category's clusters
        for category_id, category_clusters in clusters_by_category.items():
            logger.info(f"Processing {len(category_clusters)} clusters for category {category_id}")
            
            # Get category position for reference
            category = session.query(InterviewCategory).filter_by(id=category_id).first()
            if not category:
                continue
            
            # Prepare cluster data
            cluster_data = []
            for cluster in category_clusters:
                cluster_data.append({
                    'id': cluster.id,
                    'name': cluster.name,
                    'category_id': cluster.category_id,
                    'questions_count': cluster.questions_count,
                    'keywords': cluster.keywords or []
                })
            
            # Calculate positions (without embeddings for now)
            positions = calculator.calculate_cluster_positions(cluster_data, use_tsne=False)
            
            # Offset positions based on galaxy location
            galaxy_offset_x = category.galaxy_x if category.galaxy_x else 0
            galaxy_offset_y = category.galaxy_y if category.galaxy_y else 0
            galaxy_offset_z = category.galaxy_z if category.galaxy_z else 0
            
            # Update database
            for pos in positions:
                # Add galaxy offset to cluster positions
                star_x = pos['star_x'] + galaxy_offset_x
                star_y = pos['star_y'] + galaxy_offset_y
                star_z = pos['star_z'] + galaxy_offset_z
                
                stmt = (
                    update(InterviewCluster)
                    .where(InterviewCluster.id == pos['id'])
                    .values(
                        star_x=star_x,
                        star_y=star_y,
                        star_z=star_z,
                        temperature=pos['temperature'],
                        mass=pos['mass'],
                        orbit_radius=pos['orbit_radius'],
                        orbit_speed=pos['orbit_speed']
                    )
                )
                session.execute(stmt)
            
            logger.info(f"  ✅ Updated {len(positions)} clusters for category {category_id}")
        
        session.commit()
        logger.info(f"✅ Successfully updated all cluster positions")
        
    except Exception as e:
        logger.error(f"Error updating cluster positions: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def populate_question_satellites():
    """Populate satellite positions for questions"""
    session = Session()
    
    try:
        # Sample of questions to update (limit for performance)
        questions = session.query(InterviewQuestion).filter(
            InterviewQuestion.cluster_id.isnot(None)
        ).limit(1000).all()
        
        logger.info(f"Updating satellite positions for {len(questions)} questions")
        
        for question in questions:
            # Random satellite parameters
            satellite_orbit_angle = np.random.random() * 2 * np.pi
            satellite_distance = 2 + np.random.random() * 3
            glow_intensity = 0.5 + np.random.random() * 0.5
            
            stmt = (
                update(InterviewQuestion)
                .where(InterviewQuestion.id == question.id)
                .values(
                    satellite_orbit_angle=satellite_orbit_angle,
                    satellite_distance=satellite_distance,
                    glow_intensity=glow_intensity
                )
            )
            session.execute(stmt)
        
        session.commit()
        logger.info(f"✅ Updated satellite positions for {len(questions)} questions")
        
    except Exception as e:
        logger.error(f"Error updating question satellites: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def populate_cluster_connections():
    """Populate connections between clusters based on co-occurrence"""
    session = Session()
    
    try:
        logger.info("Calculating cluster connections...")
        
        # Get co-occurrence data
        query = text("""
            INSERT INTO "ClusterConnections" (source_cluster_id, target_cluster_id, connection_weight, connection_type)
            SELECT 
                q1.cluster_id as source_cluster_id,
                q2.cluster_id as target_cluster_id,
                COUNT(*) as connection_weight,
                'co-occurrence' as connection_type
            FROM "InterviewQuestion" q1
            JOIN "InterviewQuestion" q2 
                ON q1.interview_id = q2.interview_id 
                AND q1.cluster_id < q2.cluster_id
            WHERE q1.cluster_id IS NOT NULL 
                AND q2.cluster_id IS NOT NULL
            GROUP BY q1.cluster_id, q2.cluster_id
            HAVING COUNT(*) > 10
            ON CONFLICT (source_cluster_id, target_cluster_id) 
            DO UPDATE SET 
                connection_weight = EXCLUDED.connection_weight,
                updated_at = NOW()
        """)
        
        result = session.execute(query)
        session.commit()
        
        logger.info(f"✅ Created cluster connections")
        
    except Exception as e:
        logger.error(f"Error creating cluster connections: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def verify_population():
    """Verify that coordinates have been populated"""
    session = Session()
    
    try:
        # Check categories
        total_categories = session.query(InterviewCategory).count()
        populated_categories = session.query(InterviewCategory).filter(
            InterviewCategory.galaxy_x.isnot(None)
        ).count()
        
        # Check clusters
        total_clusters = session.query(InterviewCluster).count()
        populated_clusters = session.query(InterviewCluster).filter(
            InterviewCluster.star_x.isnot(None)
        ).count()
        
        # Check questions
        total_questions = session.query(InterviewQuestion).filter(
            InterviewQuestion.cluster_id.isnot(None)
        ).count()
        populated_questions = session.query(InterviewQuestion).filter(
            InterviewQuestion.satellite_orbit_angle.isnot(None)
        ).count()
        
        # Check connections
        connections_count = session.execute(
            text('SELECT COUNT(*) FROM "ClusterConnections"')
        ).scalar()
        
        logger.info("\n📊 Population Statistics:")
        logger.info(f"  Categories: {populated_categories}/{total_categories} have coordinates")
        logger.info(f"  Clusters: {populated_clusters}/{total_clusters} have coordinates")
        logger.info(f"  Questions: {populated_questions}/{total_questions} have satellite positions")
        logger.info(f"  Connections: {connections_count} cluster connections")
        
        return {
            'categories': {'total': total_categories, 'populated': populated_categories},
            'clusters': {'total': total_clusters, 'populated': populated_clusters},
            'questions': {'total': total_questions, 'populated': populated_questions},
            'connections': connections_count
        }
        
    finally:
        session.close()


def main():
    """Main function to populate all 3D coordinates"""
    logger.info("🚀 Starting Interview Universe coordinate population...")
    
    try:
        # 1. Populate galaxy positions
        logger.info("\n1️⃣ Populating galaxy positions...")
        populate_galaxy_positions()
        
        # 2. Populate cluster positions
        logger.info("\n2️⃣ Populating cluster positions...")
        populate_cluster_positions()
        
        # 3. Populate question satellites (sample)
        logger.info("\n3️⃣ Populating question satellite positions...")
        populate_question_satellites()
        
        # 4. Create cluster connections
        logger.info("\n4️⃣ Creating cluster connections...")
        populate_cluster_connections()
        
        # 5. Verify population
        logger.info("\n5️⃣ Verifying population...")
        stats = verify_population()
        
        logger.info("\n✅ Interview Universe population completed successfully!")
        
    except Exception as e:
        logger.error(f"\n❌ Error during population: {e}")
        raise


if __name__ == "__main__":
    main()