# backend/schemas.py
from pydantic import BaseModel
from typing import Optional
import datetime

class PersonOut(BaseModel):
    id: int
    name: str
    image_path: Optional[str]
    class Config:
        orm_mode = True

class CameraCreate(BaseModel):
    name: str
    rtsp_url: str

class CameraOut(CameraCreate):
    id: int
    class Config:
        orm_mode = True

class HistoryOut(BaseModel):
    id: int
    camera_id: int
    person_id: Optional[int]
    score: Optional[float]
    snapshot_path: str
    timestamp: datetime.datetime
    class Config:
        orm_mode = True
