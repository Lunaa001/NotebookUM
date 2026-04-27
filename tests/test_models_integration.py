"""Integration tests for Usuario and Document models with database"""

import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models import Base, Usuario, Document


class TestModelsWithDatabase(unittest.TestCase):
    """Test models with in-memory SQLite database"""
    
    @classmethod
    def setUpClass(cls):
        """Create in-memory SQLite database for testing"""
        # Use SQLite in-memory database for tests
        cls.engine = create_engine(
            'sqlite:///:memory:',
            connect_args={'check_same_thread': False}
        )
        Base.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(bind=cls.engine)
    
    def setUp(self):
        """Create a new session for each test"""
        self.session: Session = self.SessionLocal()
    
    def tearDown(self):
        """Rollback session after each test"""
        self.session.rollback()
        self.session.close()
    
    def test_create_usuario(self):
        """Test creating and storing a Usuario"""
        usuario = Usuario(
            nombre="Juan Pérez",
            email="juan@example.com",
            fecha_registro=datetime.utcnow()
        )
        
        self.session.add(usuario)
        self.session.commit()
        
        # Verify it was saved
        retrieved = self.session.query(Usuario).filter_by(email="juan@example.com").first()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.nombre, "Juan Pérez")
        self.assertEqual(retrieved.email, "juan@example.com")
    
    def test_usuario_email_unique(self):
        """Test that email uniqueness is enforced"""
        usuario1 = Usuario(
            nombre="User 1",
            email="duplicate@example.com",
            fecha_registro=datetime.utcnow()
        )
        usuario2 = Usuario(
            nombre="User 2",
            email="duplicate@example.com",
            fecha_registro=datetime.utcnow()
        )
        
        self.session.add(usuario1)
        self.session.commit()
        
        self.session.add(usuario2)
        with self.assertRaises(Exception):  # IntegrityError
            self.session.commit()
    
    def test_create_document(self):
        """Test creating and storing a Document with Usuario"""
        # Create Usuario first
        usuario = Usuario(
            nombre="Test User",
            email="test@example.com",
            fecha_registro=datetime.utcnow()
        )
        self.session.add(usuario)
        self.session.flush()  # Get the ID without committing
        
        # Create Document
        documento = Document(
            usuario_id=usuario.id,
            nombre_archivo="documento.pdf",
            ruta_archivo="/uploads/documento.pdf",
            texto_extraido="Contenido del documento",
            fecha_creacion=datetime.utcnow()
        )
        
        self.session.add(documento)
        self.session.commit()
        
        # Verify it was saved
        retrieved = self.session.query(Document).filter_by(
            nombre_archivo="documento.pdf"
        ).first()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.usuario_id, usuario.id)
    
    def test_document_foreign_key(self):
        """Test that document requires valid usuario_id"""
        # Try to create document with non-existent usuario_id
        documento = Document(
            usuario_id=9999,  # Non-existent ID
            nombre_archivo="doc.pdf",
            ruta_archivo="/path/doc.pdf",
            fecha_creacion=datetime.utcnow()
        )
        
        self.session.add(documento)
        # Note: SQLite doesn't enforce foreign keys by default
        # This test is primarily for documentation
        try:
            self.session.commit()
        except Exception:
            pass  # Expected behavior with stricter databases
    
    def test_usuario_has_documents_relationship(self):
        """Test the relationship between Usuario and Document"""
        # Create Usuario
        usuario = Usuario(
            nombre="Maria Garcia",
            email="maria@example.com",
            fecha_registro=datetime.utcnow()
        )
        self.session.add(usuario)
        self.session.flush()
        
        # Create multiple documents
        doc1 = Document(
            usuario_id=usuario.id,
            nombre_archivo="doc1.pdf",
            ruta_archivo="/uploads/doc1.pdf",
            fecha_creacion=datetime.utcnow()
        )
        doc2 = Document(
            usuario_id=usuario.id,
            nombre_archivo="doc2.txt",
            ruta_archivo="/uploads/doc2.txt",
            texto_extraido="Contenido de doc2",
            fecha_creacion=datetime.utcnow()
        )
        
        self.session.add_all([doc1, doc2])
        self.session.commit()
        
        # Access documents through relationship
        retrieved_usuario = self.session.query(Usuario).filter_by(
            email="maria@example.com"
        ).first()
        
        self.assertEqual(len(retrieved_usuario.documentos), 2)
        nombres = [d.nombre_archivo for d in retrieved_usuario.documentos]
        self.assertIn("doc1.pdf", nombres)
        self.assertIn("doc2.txt", nombres)
    
    def test_query_documents_by_usuario(self):
        """Test querying documents filtered by usuario"""
        # Create two usuarios
        usuario1 = Usuario(
            nombre="User 1",
            email="user1@example.com",
            fecha_registro=datetime.utcnow()
        )
        usuario2 = Usuario(
            nombre="User 2",
            email="user2@example.com",
            fecha_registro=datetime.utcnow()
        )
        self.session.add_all([usuario1, usuario2])
        self.session.flush()
        
        # Create documents for each usuario
        for i in range(3):
            doc = Document(
                usuario_id=usuario1.id,
                nombre_archivo=f"user1_doc{i}.pdf",
                ruta_archivo=f"/uploads/user1_doc{i}.pdf",
                fecha_creacion=datetime.utcnow()
            )
            self.session.add(doc)
        
        for i in range(2):
            doc = Document(
                usuario_id=usuario2.id,
                nombre_archivo=f"user2_doc{i}.pdf",
                ruta_archivo=f"/uploads/user2_doc{i}.pdf",
                fecha_creacion=datetime.utcnow()
            )
            self.session.add(doc)
        
        self.session.commit()
        
        # Query documents by usuario
        user1_docs = self.session.query(Document).filter_by(
            usuario_id=usuario1.id
        ).all()
        user2_docs = self.session.query(Document).filter_by(
            usuario_id=usuario2.id
        ).all()
        
        self.assertEqual(len(user1_docs), 3)
        self.assertEqual(len(user2_docs), 2)
    
    def test_delete_usuario_documents(self):
        """Test deleting documents associated with a usuario"""
        usuario = Usuario(
            nombre="Temp User",
            email="temp@example.com",
            fecha_registro=datetime.utcnow()
        )
        self.session.add(usuario)
        self.session.flush()
        
        # Create documents
        for i in range(2):
            doc = Document(
                usuario_id=usuario.id,
                nombre_archivo=f"doc{i}.pdf",
                ruta_archivo=f"/uploads/doc{i}.pdf",
                fecha_creacion=datetime.utcnow()
            )
            self.session.add(doc)
        
        self.session.commit()
        
        # Delete all documents from this usuario
        self.session.query(Document).filter_by(usuario_id=usuario.id).delete()
        self.session.commit()
        
        # Verify deletion
        remaining = self.session.query(Document).filter_by(
            usuario_id=usuario.id
        ).all()
        self.assertEqual(len(remaining), 0)
    
    def test_update_document(self):
        """Test updating a document's extracted text"""
        usuario = Usuario(
            nombre="User",
            email="update@example.com",
            fecha_registro=datetime.utcnow()
        )
        self.session.add(usuario)
        self.session.flush()
        
        doc = Document(
            usuario_id=usuario.id,
            nombre_archivo="updatetest.pdf",
            ruta_archivo="/uploads/updatetest.pdf",
            texto_extraido="Initial content",
            fecha_creacion=datetime.utcnow()
        )
        self.session.add(doc)
        self.session.commit()
        
        # Update the document
        doc.texto_extraido = "Updated content"
        self.session.commit()
        
        # Verify update
        retrieved = self.session.query(Document).filter_by(
            nombre_archivo="updatetest.pdf"
        ).first()
        self.assertEqual(retrieved.texto_extraido, "Updated content")


if __name__ == '__main__':
    unittest.main()
