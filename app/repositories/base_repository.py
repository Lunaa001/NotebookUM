from sqlalchemy.orm import Session
from typing import TypeVar, Generic, List, Optional

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Base repository class for CRUD operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def add(self, obj: T) -> T:
        """Add object to session"""
        self.session.add(obj)
        return obj
    
    def commit(self) -> None:
        """Commit transaction"""
        self.session.commit()
    
    def flush(self) -> None:
        """Flush session"""
        self.session.flush()
    
    def rollback(self) -> None:
        """Rollback transaction"""
        self.session.rollback()
