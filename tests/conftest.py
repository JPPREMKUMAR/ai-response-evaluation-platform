import os
import tempfile
import pytest

@pytest.fixture(autouse=True)
def isolated_db(monkeypatch):
    from app import storage
    from app import main
    handle, path = tempfile.mkstemp(suffix=".db")
    os.close(handle)
    monkeypatch.setattr(storage, "DB_PATH", __import__("pathlib").Path(path))
    monkeypatch.setattr(main, "rubric", main.Rubric())
    storage.initialize()
    yield
    os.unlink(path)
