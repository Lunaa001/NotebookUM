import unittest
from unittest.mock import patch, MagicMock

from app.services.document_service import DocumentService


class TestDocument(unittest.TestCase):
    def test_create_document_returns_created_document(self):
        mock_session = MagicMock()
        
        with patch("app.services.document_service.UserRepository") as user_repo_cls, \
             patch("app.services.document_service.DocumentRepository") as doc_repo_cls:
            
            user_repo = user_repo_cls.return_value
            doc_repo = doc_repo_cls.return_value
            user_repo.exists.return_value = True
            doc_repo.create.return_value = {
                "id": 10,
                "usuario_id": 1,
                "nombre_archivo": "apunte.pdf",
            }
            service = DocumentService(mock_session)

            created = service.create({"usuario_id": 1, "nombre_archivo": "apunte.pdf"})

            self.assertEqual(created["id"], 10)
            doc_repo.create.assert_called_once_with(
                usuario_id=1,
                nombre_archivo="apunte.pdf",
                ruta_archivo=None,
                texto_extraido=None,
            )

    def test_create_document_requires_usuario_id_and_nombre_archivo(self):
        mock_session = MagicMock()
        service = DocumentService(mock_session)

        with self.assertRaises(ValueError):
            service.create({"nombre_archivo": "apunte.pdf"})

    def test_create_document_fails_when_user_not_exists(self):
        mock_session = MagicMock()
        
        with patch("app.services.document_service.UserRepository") as user_repo_cls, \
             patch("app.services.document_service.DocumentRepository"):
            
            user_repo = user_repo_cls.return_value
            user_repo.exists.return_value = False
            service = DocumentService(mock_session)

            with self.assertRaises(ValueError):
                service.create({"usuario_id": 999, "nombre_archivo": "apunte.pdf"})

    def test_get_document_by_id_returns_document(self):
        mock_session = MagicMock()
        
        with patch("app.services.document_service.DocumentRepository") as doc_repo_cls:
            doc_repo = doc_repo_cls.return_value
            doc_repo.get_by_id.return_value = {"id": 10, "nombre_archivo": "apunte.pdf"}
            service = DocumentService(mock_session)

            document = service.get_by_id(10)

            self.assertEqual(document["id"], 10)
            doc_repo.get_by_id.assert_called_once_with(10)

    def test_get_document_by_id_raises_error_when_not_found(self):
        mock_session = MagicMock()
        
        with patch("app.services.document_service.DocumentRepository") as doc_repo_cls:
            doc_repo = doc_repo_cls.return_value
            doc_repo.get_by_id.return_value = None
            service = DocumentService(mock_session)

            with self.assertRaises(ValueError):
                service.get_by_id(999)

    def test_update_document_returns_updated_document(self):
        mock_session = MagicMock()
        
        with patch("app.services.document_service.DocumentRepository") as doc_repo_cls:
            doc_repo = doc_repo_cls.return_value
            doc_repo.get_by_id.return_value = {"id": 10, "nombre_archivo": "apunte.pdf"}
            doc_repo.update.return_value = {
                "id": 10,
                "nombre_archivo": "apunte_actualizado.pdf",
                "texto_extraido": "texto",
            }
            service = DocumentService(mock_session)

            updated = service.update(
                10,
                {
                    "nombre_archivo": "apunte_actualizado.pdf",
                    "texto_extraido": "texto",
                },
            )

            self.assertEqual(updated["nombre_archivo"], "apunte_actualizado.pdf")
            doc_repo.update.assert_called_once_with(
                10,
                nombre_archivo="apunte_actualizado.pdf",
                ruta_archivo=None,
                texto_extraido="texto",
            )

    def test_delete_document_returns_true_when_deleted(self):
        mock_session = MagicMock()
        
        with patch("app.services.document_service.DocumentRepository") as doc_repo_cls:
            doc_repo = doc_repo_cls.return_value
            doc_repo.get_by_id.return_value = {"id": 10, "nombre_archivo": "apunte.pdf"}
            doc_repo.delete.return_value = True
            service = DocumentService(mock_session)

            deleted = service.delete(10)

            self.assertTrue(deleted)
            doc_repo.delete.assert_called_once_with(10)


if __name__ == "__main__":
    unittest.main()
