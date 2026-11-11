from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_name = Column(String)
    phone = Column(String)

    items = relationship("Item", back_populates="shop")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    name = Column(String, nullable=False)
    cost_price = Column(Float, nullable=False)      # what it costs the shop to make one
    selling_price = Column(Float, nullable=False)   # what the customer pays for one

    shop = relationship("Shop", back_populates="items")
    logs = relationship("DailyLog", back_populates="item")


class DailyLog(Base):
    __tablename__ = "daily_logs"
    # One row per item per day, so the same day can't be logged twice by accident
    __table_args__ = (UniqueConstraint("item_id", "date", name="one_log_per_item_per_day"),)

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    date = Column(Date, nullable=False)
    quantity_made = Column(Integer, nullable=False)
    quantity_sold = Column(Integer, nullable=False)
    quantity_wasted = Column(Integer, nullable=False)

    item = relationship("Item", back_populates="logs")
