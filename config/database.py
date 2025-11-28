import os
from sqlalchemy import create_engine

def get_database_url():
    """
    Generate database URL based on DB_CONNECTION environment variable.
    Supports: sqlite, mysql, pgsql (PostgreSQL)
    """
    conn = os.getenv("DB_CONNECTION", "sqlite")

    if conn == "sqlite":
        db = os.getenv("DB_DATABASE", "database.sqlite")
        return f"sqlite:///{db}"

    elif conn == "mysql":
        user = os.getenv("DB_USERNAME", "root")
        pwd = os.getenv("DB_PASSWORD", "")
        host = os.getenv("DB_HOST", "127.0.0.1")
        port = os.getenv("DB_PORT", "3306")
        db = os.getenv("DB_DATABASE", "test")
        return f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}"

    elif conn == "pgsql" or conn == "postgresql":
        user = os.getenv("DB_USERNAME", "postgres")
        pwd = os.getenv("DB_PASSWORD", "")
        host = os.getenv("DB_HOST", "127.0.0.1")
        port = os.getenv("DB_PORT", "5432")
        db = os.getenv("DB_DATABASE", "postgres")
        return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"

    else:
        raise Exception(f"Unsupported DB_CONNECTION: {conn}. Supported: sqlite, mysql, pgsql")

def get_engine():
    """
    Create SQLAlchemy engine based on database configuration.
    """
    db_url = get_database_url()
    return create_engine(db_url)
