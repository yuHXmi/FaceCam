import os
import json
import cv2
from uuid import uuid4
import numpy as np
from deepface import DeepFace

# Thư mục mount ra ngoài container để lưu ảnh
DATA_DIR = os.getenv("DATA_DIR", "/data/uploads")
FACES_DIR = os.path.join(DATA_DIR, "faces")
SNAP_DIR = os.path.join(DATA_DIR, "snapshots")
os.makedirs(FACES_DIR, exist_ok=True)
os.makedirs(SNAP_DIR, exist_ok=True)

MODEL_NAME = "Facenet"

def img_to_embedding(img, model_name=MODEL_NAME):
    if img is None or not hasattr(img, 'shape') or img.size == 0:
        print("Invalid photo")
        return None
    try:
        result = DeepFace.represent(img_path=img, model_name=model_name, enforce_detection=False)
        if isinstance(result, list):
            if len(result) > 0 and isinstance(result[0], dict) and 'embedding' in result[0]:
                emb = np.array(result[0]['embedding'])
            else:
                emb = np.array(result[0]) if len(result) > 0 else np.array([])
        else:
            emb = np.array(result)
        return emb.reshape(-1) if emb.size > 0 else None
    except Exception as e:
        print("img_to_embedding error:", e)
        return None

def emb_to_json(emb):
    return json.dumps(emb.astype(float).tolist())

def emb_from_json(s):
    return np.array(json.loads(s))

def compare_embeddings(a, b):
    if a is None or b is None:
        return 1.0
    a = np.array(a, dtype=np.float64)
    b = np.array(b, dtype=np.float64)
    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)
    if a_norm > 0:
        a = a / a_norm
    if b_norm > 0:
        b = b / b_norm
    cos = np.dot(a, b)
    dist = 1 - cos
    return float(dist)

def save_snapshot(frame):
    filename = f"{uuid4()}.jpg"
    filepath = os.path.join(SNAP_DIR, filename)
    cv2.imwrite(filepath, frame)
    return filepath

def save_face_image(frame):
    filename = f"{uuid4()}.jpg"
    filepath = os.path.join(FACES_DIR, filename)
    cv2.imwrite(filepath, frame)
    return filepath
