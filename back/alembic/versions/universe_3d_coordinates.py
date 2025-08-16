"""Add 3D coordinates and metadata for Interview Universe visualization

Revision ID: universe_3d_coords_001
Revises: 
Create Date: 2025-01-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'universe_3d_coords_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add 3D coordinates and metadata to InterviewCategory (galaxies)
    op.add_column('InterviewCategory', 
        sa.Column('galaxy_x', sa.Float(), nullable=True, server_default='0'))
    op.add_column('InterviewCategory',
        sa.Column('galaxy_y', sa.Float(), nullable=True, server_default='0'))
    op.add_column('InterviewCategory',
        sa.Column('galaxy_z', sa.Float(), nullable=True, server_default='0'))
    op.add_column('InterviewCategory',
        sa.Column('spiral_arm_angle', sa.Float(), nullable=True, server_default='0'))
    op.add_column('InterviewCategory',
        sa.Column('luminosity', sa.Float(), nullable=True, server_default='1.0'))
    op.add_column('InterviewCategory',
        sa.Column('last_activity_date', sa.TIMESTAMP(), nullable=True))
    
    # Add 3D coordinates and metadata to InterviewCluster (stars)
    op.add_column('InterviewCluster',
        sa.Column('star_x', sa.Float(), nullable=True))
    op.add_column('InterviewCluster',
        sa.Column('star_y', sa.Float(), nullable=True))
    op.add_column('InterviewCluster',
        sa.Column('star_z', sa.Float(), nullable=True))
    op.add_column('InterviewCluster',
        sa.Column('temperature', sa.Integer(), nullable=True))  # difficulty 1-10
    op.add_column('InterviewCluster',
        sa.Column('mass', sa.Float(), nullable=True))  # importance
    op.add_column('InterviewCluster',
        sa.Column('orbit_radius', sa.Float(), nullable=True))
    op.add_column('InterviewCluster',
        sa.Column('orbit_speed', sa.Float(), nullable=True))
    op.add_column('InterviewCluster',
        sa.Column('embedding_vector', postgresql.ARRAY(sa.Float()), nullable=True))
    
    # Add satellite coordinates to InterviewQuestion
    op.add_column('InterviewQuestion',
        sa.Column('satellite_orbit_angle', sa.Float(), nullable=True))
    op.add_column('InterviewQuestion',
        sa.Column('satellite_distance', sa.Float(), nullable=True))
    op.add_column('InterviewQuestion',
        sa.Column('glow_intensity', sa.Float(), nullable=True))
    op.add_column('InterviewQuestion',
        sa.Column('last_asked_date', sa.Date(), nullable=True))
    
    # Create table for cluster connections
    op.create_table('ClusterConnections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_cluster_id', sa.Integer(), nullable=True),
        sa.Column('target_cluster_id', sa.Integer(), nullable=True),
        sa.Column('connection_weight', sa.Float(), nullable=True),
        sa.Column('connection_type', sa.String(50), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['source_cluster_id'], ['InterviewCluster.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_cluster_id'], ['InterviewCluster.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('source_cluster_id', 'target_cluster_id')
    )
    
    # Create indexes for performance
    op.create_index('idx_cluster_3d_coords', 'InterviewCluster', ['star_x', 'star_y', 'star_z'])
    op.create_index('idx_question_activity', 'InterviewQuestion', ['last_asked_date'])
    op.create_index('idx_cluster_connections_source', 'ClusterConnections', ['source_cluster_id'])
    op.create_index('idx_cluster_connections_target', 'ClusterConnections', ['target_cluster_id'])
    
    # Create materialized view for cluster connections
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS cluster_connections_mv AS
        WITH co_occurrence AS (
            SELECT 
                q1.cluster_id as cluster1,
                q2.cluster_id as cluster2,
                COUNT(*) as weight
            FROM "InterviewQuestion" q1
            JOIN "InterviewQuestion" q2 
                ON q1.interview_id = q2.interview_id 
                AND q1.cluster_id < q2.cluster_id
            WHERE q1.cluster_id IS NOT NULL 
                AND q2.cluster_id IS NOT NULL
            GROUP BY q1.cluster_id, q2.cluster_id
            HAVING COUNT(*) > 10
        )
        SELECT 
            cluster1,
            cluster2,
            weight,
            'co-occurrence' as connection_type
        FROM co_occurrence;
    """)
    
    op.create_index('idx_cluster_connections_mv', 'cluster_connections_mv', ['cluster1', 'cluster2'])


def downgrade() -> None:
    # Drop materialized view
    op.execute("DROP MATERIALIZED VIEW IF EXISTS cluster_connections_mv")
    
    # Drop indexes
    op.drop_index('idx_cluster_connections_target', 'ClusterConnections')
    op.drop_index('idx_cluster_connections_source', 'ClusterConnections')
    op.drop_index('idx_question_activity', 'InterviewQuestion')
    op.drop_index('idx_cluster_3d_coords', 'InterviewCluster')
    
    # Drop ClusterConnections table
    op.drop_table('ClusterConnections')
    
    # Remove columns from InterviewQuestion
    op.drop_column('InterviewQuestion', 'last_asked_date')
    op.drop_column('InterviewQuestion', 'glow_intensity')
    op.drop_column('InterviewQuestion', 'satellite_distance')
    op.drop_column('InterviewQuestion', 'satellite_orbit_angle')
    
    # Remove columns from InterviewCluster
    op.drop_column('InterviewCluster', 'embedding_vector')
    op.drop_column('InterviewCluster', 'orbit_speed')
    op.drop_column('InterviewCluster', 'orbit_radius')
    op.drop_column('InterviewCluster', 'mass')
    op.drop_column('InterviewCluster', 'temperature')
    op.drop_column('InterviewCluster', 'star_z')
    op.drop_column('InterviewCluster', 'star_y')
    op.drop_column('InterviewCluster', 'star_x')
    
    # Remove columns from InterviewCategory
    op.drop_column('InterviewCategory', 'last_activity_date')
    op.drop_column('InterviewCategory', 'luminosity')
    op.drop_column('InterviewCategory', 'spiral_arm_angle')
    op.drop_column('InterviewCategory', 'galaxy_z')
    op.drop_column('InterviewCategory', 'galaxy_y')
    op.drop_column('InterviewCategory', 'galaxy_x')