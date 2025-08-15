# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from .routers import people, cameras, history, stream
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Security Camera DeepFace Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mount uploads (faces + snapshots) để frontend có thể GET ảnh
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

app.include_router(people.router)
app.include_router(cameras.router)
app.include_router(history.router)
app.include_router(stream.router)

@app.get("/")
def root():
    return {"msg": "backend running"}
