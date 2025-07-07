from abc import ABC
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BaseEntity(ABC):
    """Базовый класс для всех domain entities"""
    id: Optional[Any] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертация entity в словарь"""
        return {
            k: v for k, v in self.__dict__.items() 
            if not k.startswith('_')
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseEntity':
        """Создание entity из словаря"""
        return cls(**data) 