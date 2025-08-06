import threading
from pathlib import Path

from storage import save_project, load_project, close


def _worker(db: Path, value: int):
    save_project({"v": value}, db)
    assert load_project(db)["v"] == value


def test_thread_safe(tmp_path):
    db = tmp_path / "project.db"
    threads = [threading.Thread(target=_worker, args=(db, i)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    # After all threads, database should contain last written value (0-4)
    assert load_project(db)["v"] in range(5)
    close()
