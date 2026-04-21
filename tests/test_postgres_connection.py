import os
import unittest

import psycopg


def _postgres_dsn_from_env() -> str | None:
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        return None

    if database_url.startswith("postgresql+psycopg://"):
        return "postgresql://" + database_url.split("://", 1)[1]

    if database_url.startswith("postgres://"):
        return "postgresql://" + database_url.split("://", 1)[1]

    if database_url.startswith("postgresql://"):
        return database_url

    return None


class TestPostgresConnection(unittest.TestCase):
    def test_can_connect_and_run_select_1(self):
        dsn = _postgres_dsn_from_env()
        self.assertIsNotNone(
            dsn,
            "DATABASE_URL no apunta a PostgreSQL. Define DATABASE_URL con esquema postgresql:// o postgresql+psycopg://",
        )

        with psycopg.connect(dsn, connect_timeout=5) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()

        self.assertEqual(result[0], 1)

    def test_can_create_insert_and_read_data(self):
        dsn = _postgres_dsn_from_env()
        self.assertIsNotNone(
            dsn,
            "DATABASE_URL no apunta a PostgreSQL. Define DATABASE_URL con esquema postgresql:// o postgresql+psycopg://",
        )

        table_name = "_test_postgres_connection"

        with psycopg.connect(dsn, connect_timeout=5, autocommit=True) as connection:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                    cursor.execute(
                        f"""
                        CREATE TABLE {table_name} (
                            id SERIAL PRIMARY KEY,
                            content TEXT NOT NULL
                        )
                        """
                    )
                    cursor.execute(
                        f"INSERT INTO {table_name} (content) VALUES (%s) RETURNING id, content",
                        ("registro de prueba",),
                    )
                    row = cursor.fetchone()
                    self.assertIsNotNone(row)
                    self.assertEqual(row[1], "registro de prueba")

                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    total = cursor.fetchone()[0]
                    self.assertEqual(total, 1)
                finally:
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")


if __name__ == "__main__":
    unittest.main()