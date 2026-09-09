"""Copy legacy SQLite rows into a configured MySQL database.

The script is intentionally conservative: it copies only rows whose target
tables are empty and leaves the legacy SQLite file untouched.
"""
import os
import sqlite3
from pathlib import Path
from app.main import engine, init_db, users, contents, events, feedbacks

source = Path(os.getenv("CAMPUS_DB", Path(__file__).resolve().parents[1] / "campus.db"))
if not engine.url.get_backend_name().startswith("mysql"):
    raise SystemExit("请先配置 MYSQL_PASSWORD 或 DATABASE_URL 为 MySQL")
init_db()
if not source.exists():
    raise SystemExit(f"SQLite 文件不存在: {source}")
with sqlite3.connect(source) as old, engine.begin() as new:
    old.row_factory = sqlite3.Row
    for table, columns in [(users, ["id", "name", "role", "college", "major", "grade", "interests", "created_at"]), (contents, ["id", "title", "body", "content_type", "publisher_id", "target_roles", "target_colleges", "target_grades", "tags", "start_time", "end_time", "publish_time", "status"]), (events, ["id", "user_id", "content_id", "event_type", "source", "timestamp"]), (feedbacks, ["id", "user_id", "content_id", "feedback_type", "reason", "created_at"])]:
        if new.execute(table.select().limit(1)).first():
            continue
        rows = old.execute(f"SELECT {','.join(columns)} FROM {table.name}").fetchall()
        if rows:
            new.execute(table.insert(), [dict(row) for row in rows])
            print(f"migrated {table.name}: {len(rows)}")
print("Migration complete")
