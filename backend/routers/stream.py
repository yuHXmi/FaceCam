# backend/routers/stream.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from ..camera_manager import manager
import cv2, time, traceback

router = APIRouter(prefix="/api/stream", tags=["stream"])

def gen_frames(cam_thread):
    while True:
        try:
            if not cam_thread or not hasattr(cam_thread, "cap"):
                time.sleep(0.1)
                continue

            cap = cam_thread.cap
            if not cap or not cap.isOpened():
                time.sleep(0.1)
                continue

            ret, frame = cap.read()
            if not ret or frame is None:
                time.sleep(0.05)  # tránh vòng lặp quá nhanh
                continue

            success, buffer = cv2.imencode(".jpg", frame)
            if not success:
                continue

            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")

            time.sleep(0.03)  # ~30 FPS max

        except Exception:
            traceback.print_exc()
            time.sleep(0.5)

@router.get("/{cam_id}")
def stream_cam(cam_id: int):
    cam_thread = manager.get(cam_id)
    return StreamingResponse(
        gen_frames(cam_thread),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
