import importlib
import os
import tempfile
import unittest
from pathlib import Path


class DatabaseTests(unittest.TestCase):
    def test_lead_creation_and_deletion(self):
        with tempfile.TemporaryDirectory() as temp:
            os.environ["DB_PATH"] = str(Path(temp) / "leads.db")
            import database
            importlib.reload(database)
            database.initialize()
            lead_id = database.save_lead(123, "demo_user", "Alex", "+1 555 123 4567", "Full detailing", "Camry")
            self.assertEqual(lead_id, 1)
            with database.connect() as conn:
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0], 1)
            self.assertEqual(database.delete_user_leads(123), 1)
            self.assertEqual(database.delete_user_leads(123), 0)


if __name__ == "__main__":
    unittest.main()
