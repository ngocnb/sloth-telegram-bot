from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from src.database.base import Base


class GoldPrice(Base):
    __tablename__ = "gold_prices"
    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_name = Column(String(255))  # e.g., "VÀNG MIẾNG VRTL"
    buy_price = Column(Float)
    sell_price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
