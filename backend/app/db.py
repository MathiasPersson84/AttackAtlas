from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATA_DIR = Path(__import__('os').environ.get('ATTACKATLAS_DATA_DIR', '/data'))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / 'attackatlas.db'

engine = create_engine(f'sqlite:///{DB_PATH}', connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def apply_lightweight_migrations():
    """Small additive SQLite migrations for the local-first MVP."""
    with engine.begin() as conn:
        tables = {row[0] for row in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))}
        if 'projects' in tables:
            project_cols = {row[1] for row in conn.execute(text('PRAGMA table_info(projects)'))}
            if 'notes' not in project_cols:
                conn.execute(text("ALTER TABLE projects ADD COLUMN notes TEXT DEFAULT ''"))
        if 'hosts' not in tables:
            return
        cols = {row[1] for row in conn.execute(text('PRAGMA table_info(hosts)'))}
        additions = {
            'domain': "ALTER TABLE hosts ADD COLUMN domain VARCHAR(255) DEFAULT ''",
            'os_family': "ALTER TABLE hosts ADD COLUMN os_family VARCHAR(32) DEFAULT 'unknown'",
            'device_type': "ALTER TABLE hosts ADD COLUMN device_type VARCHAR(32) DEFAULT 'host'",
            'sort_order': "ALTER TABLE hosts ADD COLUMN sort_order INTEGER DEFAULT 0 NOT NULL",
            'pos_x': "ALTER TABLE hosts ADD COLUMN pos_x INTEGER DEFAULT 80 NOT NULL",
            'pos_y': "ALTER TABLE hosts ADD COLUMN pos_y INTEGER DEFAULT 80 NOT NULL",
        }
        for name, ddl in additions.items():
            if name not in cols:
                conn.execute(text(ddl))
        if 'services' in tables:
            service_cols = {row[1] for row in conn.execute(text('PRAGMA table_info(services)'))}
            if 'script_output' not in service_cols:
                conn.execute(text("ALTER TABLE services ADD COLUMN script_output TEXT DEFAULT ''"))
            if 'raw_output' not in service_cols:
                conn.execute(text("ALTER TABLE services ADD COLUMN raw_output TEXT DEFAULT ''"))
        if 'edges' in tables:
            edge_cols = {row[1] for row in conn.execute(text('PRAGMA table_info(edges)'))}
            if 'directed' not in edge_cols:
                conn.execute(text("ALTER TABLE edges ADD COLUMN directed INTEGER DEFAULT 1 NOT NULL"))
        if 'accounts' in tables:
            account_cols = {row[1] for row in conn.execute(text('PRAGMA table_info(accounts)'))}
            if 'host_id' not in account_cols:
                conn.execute(text("ALTER TABLE accounts ADD COLUMN host_id INTEGER"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_accounts_host_id ON accounts(host_id)"))
        if 'credentials' in tables:
            cred_cols = {row[1] for row in conn.execute(text('PRAGMA table_info(credentials)'))}
            if 'host_id' not in cred_cols:
                conn.execute(text("ALTER TABLE credentials ADD COLUMN host_id INTEGER"))
            if 'notes' not in cred_cols:
                conn.execute(text("ALTER TABLE credentials ADD COLUMN notes TEXT DEFAULT ''"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
