from typing import Generic, TypeVar, Type, Optional, List, Dict, Any, Union
from sqlalchemy import and_, or_, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.shared.database.base import get_db_session, transactional
from app.shared.exceptions.base import (
    DatabaseException as DatabaseError,
    ResourceNotFoundException as EntityNotFoundError,
    ResourceConflictException as DuplicateEntityError
)
from app.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar('T')  # Generic type for model


class BaseRepository(Generic[T]):
    """
    Generic repository base class with common CRUD operations.
    All feature repositories should inherit from this class.
    """
    
    def __init__(self, model: Type[T]):
        self.model = model
        self.model_name = model.__name__
    
    @transactional
    def create(self, data: Dict[str, Any], session: Session = None) -> T:
        """Create new entity."""
        try:
            entity = self.model(**data)
            session.add(entity)
            session.flush()
            
            logger.info(f"Created {self.model_name}", extra={
                "model": self.model_name,
                "entity_id": getattr(entity, 'id', None),
                "data": data
            })
            
            return entity
            
        except IntegrityError as e:
            logger.error(f"Integrity error creating {self.model_name}", extra={
                "model": self.model_name,
                "error": str(e),
                "data": data
            })
            raise DuplicateEntityError(f"Duplicate {self.model_name}")
            
        except Exception as e:
            logger.error(f"Error creating {self.model_name}", extra={
                "model": self.model_name,
                "error": str(e),
                "data": data
            })
            raise DatabaseError(f"Failed to create {self.model_name}")
    
    def get_by_id(self, entity_id: Any, session: Session = None) -> Optional[T]:
        """Get entity by ID."""
        if session is None:
            session = get_db_session()
            
        try:
            entity = session.query(self.model).filter(self.model.id == entity_id).first()
            
            if entity:
                logger.debug(f"Found {self.model_name} by ID", extra={
                    "model": self.model_name,
                    "entity_id": entity_id
                })
            
            return entity
            
        except Exception as e:
            logger.error(f"Error getting {self.model_name} by ID", extra={
                "model": self.model_name,
                "entity_id": entity_id,
                "error": str(e)
            })
            raise DatabaseError(f"Failed to get {self.model_name}")
    
    def get_by_id_or_raise(self, entity_id: Any, session: Session = None) -> T:
        """Get entity by ID or raise EntityNotFoundError."""
        entity = self.get_by_id(entity_id, session)
        if not entity:
            raise EntityNotFoundError(f"{self.model_name} with id {entity_id} not found")
        return entity
    
    def get_all(self, 
                limit: Optional[int] = None,
                offset: Optional[int] = None,
                filters: Optional[Dict[str, Any]] = None,
                session: Session = None) -> List[T]:
        """Get all entities with optional filtering and pagination."""
        if session is None:
            session = get_db_session()
            
        try:
            query = session.query(self.model)
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        if isinstance(value, list):
                            query = query.filter(getattr(self.model, key).in_(value))
                        else:
                            query = query.filter(getattr(self.model, key) == value)
            
            # Apply pagination
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
                
            entities = query.all()
            
            logger.debug(f"Retrieved {len(entities)} {self.model_name} entities", extra={
                "model": self.model_name,
                "count": len(entities),
                "filters": filters,
                "limit": limit,
                "offset": offset
            })
            
            return entities
            
        except Exception as e:
            logger.error(f"Error getting {self.model_name} entities", extra={
                "model": self.model_name,
                "error": str(e),
                "filters": filters
            })
            raise DatabaseError(f"Failed to get {self.model_name} entities")
    
    @transactional
    def update(self, entity_id: Any, data: Dict[str, Any], session: Session = None) -> T:
        """Update entity by ID."""
        try:
            entity = self.get_by_id_or_raise(entity_id, session)
            
            # Update fields
            for key, value in data.items():
                if hasattr(entity, key) and key != 'id':
                    setattr(entity, key, value)
            
            session.flush()
            
            logger.info(f"Updated {self.model_name}", extra={
                "model": self.model_name,
                "entity_id": entity_id,
                "updated_fields": list(data.keys())
            })
            
            return entity
            
        except EntityNotFoundError:
            raise
        except IntegrityError as e:
            logger.error(f"Integrity error updating {self.model_name}", extra={
                "model": self.model_name,
                "entity_id": entity_id,
                "error": str(e)
            })
            raise DuplicateEntityError(f"Update violates constraints for {self.model_name}")
        except Exception as e:
            logger.error(f"Error updating {self.model_name}", extra={
                "model": self.model_name,
                "entity_id": entity_id,
                "error": str(e)
            })
            raise DatabaseError(f"Failed to update {self.model_name}")
    
    @transactional
    def delete(self, entity_id: Any, session: Session = None) -> bool:
        """Delete entity by ID."""
        try:
            entity = self.get_by_id_or_raise(entity_id, session)
            session.delete(entity)
            session.flush()
            
            logger.info(f"Deleted {self.model_name}", extra={
                "model": self.model_name,
                "entity_id": entity_id
            })
            
            return True
            
        except EntityNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error deleting {self.model_name}", extra={
                "model": self.model_name,
                "entity_id": entity_id,
                "error": str(e)
            })
            raise DatabaseError(f"Failed to delete {self.model_name}")
    
    def count(self, filters: Optional[Dict[str, Any]] = None, session: Session = None) -> int:
        """Count entities with optional filtering."""
        if session is None:
            session = get_db_session()
            
        try:
            query = session.query(self.model)
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        query = query.filter(getattr(self.model, key) == value)
            
            count = query.count()
            
            logger.debug(f"Counted {count} {self.model_name} entities", extra={
                "model": self.model_name,
                "count": count,
                "filters": filters
            })
            
            return count
            
        except Exception as e:
            logger.error(f"Error counting {self.model_name} entities", extra={
                "model": self.model_name,
                "error": str(e)
            })
            raise DatabaseError(f"Failed to count {self.model_name} entities")
    
    def exists(self, filters: Dict[str, Any], session: Session = None) -> bool:
        """Check if entity exists with given filters."""
        return self.count(filters, session) > 0
    
    def bulk_create(self, data_list: List[Dict[str, Any]], session: Session = None) -> List[T]:
        """Create multiple entities in bulk."""
        if session is None:
            session = get_db_session()
            
        try:
            entities = []
            for data in data_list:
                entity = self.model(**data)
                entities.append(entity)
                session.add(entity)
            
            session.flush()
            
            logger.info(f"Bulk created {len(entities)} {self.model_name} entities", extra={
                "model": self.model_name,
                "count": len(entities)
            })
            
            return entities
            
        except Exception as e:
            logger.error(f"Error bulk creating {self.model_name} entities", extra={
                "model": self.model_name,
                "error": str(e),
                "count": len(data_list)
            })
            raise DatabaseError(f"Failed to bulk create {self.model_name} entities")


class ReadOnlyRepository(BaseRepository[T]):
    """
    Read-only repository for entities that should not be modified.
    """
    
    def create(self, *args, **kwargs):
        raise NotImplementedError("Create operation not allowed in read-only repository")
    
    def update(self, *args, **kwargs):
        raise NotImplementedError("Update operation not allowed in read-only repository")
    
    def delete(self, *args, **kwargs):
        raise NotImplementedError("Delete operation not allowed in read-only repository")
    
    def bulk_create(self, *args, **kwargs):
        raise NotImplementedError("Bulk create operation not allowed in read-only repository") 


