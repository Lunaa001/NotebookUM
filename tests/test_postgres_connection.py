import os
import unittest

import psycopg


def _postgres_dsn_from_env() -> str | None:
    database_url = os.getenv("DATABASE_URL", "")
    if database_url:
        if database_url.startswith("postgresql+psycopg://"):
            return "postgresql://" + database_url.split("://", 1)[1]

        if database_url.startswith("postgres://"):
            return "postgresql://" + database_url.split("://", 1)[1]

        if database_url.startswith("postgresql://"):
            return database_url

        return None

    host = os.getenv("PGHOST") or os.getenv("POSTGRES_HOST")
    user = os.getenv("PGUSER") or os.getenv("POSTGRES_USER")
    password = os.getenv("PGPASSWORD") or os.getenv("POSTGRES_PASSWORD")
    database = os.getenv("PGDATABASE") or os.getenv("POSTGRES_DB")
    port = os.getenv("PGPORT", "5432")

    if not all([host, user, password, database]):
        return None

    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def _connect_or_skip(dsn: str, *, autocommit: bool = False):
    try:
        return psycopg.connect(dsn, connect_timeout=5, autocommit=autocommit)
    except psycopg.OperationalError as exc:
        raise unittest.SkipTest(f"PostgreSQL no disponible para pruebas de integración: {exc}") from exc


class TestPostgresConnection(unittest.TestCase):
    def test_can_connect_and_run_select_1(self):
        dsn = _postgres_dsn_from_env()
        if dsn is None:
            raise unittest.SkipTest(
                "Sin configuración PostgreSQL. Define DATABASE_URL o PGHOST/PGUSER/PGPASSWORD/PGDATABASE."
            )

        with _connect_or_skip(dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()

        self.assertEqual(result[0], 1)

    def test_can_create_insert_and_read_data(self):
        dsn = _postgres_dsn_from_env()
        if dsn is None:
            raise unittest.SkipTest(
                "Sin configuración PostgreSQL. Define DATABASE_URL o PGHOST/PGUSER/PGPASSWORD/PGDATABASE."
            )

        table_name = "_test_postgres_connection"

        with _connect_or_skip(dsn, autocommit=True) as connection:
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