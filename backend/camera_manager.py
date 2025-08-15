import threading
import time
import os
import cv2
import uuid
import numpy as np
from .database import SessionLocal
from . import models, utils
from sqlalchemy.orm import Session

manager = {}

class CameraThread(threading.Thread):
    def __init__(self, cam_id, cam_url, poll_interval=1.0, match_threshold=0.5, max_fail=5):
        super().__init__(daemon=True)
        self.cam_id = cam_id
        self.cam_url = cam_url  
        self.poll_interval = poll_interval
        self.match_threshold = match_threshold
        self.max_fail = max_fail  # số lần lỗi frame liên tiếp trước khi reconnect
        self.fail_count = 0
        self.running = threading.Event()
        self.running.set()
        self.cap = None

    def connect_camera(self):
        """Kết nối lại camera"""
        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(int(self.cam_url) if str(self.cam_url).isdigit() else self.cam_url, cv2.CAP_FFMPEG)
        if self.cap.isOpened():
            print(f"[CameraThread] connected to {self.cam_url}")
            self.fail_count = 0
            return True
        else:
            print(f"[CameraThread] cannot open stream {self.cam_url}")
            return False

    def run(self):
        print(f"[CameraThread] starting camera {self.cam_id} url={self.cam_url}")

        if not self.connect_camera():
            return

        while self.running.is_set():
            try:
                ret, frame = self.cap.read()
                if not ret:
                    self.fail_count += 1
                    print(f"[CameraThread] failed to read frame from {self.cam_url} ({self.fail_count}/{self.max_fail})")
                    if self.fail_count >= self.max_fail:
                        print(f"[CameraThread] too many errors, reconnecting...")
                        if not self.connect_camera():
                            time.sleep(5)
                            continue
                    else:
                        time.sleep(1)
                    continue
                else:
                    self.fail_count = 0  # reset khi đọc thành công

                # --- Xử lý nhận diện ---
                from deepface import DeepFace
                try:
                    faces = DeepFace.extract_faces(img_path=frame, detector_backend="retinaface")
                except Exception:
                    faces = []

                for det in faces:
                    face_img = det.get("face")
                    if face_img is None:
                        continue

                    # Convert float [0,1] -> uint8 [0,255]
                    if face_img.dtype in [np.float32, np.float64]:
                        face_img = (face_img * 255).astype("uint8")
                    else:
                        face_img = face_img.astype("uint8")

                    emb = utils.img_to_embedding(face_img)
                    db: Session = SessionLocal()
                    people = db.query(models.Person).filter(models.Person.embedding_json != None).all()
                    best_id = None
                    best_score = 1.0
                    for p in people:
                        try:
                            p_emb = utils.emb_from_json(p.embedding_json)
                            dist = utils.compare_embeddings(emb, p_emb)
                            print(p.id, dist)
                            if dist < best_score:
                                best_score = dist
                                best_id = p.id
                        except Exception:
                            continue
                    is_known = (best_id is not None and best_score <= self.match_threshold)

                    # Lưu snapshot
                    fname = f"{self.cam_id}_{uuid.uuid4().hex}.jpg"
                    snap_dir = os.path.join(os.path.dirname(__file__), "uploads", "snapshots")
                    os.makedirs(snap_dir, exist_ok=True)
                    fpath = os.path.join(snap_dir, fname)

                    try:
                        tmp = face_img.astype("uint8")
                        if tmp.shape[2] == 3:
                            tmp = cv2.cvtColor(tmp, cv2.COLOR_RGB2BGR)
                        cv2.imwrite(fpath, tmp)
                    except Exception:
                        cv2.imwrite(fpath, frame)

                    ev = models.History(
                        camera_id=self.cam_id,
                        person_id=best_id if is_known else None,
                        score=best_score if is_known else None,
                        snapshot_path=fpath
                    )
                    db.add(ev)
                    db.commit()
                    db.close()

                time.sleep(self.poll_interval)
            except Exception as e:
                print(f"[CameraThread] error: {e}")
                time.sleep(1)

        if self.cap:
            self.cap.release()
        print(f"[CameraThread] stopped camera {self.cam_id}")

    def stop(self):
        self.running.clear()

def start_camera(cam_id, cam_url):
    if cam_id in manager:
        print(f"Camera {cam_id} already running")
        return
    t = CameraThread(cam_id, cam_url)
    manager[cam_id] = t
    t.start()

def stop_camera(cam_id):
    thread = manager.get(cam_id)
    if thread:
        thread.stop()
        thread.join()
        del manager[cam_id]
