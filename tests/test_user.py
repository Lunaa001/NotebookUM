import unittest
from unittest.mock import patch, MagicMock

from app.services.user_service import UserService


class TestUser(unittest.TestCase):
    @patch("app.services.user_service.hash_password", return_value="hashed-password")
    def test_create_user_returns_created_user(self, hash_mock):
        mock_session = MagicMock()
        
        with patch("app.services.user_service.UserRepository") as repo_cls:
            repo = repo_cls.return_value
            repo.get_by_email.return_value = None
            repo.create.return_value = {
                "id": 1,
                "nombre": "Ana",
                "email": "ana@example.com",
            }
            service = UserService(mock_session)

            created = service.create(
                {
                    "nombre": "Ana",
                    "email": "ana@example.com",
                    "password": "secreta123",
                }
            )

            self.assertEqual(created["id"], 1)
            hash_mock.assert_called_once_with("secreta123")
            repo.create.assert_called_once_with(
                nombre="Ana",
                email="ana@example.com",
                password_hash="hashed-password",
            )

    def test_create_user_requires_nombre_email_password(self):
        mock_session = MagicMock()
        service = UserService(mock_session)

        with self.assertRaises(ValueError):
            service.create({"nombre": "Ana"})

    def test_create_user_rejects_duplicate_email(self):
        mock_session = MagicMock()
        
        with patch("app.services.user_service.UserRepository") as repo_cls:
            repo = repo_cls.return_value
            repo.get_by_email.return_value = {"id": 99, "email": "ana@example.com"}
            service = UserService(mock_session)

            with self.assertRaises(ValueError):
                service.create(
                    {
                        "nombre": "Ana",
                        "email": "ana@example.com",
                        "password": "secreta123",
                    }
                )
            repo.create.assert_not_called()

    def test_get_user_by_id_returns_user(self):
        mock_session = MagicMock()
        
        with patch("app.services.user_service.UserRepository") as repo_cls:
            repo = repo_cls.return_value
            repo.get_by_id.return_value = {"id": 1, "nombre": "Ana"}
            service = UserService(mock_session)

            user = service.get_by_id(1)

            self.assertEqual(user["id"], 1)
            repo.get_by_id.assert_called_once_with(1)

    def test_get_user_by_id_raises_error_when_not_found(self):
        mock_session = MagicMock()
        
        with patch("app.services.user_service.UserRepository") as repo_cls:
            repo = repo_cls.return_value
            repo.get_by_id.return_value = None
            service = UserService(mock_session)

            with self.assertRaises(ValueError):
                service.get_by_id(999)

    @patch("app.services.user_service.hash_password", return_value="new-hash")
    def test_update_user_updates_data_and_returns_user(self, hash_mock):
        mock_session = MagicMock()
        
        with patch("app.services.user_service.UserRepository") as repo_cls:
            repo = repo_cls.return_value
            repo.get_by_id.return_value = {"id": 1, "nombre": "Ana", "email": "ana@example.com"}
            repo.update.return_value = {"id": 1, "nombre": "Ana Maria", "email": "ana@example.com"}
            service = UserService(mock_session)

            updated = service.update(
                1,
                {
                    "nombre": "Ana Maria",
                    "email": "ana@example.com",
                    "password": "nueva123",
                },
            )

            self.assertEqual(updated["nombre"], "Ana Maria")
            hash_mock.assert_called_once_with("nueva123")
            repo.update.assert_called_once_with(
                1,
                nombre="Ana Maria",
                email="ana@example.com",
                password_hash="new-hash",
            )

    def test_delete_user_is_not_allowed(self):
        mock_session = MagicMock()
        service = UserService(mock_session)

        with self.assertRaises(ValueError):
            service.delete(1)


if __name__ == "__main__":
    unittest.main()
