# backend/routers/history.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import database, models, schemas

router = APIRouter(prefix="/api/history", tags=["history"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[schemas.HistoryOut])
def list_history(db: Session = Depends(get_db)):
    return db.query(models.History).order_by(models.History.id.desc()).limit(500).all()
