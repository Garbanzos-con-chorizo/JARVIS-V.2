import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from jarvis_core import database


def test_database_roundtrip(tmp_path):
    db_file = tmp_path / "test.db"
    database.init_db(db_path=str(db_file))
    database.insert_message("user", "hello", db_path=str(db_file))
    database.insert_message("assistant", "hi", db_path=str(db_file))
    rows = database.fetch_last_messages(2, db_path=str(db_file))
    assert rows[0] == ("assistant", "hi")
    assert rows[1] == ("user", "hello")

