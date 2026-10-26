from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from database import engine, get_db, Base
import models, schemas

# Создаем таблицы при запуске
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Auction API")


@app.post("/api/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email уже занят")


@app.post("/api/login")
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.execute(select(models.User).where(models.User.email == user.email)).scalar()
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    return {"id": db_user.id, "name": db_user.name, "role": db_user.role}


@app.get("/api/lots", response_model=List[schemas.LotResponse])
def get_lots(search: Optional[str] = None, db: Session = Depends(get_db)):
    stmt = select(models.Lot)
    if search:
        # ilike - поиск без учета регистра
        stmt = stmt.where(models.Lot.title.ilike(f"%{search}%"))
    return db.execute(stmt).scalars().all()


@app.get("/api/lots/{lot_id}", response_model=schemas.LotResponse)
def get_lot(lot_id: int, db: Session = Depends(get_db)):
    lot = db.get(models.Lot, lot_id)
    if not lot:
        raise HTTPException(status_code=404, detail="Лот не найден")
    return lot


@app.post("/api/lots", response_model=schemas.LotResponse)
def create_lot(lot: schemas.LotCreate, db: Session = Depends(get_db)):
    db_lot = models.Lot(**lot.model_dump())
    db.add(db_lot)
    db.commit()
    db.refresh(db_lot)
    return db_lot


@app.put("/api/lots/{lot_id}", response_model=schemas.LotResponse)
def update_lot(lot_id: int, lot_data: schemas.LotUpdate, db: Session = Depends(get_db)):
    db_lot = db.get(models.Lot, lot_id)
    if not db_lot:
        raise HTTPException(status_code=404, detail="Лот не найден")
    db_lot.title = lot_data.title
    db_lot.price = lot_data.price
    db_lot.step = lot_data.step
    db.commit()
    return db_lot


@app.delete("/api/lots/{lot_id}")
def delete_lot(lot_id: int, db: Session = Depends(get_db)):
    db_lot = db.get(models.Lot, lot_id)
    if not db_lot:
        raise HTTPException(status_code=404, detail="Лот не найден")
    db.delete(db_lot)
    db.commit()
    return {"message": "Удалено"}


@app.post("/api/lots/{lot_id}/bids")
def make_bid(lot_id: int, bid: schemas.BidCreate, db: Session = Depends(get_db)):
    lot = db.get(models.Lot, lot_id)
    if not lot:
        raise HTTPException(status_code=404, detail="Лот не найден")
    if bid.amount < lot.price + lot.step:
        raise HTTPException(status_code=400, detail=f"Ставка должна быть не менее {lot.price + lot.step}")

    lot.price = bid.amount
    db_bid = models.Bid(amount=bid.amount, user_id=bid.user_id, lot_id=lot_id)
    db.add(db_bid)

    notif = models.Notification(user_id=lot.seller_id, message=f"Новая ставка {bid.amount} на '{lot.title}'")
    db.add(notif)

    db.commit()
    return {"message": "Ставка принята"}


@app.get("/api/users/{user_id}/notifications", response_model=List[schemas.NotificationResponse])
def get_notifications(user_id: int, db: Session = Depends(get_db)):
    return db.execute(select(models.Notification).where(models.Notification.user_id == user_id)).scalars().all()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)