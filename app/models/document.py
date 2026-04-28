from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Document(Base):
    """Document model for storing uploaded documents"""
    __tablename__ = "documentos"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    nombre_archivo = Column(String(255), nullable=False)
    ruta_archivo = Column(String(500), nullable=False)
    texto_extraido = Column(Text, nullable=True)
    resumen = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    usuario = relationship("Usuario", backref="documentos")
    
    def __repr__(self):
        return f"<Document(id={self.id}, nombre_archivo={self.nombre_archivo}, usuario_id={self.usuario_id})>"
