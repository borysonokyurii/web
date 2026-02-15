import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    db_user = os.getenv('DB_USER', 'user')
    db_password = os.getenv('DB_PASSWORD', 'password')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'db')
    DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

try:
    # pool_pre_ping=True ensures connections are checked before use
    # pool_recycle=1800 recycles connections every 30 mins to avoid potential timeouts
    engine = create_engine(
        DATABASE_URL, 
        pool_pre_ping=True,
        pool_recycle=1800
    )
except Exception as e:
    print(f"Failed to create engine: {e}")
    engine = None

def get_db():
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()