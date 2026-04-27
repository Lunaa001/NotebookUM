from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .base import Base


class Usuario(Base):
    """Usuario model for storing user information"""
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, nombre={self.nombre}, email={self.email})>"
