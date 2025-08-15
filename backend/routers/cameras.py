# backend/routers/cameras.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, models, schemas
from ..camera_manager import start_camera, stop_camera

router = APIRouter(prefix="/api/cameras", tags=["cameras"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.CameraOut)
def add_camera(cam: schemas.CameraCreate, db: Session = Depends(get_db)):
    camera = models.Camera(name=cam.name, rtsp_url=cam.rtsp_url)
    db.add(camera)
    db.commit()
    db.refresh(camera)
    # start worker
    start_camera(camera.id, camera.rtsp_url)
    return camera

@router.get("/", response_model=list[schemas.CameraOut])
def list_cameras(db: Session = Depends(get_db)):
    return db.query(models.Camera).all()

@router.delete("/{cam_id}")
def delete_camera(cam_id: int, db: Session = Depends(get_db)):
    cam = db.query(models.Camera).get(cam_id)
    if not cam:
        raise HTTPException(status_code=404, detail="camera not found")
    stop_camera(cam.id)
    db.delete(cam)
    db.commit()
    return {"ok": True}
