from datetime import date
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse

from app import models
from app.database import engine, get_db

# Create the tables in waste_tracker.db if they don't exist yet
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Food Waste Tracker")


# ---------- Request shapes (what the API expects to receive) ----------

class ShopIn(BaseModel):
    name: str
    owner_name: Optional[str] = None
    phone: Optional[str] = None


class ItemIn(BaseModel):
    shop_id: int
    name: str
    cost_price: float
    selling_price: float


class LogIn(BaseModel):
    item_id: int
    date: date
    quantity_made: int
    quantity_sold: int
    quantity_wasted: int


# ---------- Endpoints ----------

@app.post("/shops")
def create_shop(shop: ShopIn, db: Session = Depends(get_db)):
    new_shop = models.Shop(**shop.model_dump())
    db.add(new_shop)
    db.commit()
    db.refresh(new_shop)
    return {"id": new_shop.id, "name": new_shop.name}


@app.post("/items")
def create_item(item: ItemIn, db: Session = Depends(get_db)):
    if not db.get(models.Shop, item.shop_id):
        raise HTTPException(status_code=404, detail="Shop not found")
    new_item = models.Item(**item.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {"id": new_item.id, "name": new_item.name}


@app.post("/logs")
def create_log(log: LogIn, db: Session = Depends(get_db)):
    if not db.get(models.Item, log.item_id):
        raise HTTPException(status_code=404, detail="Item not found")

    already_logged = (
        db.query(models.DailyLog)
        .filter(models.DailyLog.item_id == log.item_id, models.DailyLog.date == log.date)
        .first()
    )
    if already_logged:
        raise HTTPException(status_code=400, detail="This item is already logged for that date")

    new_log = models.DailyLog(**log.model_dump())
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return {"id": new_log.id, "message": "Log saved"}


@app.get("/report")
def report(shop_id: int, db: Session = Depends(get_db)):
    """Totals per item: how much was made, sold and wasted, what the waste cost, and profit."""
    rows = (
        db.query(
            models.Item,
            func.coalesce(func.sum(models.DailyLog.quantity_made), 0),
            func.coalesce(func.sum(models.DailyLog.quantity_sold), 0),
            func.coalesce(func.sum(models.DailyLog.quantity_wasted), 0),
        )
        .outerjoin(models.DailyLog, models.DailyLog.item_id == models.Item.id)
        .filter(models.Item.shop_id == shop_id)
        .group_by(models.Item.id)
        .all()
    )

    result = []
    for item, made, sold, wasted in rows:
        result.append({
            "item": item.name,
            "made": made,
            "sold": sold,
            "wasted": wasted,
            "waste_percent": round(wasted / made * 100, 1) if made else 0,
            "waste_cost": round(wasted * item.cost_price, 2),
            "profit": round(sold * item.selling_price - made * item.cost_price, 2),
        })
    return result
@app.get("/items")
def list_items(shop_id: int, db: Session = Depends(get_db)):
    items = db.query(models.Item).filter(models.Item.shop_id == shop_id).all()
    return [{"id": i.id, "name": i.name} for i in items]


@app.get("/")
def home():
    return FileResponse("static/index.html")