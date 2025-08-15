# backend/models.py
from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class Person(Base):
    __tablename__ = "people"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    image_path = Column(String)          # sample image path
    embedding_json = Column(String)      # embedding stored as JSON string

class Camera(Base):
    __tablename__ = "cameras"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    rtsp_url = Column(String)

class History(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer)
    person_id = Column(Integer, nullable=True)   # null => unknown
    score = Column(Float, nullable=True)         # matching score (distance)
    snapshot_path = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
