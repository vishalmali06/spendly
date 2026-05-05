import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    monkeypatch.setattr("database.db.DB_PATH", str(db_file))

    from database.db import init_db
    import app as app_module

    init_db()
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c
