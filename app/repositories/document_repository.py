from sqlalchemy.orm import Session
from app.models.document import Document


class DocumentRepository:
    """Repository for Document model operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, document_id: int) -> Document | None:
        """Get document by ID"""
        return self.session.query(Document).filter(Document.id == document_id).first()
    
    def create(
        self,
        *,
        usuario_id: int,
        nombre_archivo: str,
        ruta_archivo: str | None = None,
        texto_extraido: str | None = None,
    ) -> Document:
        """Create new document"""
        document = Document(
            usuario_id=usuario_id,
            nombre_archivo=nombre_archivo,
            ruta_archivo=ruta_archivo,
            texto_extraido=texto_extraido,
        )
        self.session.add(document)
        self.session.flush()
        return document
    
    def update(
        self,
        document_id: int,
        *,
        nombre_archivo: str | None = None,
        ruta_archivo: str | None = None,
        texto_extraido: str | None = None,
    ) -> Document | None:
        """Update document"""
        document = self.get_by_id(document_id)
        if not document:
            return None
        
        if nombre_archivo is not None:
            document.nombre_archivo = nombre_archivo
        if ruta_archivo is not None:
            document.ruta_archivo = ruta_archivo
        if texto_extraido is not None:
            document.texto_extraido = texto_extraido
        
        self.session.flush()
        return document
    
    def delete(self, document_id: int) -> bool:
        """Delete document by ID"""
        document = self.get_by_id(document_id)
        if not document:
            return False
        
        self.session.delete(document)
        self.session.flush()
        return True
    
    def list_by_user(self, usuario_id: int, skip: int = 0, limit: int = 100) -> list[Document]:
        """List documents by user with pagination"""
        return (
            self.session.query(Document)
            .filter(Document.usuario_id == usuario_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def list_all(self, skip: int = 0, limit: int = 100) -> list[Document]:
        """List all documents with pagination"""
        return self.session.query(Document).offset(skip).limit(limit).all()
