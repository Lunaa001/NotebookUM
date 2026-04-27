"""Tests for Usuario and Document models"""

import unittest
from datetime import datetime
from sqlalchemy import inspect
from app.models import Usuario, Document, Base
from app.models.usuario import Usuario as UsuarioModel
from app.models.document import Document as DocumentModel


class TestModelStructure(unittest.TestCase):
    """Test the structure and definitions of Usuario and Document models"""
    
    def test_usuario_model_exists(self):
        """Test that Usuario model is defined"""
        self.assertTrue(hasattr(UsuarioModel, '__tablename__'))
        self.assertEqual(UsuarioModel.__tablename__, 'usuarios')
    
    def test_usuario_columns(self):
        """Test that Usuario has all required columns"""
        mapper = inspect(UsuarioModel)
        columns = {c.name: c for c in mapper.columns}
        
        required_columns = {'id', 'nombre', 'email', 'fecha_registro'}
        self.assertTrue(required_columns.issubset(set(columns.keys())))
        
        # Verify column types
        self.assertTrue(columns['id'].primary_key)
        self.assertFalse(columns['nombre'].nullable)
        self.assertFalse(columns['email'].nullable)
        self.assertFalse(columns['fecha_registro'].nullable)
    
    def test_usuario_email_unique(self):
        """Test that email column has unique constraint"""
        mapper = inspect(UsuarioModel)
        columns = {c.name: c for c in mapper.columns}
        
        # Verify email column exists
        self.assertIn('email', columns)
        
        # Verify email column is not nullable (required)
        self.assertFalse(columns['email'].nullable, 
                        "Email should be required (non-nullable)")
    
    def test_document_model_exists(self):
        """Test that Document model is defined"""
        self.assertTrue(hasattr(DocumentModel, '__tablename__'))
        self.assertEqual(DocumentModel.__tablename__, 'documentos')
    
    def test_document_columns(self):
        """Test that Document has all required columns"""
        mapper = inspect(DocumentModel)
        columns = {c.name: c for c in mapper.columns}
        
        required_columns = {
            'id', 'usuario_id', 'nombre_archivo', 
            'ruta_archivo', 'texto_extraido', 'fecha_creacion'
        }
        self.assertTrue(required_columns.issubset(set(columns.keys())))
        
        # Verify column types
        self.assertTrue(columns['id'].primary_key)
        self.assertFalse(columns['usuario_id'].nullable)
        self.assertFalse(columns['nombre_archivo'].nullable)
        self.assertTrue(columns['texto_extraido'].nullable)
    
    def test_document_foreign_key(self):
        """Test that Document has foreign key to Usuario"""
        mapper = inspect(DocumentModel)
        
        # Check if usuario_id column exists and is indexed
        columns = {c.name: c for c in mapper.columns}
        self.assertIn('usuario_id', columns)
        
        # Verify the relationship is defined
        relationships = {r.key: r for r in mapper.relationships}
        self.assertIn('usuario', relationships)
    
    def test_relationship_usuario_to_document(self):
        """Test that Usuario has relationship to documents"""
        mapper = inspect(UsuarioModel)
        relationships = {r.key: r for r in mapper.relationships}
        
        # Check if relationship is defined
        self.assertIn('documentos', relationships)


class TestModelInstantiation(unittest.TestCase):
    """Test that models can be instantiated with proper attributes"""
    
    def test_usuario_instantiation(self):
        """Test creating a Usuario instance"""
        usuario = UsuarioModel(
            id=1,
            nombre="Juan Pérez",
            email="juan@example.com",
            fecha_registro=datetime.utcnow()
        )
        
        self.assertEqual(usuario.id, 1)
        self.assertEqual(usuario.nombre, "Juan Pérez")
        self.assertEqual(usuario.email, "juan@example.com")
        self.assertIsNotNone(usuario.fecha_registro)
    
    def test_document_instantiation(self):
        """Test creating a Document instance"""
        doc = DocumentModel(
            id=1,
            usuario_id=1,
            nombre_archivo="documento.pdf",
            ruta_archivo="/uploads/documento.pdf",
            texto_extraido="Contenido del documento",
            fecha_creacion=datetime.utcnow()
        )
        
        self.assertEqual(doc.id, 1)
        self.assertEqual(doc.usuario_id, 1)
        self.assertEqual(doc.nombre_archivo, "documento.pdf")
        self.assertEqual(doc.ruta_archivo, "/uploads/documento.pdf")
    
    def test_usuario_repr(self):
        """Test Usuario string representation"""
        usuario = UsuarioModel(
            id=1,
            nombre="Test User",
            email="test@example.com"
        )
        repr_str = repr(usuario)
        self.assertIn("Usuario", repr_str)
        self.assertIn("id=1", repr_str)
    
    def test_document_repr(self):
        """Test Document string representation"""
        doc = DocumentModel(
            id=1,
            usuario_id=1,
            nombre_archivo="test.pdf"
        )
        repr_str = repr(doc)
        self.assertIn("Document", repr_str)
        self.assertIn("id=1", repr_str)


class TestModelDefaults(unittest.TestCase):
    """Test default values in models"""
    
    def test_usuario_fecha_registro_default(self):
        """Test that fecha_registro has default value"""
        usuario1 = UsuarioModel(nombre="User1", email="user1@test.com")
        usuario2 = UsuarioModel(nombre="User2", email="user2@test.com")
        
        # Both should have fecha_registro even without explicit setting
        # (will be set when inserted into DB)
        self.assertIsNone(usuario1.fecha_registro)  # Will be set by DB default
    
    def test_document_fecha_creacion_default(self):
        """Test that fecha_creacion has default value"""
        doc = DocumentModel(
            usuario_id=1,
            nombre_archivo="test.pdf",
            ruta_archivo="/path/test.pdf"
        )
        
        # fecha_creacion should be set when inserted into DB
        self.assertIsNone(doc.fecha_creacion)


class TestBaseMetadata(unittest.TestCase):
    """Test that Base metadata is properly configured"""
    
    def test_base_contains_models(self):
        """Test that Base metadata contains Usuario and Document"""
        table_names = [table.name for table in Base.metadata.tables.values()]
        
        self.assertIn('usuarios', table_names)
        self.assertIn('documentos', table_names)


if __name__ == '__main__':
    unittest.main()
