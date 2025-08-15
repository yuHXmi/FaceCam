**FaceCam – Hệ thống nhận diện khuôn mặt từ camera**

FaceCam là dự án biến luồng camera HTTP thành hệ thống nhận diện khuôn mặt thời gian thực, có giao diện quản trị (admin) để quản lý danh sách người/ảnh mẫu và camera, cùng giao diện người dùng (user) để xem luồng và lịch sử nhận diện. Backend viết bằng FastAPI, lưu dữ liệu PostgreSQL, xử lý nhận diện bằng DeepFace (mặc định Facenet). Frontend viết bằng React (Ant Design). Có sẵn Docker/Docker Compose để chạy nhanh.

**Tính năng chính**

📷 Quản lý đa camera qua HTTP stream.

👤 Quản lý danh sách người; tự động trích xuất embedding bằng DeepFace.

🔍 So khớp khuôn mặt từng khung hình với ngưỡng (cosine distance) tùy chỉnh.

🖼️ Lưu snapshot khi có khớp (ảnh cắt từ khung hình), kèm điểm số và thời gian.

🗂️ Xem lịch sử nhận diện gần đây.

**Kiến trúc & thành phần**
```bash
FaceCam/
├─ backend/                # FastAPI + xử lý nhận diện
│  ├─ main.py              # Khởi tạo app, CORS, mount /uploads, đăng ký routers
│  ├─ database.py          # Kết nối database
│  ├─ models.py            # (Person, Camera, History)
│  ├─ schemas.py           # Pydantic schemas cho API
│  ├─ utils.py             # DeepFace embedding, so sánh cosine, thư mục uploads/
│  ├─ camera_manager.py    # Thread đọc camera, nhận diện, lưu snapshot & history
│  └─ routers/
│     ├─ people.py         # /api/people: thêm/xóa/list người (upload ảnh)
│     ├─ cameras.py        # /api/cameras: thêm/xóa/list camera & start/stop thread
│     ├─ history.py        # /api/history: list lịch sử nhận diện
│     └─ stream.py         # /api/stream/{cam_id}: phát MJPEG
│
├─ frontend-admin/         # React (AntD) – giao diện quản trị
│  └─ src/
│     ├─ api.js            # Gọi API backend (mặc định http://localhost:8000)
│     └─ App.js            # Trang People / Cameras / History
│
├─ frontend-user/          # React (AntD) – giao diện người dùng
│  └─ src/
│     ├─ api.js            # Gọi API backend (mặc định http://localhost:8000)
│     └─ App.js            # Chọn camera, xem luồng & lịch sử
│
├─ Dockerfile.backend      # Dockerfile cho backend
└─ docker-compose.yml      # Orchestrate backend + 2 frontend (+ service db)
```

**Yêu cầu hệ thống**

Docker & Docker Compose

**Cài đặt & chạy nhanh với Docker**

Tại thư mục gốc FaceCam/, chạy:

```bash
docker-compose up --build
```

**Truy cập:**

Backend: http://localhost:8000

Frontend User: http://localhost:3001

Frontend Admin: http://localhost:3002

**Hướng dẫn sử dụng**

Thêm người (ảnh mẫu) – Mở Frontend Admin → tab People → nhập name và upload ảnh rõ mặt. Hệ thống sẽ trích xuất embedding và lưu.

Thêm camera – Vào tab Cameras → nhập name + RTSP/HTTP URL (ví dụ RTSP từ IP camera). Backend sẽ tạo thread đọc luồng và bắt đầu nhận diện.

**Xem luồng & lịch sử**

MJPEG stream: GET /api/stream/{cam_id} (có thể nhúng <img src=...>).

Lịch sử: GET /api/history (frontend hiển thị kèm ảnh snapshot, tên người và điểm số).

Xoá người/camera – Qua giao diện admin hoặc API tương ứng.

**Các API chính:**

POST /api/people/add – multipart form (name, file)

GET /api/people – danh sách người

DELETE /api/people/{id} – xoá người

POST /api/cameras – thêm camera (name, rtsp_url) và start thread

GET /api/cameras – danh sách camera

DELETE /api/cameras/{id} – dừng thread và xoá camera

GET /api/history – lịch sử nhận diện

GET /api/stream/{cam_id} – MJPEG stream

**Tuỳ chỉnh & cấu hình**

Ngưỡng khớp (match_threshold): mặc định 0.5 trong backend/camera_manager.py. Giảm để nhận diện khắt khe hơn, tăng để dễ khớp hơn.

Model DeepFace: utils.py đặt MODEL_NAME = "Facenet". Có thể đổi sang "ArcFace" (cần tải model lúc chạy lần đầu).

Vị trí lưu file: đặt trong backend/utils.py – uploads/faces và uploads/snapshots. Backend mount /uploads để frontend truy cập ảnh.

CORS: hiện mở allow_origins=["*"] trong main.py, có thể siết lại domain.

Database: PostgreSQL.

**Lưu ý hiệu năng**

DeepFace lần đầu sẽ tải trọng số model → khởi động chậm. Sau đó cache sẽ nhanh hơn.


MJPEG stream: đây là luồng multipart đơn giản; trình duyệt hiển thị được nhưng không có âm thanh và độ trễ phụ thuộc CPU/mạng.

**Phát triển & mở rộng**

Thêm phân quyền/tài khoản thay vì CORS mở.

Chuẩn hoá logging, giám sát các thread camera.

**Dockerhub**

Backend:https://hub.docker.com/repository/docker/iamxhuy/facecam-backend/general

Frontend-admin: https://hub.docker.com/repository/docker/iamxhuy/facecam-frontend-admin/general

Frontend-user: https://hub.docker.com/repository/docker/iamxhuy/facecam-frontend-user/general

**Tác giả** 

Hà Xuân Huy
