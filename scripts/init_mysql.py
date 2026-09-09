import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.main import engine, init_db
if not engine.url.get_backend_name().startswith('mysql'):
    raise SystemExit('请设置 MYSQL_PASSWORD 或 DATABASE_URL 为 MySQL 连接')
init_db(); print('MySQL schema initialized:', engine.url)
