from sqlalchemy.orm import Session
from app.repositories import UserRepository, DocumentRepository


class DocumentService:
    """Service for document operations"""
    
    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)
        self.document_repo = DocumentRepository(session)
    
    def create(self, payload: dict):
        """Create new document after validation"""
        if not payload.get("usuario_id") or not payload.get("nombre_archivo"):
            raise ValueError("usuario_id y nombre_archivo son obligatorios")

        usuario_id = payload["usuario_id"]
        nombre_archivo = payload["nombre_archivo"]

        if not self.user_repo.exists(usuario_id):
            raise ValueError("Usuario no encontrado")

        document = self.document_repo.create(
            usuario_id=usuario_id,
            nombre_archivo=nombre_archivo,
            ruta_archivo=payload.get("ruta_archivo"),
            texto_extraido=payload.get("texto_extraido"),
        )
        self.session.commit()
        return document
    
    def get_by_id(self, document_id: int):
        """Get document by ID"""
        document = self.document_repo.get_by_id(document_id)
        if document is None:
            raise ValueError("Documento no encontrado")
        return document
    
    def update(self, document_id: int, payload: dict):
        """Update document"""
        self.get_by_id(document_id)
        document = self.document_repo.update(
            document_id,
            nombre_archivo=payload.get("nombre_archivo"),
            ruta_archivo=payload.get("ruta_archivo"),
            texto_extraido=payload.get("texto_extraido"),
        )
        self.session.commit()
        return document
    
    def delete(self, document_id: int) -> bool:
        """Delete document"""
        self.get_by_id(document_id)
        result = self.document_repo.delete(document_id)
        self.session.commit()
        return result
    
    def list_by_user(self, usuario_id: int, skip: int = 0, limit: int = 100):
        """List documents by user"""
        if not self.user_repo.exists(usuario_id):
            raise ValueError("Usuario no encontrado")
        return self.document_repo.list_by_user(usuario_id, skip=skip, limit=limit)
    
    def list_all(self, skip: int = 0, limit: int = 100):
        """List all documents"""
        return self.document_repo.list_all(skip=skip, limit=limit)

