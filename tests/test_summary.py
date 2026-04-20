import unittest
from unittest.mock import patch

from app.services.summary_service import SummaryService


class TestSummary(unittest.TestCase):
    @patch("app.services.summary_service.DocumentRepository")
    @patch("app.services.summary_service.SummaryRepository")
    def test_create_summary_returns_created_summary(self, summary_repo_cls, document_repo_cls):
        summary_repo = summary_repo_cls.return_value
        document_repo = document_repo_cls.return_value
        document_repo.exists.return_value = True
        summary_repo.create.return_value = {
            "id": 1,
            "documento_id": 10,
            "contenido": "Resumen inicial",
        }
        service = SummaryService()

        created = service.create({"documento_id": 10, "contenido": "Resumen inicial"})

        self.assertEqual(created["id"], 1)
        summary_repo.create.assert_called_once_with(
            documento_id=10,
            contenido="Resumen inicial",
        )

    def test_create_summary_requires_documento_id_and_contenido(self):
        service = SummaryService()

        with self.assertRaises(ValueError):
            service.create({"documento_id": 10})

    @patch("app.services.summary_service.DocumentRepository")
    @patch("app.services.summary_service.SummaryRepository")
    def test_create_summary_fails_when_document_not_exists(self, summary_repo_cls, document_repo_cls):
        document_repo = document_repo_cls.return_value
        document_repo.exists.return_value = False
        service = SummaryService()

        with self.assertRaises(ValueError):
            service.create({"documento_id": 999, "contenido": "Resumen"})
        summary_repo_cls.return_value.create.assert_not_called()

    @patch("app.services.summary_service.SummaryRepository")
    def test_get_summary_by_id_returns_summary(self, summary_repo_cls):
        summary_repo = summary_repo_cls.return_value
        summary_repo.get_by_id.return_value = {"id": 1, "documento_id": 10, "contenido": "Resumen"}
        service = SummaryService()

        summary = service.get_by_id(1)

        self.assertEqual(summary["id"], 1)
        summary_repo.get_by_id.assert_called_once_with(1)

    @patch("app.services.summary_service.SummaryRepository")
    def test_get_summary_by_id_raises_error_when_not_found(self, summary_repo_cls):
        summary_repo = summary_repo_cls.return_value
        summary_repo.get_by_id.return_value = None
        service = SummaryService()

        with self.assertRaises(ValueError):
            service.get_by_id(999)

    @patch("app.services.summary_service.SummaryRepository")
    def test_update_summary_returns_updated_summary(self, summary_repo_cls):
        summary_repo = summary_repo_cls.return_value
        summary_repo.get_by_id.return_value = {"id": 1, "documento_id": 10, "contenido": "Viejo"}
        summary_repo.update.return_value = {"id": 1, "documento_id": 10, "contenido": "Nuevo"}
        service = SummaryService()

        updated = service.update(1, {"contenido": "Nuevo"})

        self.assertEqual(updated["contenido"], "Nuevo")
        summary_repo.update.assert_called_once_with(1, contenido="Nuevo")

    @patch("app.services.summary_service.SummaryRepository")
    def test_delete_summary_returns_true_when_deleted(self, summary_repo_cls):
        summary_repo = summary_repo_cls.return_value
        summary_repo.get_by_id.return_value = {"id": 1, "documento_id": 10, "contenido": "Resumen"}
        summary_repo.delete.return_value = True
        service = SummaryService()

        deleted = service.delete(1)

        self.assertTrue(deleted)
        summary_repo.delete.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
