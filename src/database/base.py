import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

# Build MySQL URL from environment variables for security
DATABASE_URL = (
    f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# engine is the actual connection to the database
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Vital for MySQL stability
    pool_size=10,
    max_overflow=20,
)

# SessionLocal is a factory for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Re-add Base here so all models can inherit from it
Base = declarative_base()
