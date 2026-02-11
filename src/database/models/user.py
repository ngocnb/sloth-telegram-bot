from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from src.database.base import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(255), nullable=True)
    joined_at = Column(DateTime, default=datetime.utcnow)
