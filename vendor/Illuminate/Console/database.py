import os
import re
import sys
import importlib.util
from vendor.Illuminate.Support.Env import Env
from sqlalchemy import create_engine, text, MetaData
from datetime import datetime

BASE_DIR = sys.path[0]

def get_database_url():
    """
    Generate database URL based on DB_CONNECTION environment variable.
    Supports: sqlite, mysql, pgsql (PostgreSQL)
    """
    conn = Env.get("DB_CONNECTION", "sqlite")

    if conn == "sqlite":
        db = Env.get("DB_DATABASE", "database.sqlite")
        return f"sqlite:///{db}"

    elif conn == "mysql":
        user = Env.get("DB_USERNAME", "root")
        pwd = Env.get("DB_PASSWORD", "")
        host = Env.get("DB_HOST", "127.0.0.1")
        port = Env.get("DB_PORT", "3306")
        db = Env.get("DB_DATABASE", "test")
        return f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}"

    elif conn == "pgsql" or conn == "postgresql":
        user = Env.get("DB_USERNAME", "postgres")
        pwd = Env.get("DB_PASSWORD", "")
        host = Env.get("DB_HOST", "127.0.0.1")
        port = Env.get("DB_PORT", "5432")
        db = Env.get("DB_DATABASE", "postgres")
        return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"

    else:
        raise Exception(f"Unsupported DB_CONNECTION: {conn}. Supported: sqlite, mysql, pgsql")

def get_engine():
    db_url = get_database_url()
    engine = create_engine(db_url, echo=False)
    return engine

def create_database_if_not_exists():
    conn_type = Env.get("DB_CONNECTION", "sqlite")
    
    # Skip for PostgreSQL on cloud (Supabase) - database already exists
    if conn_type in ("pgsql", "postgresql"):
        host = Env.get("DB_HOST", "127.0.0.1")
        if "supabase" in host or "pooler" in host:
            print("ℹ️  Using cloud PostgreSQL - skipping database creation")
            return
    
    # Only try to create database for MySQL
    if conn_type == "mysql":
        db_name = Env.get("DB_DATABASE", "laravelfastapi")
        user = Env.get("DB_USERNAME", "root")
        password = Env.get("DB_PASSWORD", "")
        host = Env.get("DB_HOST", "127.0.0.1")
        port = Env.get("DB_PORT", "3306")

        engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/")
        with engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
            print(f"✅ Database `{db_name}` ready.")

def ensure_migrations_table(engine):
    conn_type = Env.get("DB_CONNECTION", "sqlite")
    
    with engine.connect() as conn:
        if conn_type == "mysql":
            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS migrations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                migration VARCHAR(255) NOT NULL,
                batch INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """))
        elif conn_type in ("pgsql", "postgresql"):
            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS migrations (
                id SERIAL PRIMARY KEY,
                migration VARCHAR(255) NOT NULL,
                batch INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """))
        elif conn_type == "sqlite":
            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration VARCHAR(255) NOT NULL,
                batch INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """))
        conn.commit()

def normalize_migration(filename: str) -> str:
    """
    Ambil core migration name tanpa timestamp.
    contoh:
      2025_09_28_035906_create_todos_table.py -> create_todos_table
    """
    match = re.match(r"^\d{4}_\d{2}_\d{2}_\d{6}_(.*)\.py$", filename)
    return match.group(1) if match else filename

def get_ran_migrations(engine):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT migration FROM migrations"))
        return [row[0] for row in result]

def log_migration(engine, migration, batch):
    with engine.connect() as conn:
        conn.execute(text(
            "INSERT INTO migrations (migration, batch) VALUES (:migration, :batch)"
        ), {"migration": migration, "batch": batch})
        conn.commit()

def migrate():
    db_name = Env.get("DB_DATABASE", "laravelfastapi")
    conn_type = Env.get("DB_CONNECTION", "sqlite")

    try:
        engine = get_engine()
        ensure_migrations_table(engine)
    except Exception as e:
        print(f"⚠️ Error connecting to database: {e}")
        
        # Only prompt for database creation for MySQL
        if conn_type == "mysql":
            choice = input(f"❌ Database `{db_name}` belum ada. Buat sekarang? [y/N]: ").lower()
            if choice == "y":
                create_database_if_not_exists()
                engine = get_engine()
                ensure_migrations_table(engine)
            else:
                print("⚠️ Migration dibatalkan karena database tidak ada.")
                return
        else:
            print(f"❌ Cannot connect to database. Please check your .env configuration.")
            print(f"   DB_CONNECTION: {conn_type}")
            print(f"   DB_HOST: {Env.get('DB_HOST')}")
            print(f"   DB_PORT: {Env.get('DB_PORT')}")
            print(f"   DB_DATABASE: {db_name}")
            return

    migrations_path = os.path.join(BASE_DIR, "database", "migrations")
    if not os.path.exists(migrations_path):
        print("❌ No migrations directory found.")
        return

    ran = get_ran_migrations(engine)
    files = sorted(os.listdir(migrations_path))

    new_migrations = []
    for f in files:
        if f.endswith(".py"):
            core = normalize_migration(f)
            if core not in ran:
                new_migrations.append((f, core))

    if not new_migrations:
        print("✨ Nothing to migrate.")
        return

    # Cari batch terakhir
    with engine.connect() as conn:
        result = conn.execute(text("SELECT MAX(batch) FROM migrations")).fetchone()
        batch = (result[0] or 0) + 1

    for file, core in new_migrations:
        migration_name = file.replace(".py", "")
        file_path = os.path.join(migrations_path, file)

        spec = importlib.util.spec_from_file_location(migration_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check if module has Migration class (new style)
        if hasattr(module, "Migration"):
            print(f"🔼 Running migration: {migration_name}")
            migration = module.Migration()
            migration.up(engine)
            log_migration(engine, core, batch)
        # Or check if module has up() function directly (old style)
        elif hasattr(module, "up"):
            print(f"🔼 Running migration: {migration_name}")
            module.up(engine)
            log_migration(engine, core, batch)
        else:
            print(f"⚠️ No up() method or Migration class in {migration_name}")
