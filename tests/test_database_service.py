"""
Tests for backend/services/database_service.py.

Run from the repository root:
    python -m unittest tests.test_database_service -v

No live database is required. The live Supabase test runs only when
DATABASE_URL is set, and skips otherwise.
"""

import contextlib
import io
import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from backend.services import database_service


REPO_ROOT = Path(__file__).resolve().parent.parent
LIVE_DATABASE_URL = os.getenv("DATABASE_URL")


class StorageTestCase(unittest.TestCase):
    """Isolates each test: temp fallback file, fresh engine, chosen URL."""

    database_url = ""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        temp_path = Path(self.temp_dir.name)

        self.patches = [
            mock.patch.object(
                database_service,
                "FALLBACK_FILE",
                temp_path / "fallback.json",
            ),
            mock.patch.dict(os.environ, {"DATABASE_URL": self.database_url}),
        ]

        for patch in self.patches:
            patch.start()

        self._reset_engine()

    def tearDown(self):
        self._reset_engine()

        for patch in reversed(self.patches):
            patch.stop()

        self.temp_dir.cleanup()

    def _reset_engine(self):
        if database_service._engine is not None:
            database_service._engine.dispose()

        database_service._engine = None
        database_service._initialized = False


class TestValidationAndFallback(StorageTestCase):
    """DATABASE_URL unset: everything goes to the local fallback file."""

    def test_save_rejects_empty_input(self):
        for bad_value in ["", "   ", "\n\t", None, 123]:
            with self.assertRaises(ValueError):
                database_service.save_information(bad_value)

    def test_get_information_returns_list_of_str(self):
        self.assertEqual(database_service.get_information(), [])

        database_service.save_information("  Deadline moved to May 3  ")
        database_service.save_information("Sophie now owns SEC-210")

        information = database_service.get_information()

        self.assertIsInstance(information, list)
        self.assertTrue(all(isinstance(item, str) for item in information))
        self.assertEqual(
            information,
            ["Deadline moved to May 3", "Sophie now owns SEC-210"],
        )

    def test_records_have_timestamps(self):
        record = database_service.save_information("New risk identified")

        self.assertEqual(record["storage"], "local")
        self.assertIn("created_at", record)
        self.assertTrue(database_service.FALLBACK_FILE.exists())

    def test_corrupt_fallback_file_is_not_overwritten(self):
        database_service.FALLBACK_FILE.write_text("{not json", encoding="utf-8")

        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(RuntimeError):
                database_service.save_information("Something new")

        self.assertEqual(
            database_service.FALLBACK_FILE.read_text(encoding="utf-8"),
            "{not json",
        )


class TestDatabaseFailure(StorageTestCase):
    """DATABASE_URL points at nothing: must fall back, not crash or leak."""

    database_url = "postgres://nova_user:SuperSecretPw123@127.0.0.1:1/nova"

    def test_unreachable_database_falls_back_without_leaking(self):
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            record = database_service.save_information("Saved during outage")
            information = database_service.get_information()

        self.assertEqual(record["storage"], "local")
        self.assertEqual(information, ["Saved during outage"])
        self.assertIn("NOVA storage", output.getvalue())
        self.assertNotIn("SuperSecretPw123", output.getvalue())
        self.assertNotIn("nova_user", output.getvalue())

    def test_postgres_url_is_normalized(self):
        self.assertTrue(
            database_service.get_database_url().startswith(
                "postgresql+psycopg2://"
            )
        )


class TestSqlDatabase(StorageTestCase):
    """Exercises the real SQL path against a throwaway SQLite database."""

    def setUp(self):
        self.sqlite_dir = tempfile.TemporaryDirectory()
        self.database_url = f"sqlite:///{self.sqlite_dir.name}/nova.db"
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.sqlite_dir.cleanup()

    def test_save_and_get_through_database(self):
        first = database_service.save_information("Budget approved")
        database_service.save_information("Launch moved to June")

        self.assertEqual(first["storage"], "database")
        self.assertEqual(
            database_service.get_information(),
            ["Budget approved", "Launch moved to June"],
        )
        self.assertFalse(database_service.FALLBACK_FILE.exists())

    def test_database_and_fallback_records_are_merged(self):
        database_service.save_information("Stored in database")

        with mock.patch.object(
            database_service, "init_database", return_value=False
        ):
            database_service.save_information("Stored during outage")

        self.assertEqual(
            sorted(database_service.get_information()),
            ["Stored during outage", "Stored in database"],
        )


@unittest.skipUnless(LIVE_DATABASE_URL, "DATABASE_URL not set")
class TestLiveDatabase(StorageTestCase):
    """Round trip against the real Supabase database."""

    database_url = LIVE_DATABASE_URL or ""

    def test_live_round_trip(self):
        self.assertTrue(database_service.init_database())

        marker = f"[unittest] live round trip {os.getpid()}"
        record = database_service.save_information(marker)

        try:
            self.assertEqual(record["storage"], "database")
            self.assertIn(marker, database_service.get_information())
        finally:
            with database_service._get_engine().begin() as connection:
                connection.execute(
                    database_service.information_table.delete().where(
                        database_service.information_table.c.id == record["id"]
                    )
                )


class TestCompatibility(unittest.TestCase):
    def test_answer_question_interface_still_imports(self):
        import inspect

        from backend.services.ask_nova import (
            answer_question,
            answer_question_with_database,
        )

        parameters = list(inspect.signature(answer_question).parameters)
        self.assertEqual(parameters, ["question", "additional_information"])
        self.assertTrue(callable(answer_question_with_database))

    def test_no_hardcoded_credentials(self):
        source = (
            REPO_ROOT / "backend" / "services" / "database_service.py"
        ).read_text(encoding="utf-8")

        self.assertIsNone(re.search(r"postgres(ql)?://\S+:\S+@", source))
        self.assertNotIn("supabase.co", source)
        self.assertIsNone(re.search(r"password\s*=", source, re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
