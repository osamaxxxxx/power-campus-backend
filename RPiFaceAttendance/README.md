# RPiFaceAttendance

> **Raspberry Pi Face-Based Biometric Attendance System**  
> A standalone desktop application that uses a live camera feed, ArcFace deep learning embeddings, and liveness detection to automate student attendance – fully integrated with the **Power Campus** backend API.

---

## Table of Contents

1. [Overview](#overview)  
2. [Features](#features)  
3. [Architecture](#architecture)  
4. [Directory Structure](#directory-structure)  
5. [Prerequisites](#prerequisites)  
6. [Installation](#installation)  
7. [Configuration](#configuration)  
8. [Running the App](#running-the-app)  
9. [Module Reference](#module-reference)  
   - [main.py](#mainpy)  
   - [gui_app.py](#gui_apppy)  
   - [face_service.py](#face_servicepy)  
   - [face_alignment.py](#face_alignmentpy)  
   - [liveness_detector.py](#liveness_detectorpy)  
   - [api_client.py](#api_clientpy)  
10. [How It Works](#how-it-works)  
    - [Student Registration Flow](#student-registration-flow)  
    - [Attendance Session Flow](#attendance-session-flow)  
    - [Liveness Detection](#liveness-detection)  
11. [API Endpoints Used](#api-endpoints-used)  
12. [Known Issues & Limitations](#known-issues--limitations)  
13. [Optional – SVM Liveness Training](#optional--svm-liveness-training)  

---

## Overview

**RPiFaceAttendance** is a Python desktop application designed to run on a Raspberry Pi (or any Windows/Linux machine with a webcam). An instructor logs in, selects a course and lecture, and starts a session. The camera continuously scans for student faces, matches them against stored ArcFace embeddings, verifies liveness, and automatically marks attendance via the Power Campus REST API.

---

## Features

| Feature | Details |
|---|---|
| **Instructor Authentication** | JWT login via Power Campus `/api/Auth/login` |
| **Face Registration** | Camera auto-capture (10 images) **or** bulk image upload |
| **ArcFace Embeddings** | 512-dimensional embeddings via DeepFace `ArcFace` model |
| **Face Alignment** | Geometric alignment (eye-to-canonical) using OpenCV LBF landmarks |
| **Liveness Detection** | Adaptive one-class detector (LBP + gradient + colour + FFT features); optional SVM |
| **Multi-embedding Voting** | Up to 10 embeddings per student for robust cosine-distance matching |
| **Real-time Attendance** | Marks attendance via API and signals session start/stop to the backend |
| **Cross-platform** | Runs on Windows (DirectShow camera) and Linux (V4L2) |
| **Dark-mode GUI** | Built with CustomTkinter |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     gui_app.py  (App)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  Login View  │  │  Reg. View   │  │  Att. View    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬────────┘  │
│         │                 │                  │           │
│         ▼                 ▼                  ▼           │
│      APIClient       FaceService          FaceService    │
│         │           /    |    \              |           │
│         │    FaceAligner  |  LivenessDetector│           │
│         │          DeepFace (ArcFace)        │           │
│         ▼                                   ▼           │
│   Power Campus REST API            OpenCV Camera Loop   │
└─────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
RPiFaceAttendance/
├── requirements.txt          # Python dependencies (see Installation)
└── src/
    ├── main.py               # Entry point
    ├── gui_app.py            # CustomTkinter UI (Login / Register / Attendance)
    ├── face_service.py       # Embedding extraction, registration, recognition
    ├── face_alignment.py     # Geometric eye-alignment to 112×112 canonical crop
    ├── liveness_detector.py  # Anti-spoofing (LBP + gradient + colour + FFT)
    ├── api_client.py         # REST client for Power Campus API
    ├── yolov8n.pt            # YOLOv8 nano weights (bundled)
    └── known_faces/
        └── embeddings.pkl    # Persisted student embeddings (auto-created)
```

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python | ≥ 3.10 |
| Webcam / Pi Camera | Any OpenCV-compatible device |
| Internet access | Required for first ArcFace model download via DeepFace |
| Power Campus backend | Running at `https://powercampusapi.runasp.net` (or configured URL) |

> **Note:** The ArcFace model weights (~250 MB) are downloaded automatically by DeepFace on first run and cached in `src/.deepface/weights/`.

---

## Installation

```bash
# 1. Clone / navigate to the project
cd RPiFaceAttendance

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

> **Important:** `requirements.txt` uses `opencv-contrib-python` which includes the contrib modules needed for face landmark detection. Do **not** install `opencv-python` alongside it — they will conflict.

### Optional – SVM Liveness Training

If you want to train a binary SVM liveness classifier with your own real/spoof samples:

```bash
pip install scikit-learn>=1.3.0
```

See [Optional – SVM Liveness Training](#optional--svm-liveness-training) for usage.

---

## Configuration

The backend URL is configured directly in `src/api_client.py`:

```python
class APIClient:
    def __init__(self, base_url="https://powercampusapi.runasp.net"):
        ...
```

Change `base_url` to point to a local development server if needed:

```python
APIClient(base_url="http://localhost:5000")
```

---

## Running the App

```bash
cd src
python main.py
```

The app opens a dark-mode GUI window with three sections accessible from the left sidebar:

1. **Login** – enter instructor email & password  
2. **Register Face** – enroll student biometrics  
3. **Attendance Session** – run a live attendance session  

---

## Module Reference

### `main.py`

Simple entry point. Instantiates and runs the `App` class.

```python
from gui_app import App
app = App()
app.mainloop()
```

---

### `gui_app.py`

**Class:** `App(ctk.CTk)`

The root CustomTkinter window. Manages all UI views and mediates between `FaceService` and `APIClient`.

| Method | Purpose |
|---|---|
| `show_login()` | Renders login form |
| `handle_login()` | Calls `APIClient.login()` in a background thread |
| `show_registration()` | Renders student face registration view |
| `open_registration_camera()` | Opens webcam in preview-only mode |
| `start_registration_capture()` | Begins auto-capture of face crops |
| `_camera_preview_loop()` | Background thread: reads frames, assesses quality, auto-captures |
| `upload_images()` | File-dialog bulk upload mode |
| `handle_registration()` | Calls `FaceService.register_student_frames()` in background |
| `show_attendance()` | Renders attendance session view |
| `toggle_attendance_session()` | Starts / stops session (API + camera loop) |
| `start_camera(label, mode)` | Launches camera thread; in attendance mode calls `recognize_face()` |
| `stop_camera()` | Stops camera thread and releases capture device |
| `run_in_thread(task, callback)` | Utility: runs `task` on a daemon thread, posts `callback` to the main thread |

---

### `face_service.py`

**Class:** `FaceService`

Core logic for face quality assessment, embedding extraction, registration, and recognition.

#### Key constants

| Constant | Default | Description |
|---|---|---|
| `MODEL_NAME` | `'ArcFace'` | DeepFace model used for embedding |
| `THRESHOLD` | `0.35` | Cosine-distance threshold for a positive match |
| `MIN_FACE_PX` | `80` | Minimum face bounding-box size in pixels |
| `BLUR_THRESH` | `80` | Laplacian variance below this → too blurry |
| `TARGET_IMGS` | `10` | Default auto-capture count |

#### Methods

| Method | Returns | Description |
|---|---|---|
| `assess_quality(frame)` | `(roi, box, is_good, msg)` | Detects largest face, checks size and sharpness |
| `extract_embedding(face_roi)` | `list[float] \| None` | Aligns face, runs ArcFace embedding via DeepFace |
| `register_student_frames(student_id, rois)` | `(stored, attempted)` | Stores list of embeddings for a student |
| `recognize_face(frame)` | `(list[int], frame)` | Detects all faces, runs liveness + cosine matching |
| `get_embedding_count(student_id)` | `int` | Number of stored embeddings for a student |
| `clear_student(student_id)` | `bool` | Removes all embeddings for a student |
| `cosine_distance(a, b)` | `float` | Static helper: `1 − (a·b / ‖a‖‖b‖)` |

#### Embeddings storage

Embeddings are persisted as a `dict[int, list[list[float]]]` in `known_faces/embeddings.pkl` (format: `{ student_id: [emb1, emb2, ...] }`).  
Old single-embedding entries are automatically migrated to the list format on load.

---

### `face_alignment.py`

**Class:** `FaceAligner`

Geometrically aligns a face crop to a 112×112 ArcFace-canonical image using 5-point or 68-point facial landmarks.

#### How it works

1. Loads OpenCV's **LBF landmark detector** from `lbfmodel.yaml` (if present).  
2. Detects landmarks; selects the left and right eye centres.  
3. Computes a **similarity transform** (`cv2.estimateAffinePartial2D`) mapping detected eye positions to canonical coordinates:
   - Left eye → `(38.29, 51.70)`  
   - Right eye → `(73.53, 51.50)`  
4. Applies `cv2.warpAffine` to produce the normalised 112×112 output.

If `lbfmodel.yaml` is missing or landmark detection fails, it falls back to a plain `cv2.resize`.

#### Static convenience method

```python
FaceAligner.align_simple(face_bgr, left_eye_center, right_eye_center)
```

Use this when eye positions are already known (e.g., from MediaPipe or dlib).

---

### `liveness_detector.py`

**Class:** `LivenessDetector`

CPU-only anti-spoofing module. No external model download required.

#### Feature vector (43-dim)

| Component | Dims | Purpose |
|---|---|---|
| LBP histogram | 32 | Texture difference between real 3-D faces and flat 2-D spoofs |
| Gradient stats | 4 | Sobel magnitude mean, std, P25, P75 |
| Colour channel stats | 6 | Per-channel (BGR) mean & std |
| FFT high-freq energy | 1 | Moiré pattern detection (screen replay attacks) |

#### Modes

**Adaptive (default)**  
- Assumes the first `min_calibration_frames` (default 30) frames are genuine.  
- Builds a mean/std reference model from those frames.  
- Subsequent frames are scored via z-score distance; `score = exp(−dist/3)`.  
- Score below `spoof_threshold` (default 0.30) → **SPOOF**.
- Returns **UNSURE** during calibration (treated as live by `FaceService`).

**SVM (optional)**  
Call `train(real_crops, spoof_crops)` with lists of BGR face images to fit a scikit-learn `SVC(kernel='rbf', probability=True)`. Once trained, SVM scores are used instead of adaptive scores.

#### `LivenessResult` dataclass

| Field | Type | Values |
|---|---|---|
| `status` | `str` | `"REAL"` \| `"SPOOF"` \| `"UNSURE"` |
| `score` | `float` | 0.0 – 1.0 (higher = more likely real) |
| `confidence` | `float` | 0.0 – 1.0 |
| `is_live` | `bool` | `True` if `status` is `REAL` or `UNSURE` |

#### Public API

```python
detector = LivenessDetector(spoof_threshold=0.30, min_calibration_frames=30)
result = detector.check(face_bgr_image)
detector.reset_calibration()          # call when camera changes
detector.train(real_crops, spoof_crops)  # optional SVM training
```

---

### `api_client.py`

**Class:** `APIClient`

Thin wrapper around the Power Campus REST API using `requests`.

| Method | Endpoint | Description |
|---|---|---|
| `login(email, password)` | `POST /api/Auth/login` | Authenticates; stores JWT token |
| `get_courses()` | `GET /api/Courses` | Returns list of instructor's courses |
| `get_course_students(course_id)` | `GET /api/Enrollments/course/{id}` | Returns enrolled students |
| `get_lectures(course_id)` | `GET /api/Lectures/course/{id}` | Returns lectures for a course |
| `mark_attendance(student_id, course_id, lecture_id)` | `POST /api/Attendance` | Marks a student as present |
| `start_session(course_id, lecture_id)` | `POST /api/Attendance/session/start` | Signals session start to backend/SignalR |
| `stop_session()` | `POST /api/Attendance/session/stop` | Signals session end to backend/SignalR |

All authenticated requests include `Authorization: Bearer <token>`.

---

## How It Works

### Student Registration Flow

```
Instructor selects course → selects student
         │
         ▼
  [Camera Mode]                  [File Upload Mode]
  Open camera → preview          File dialog → load images
         │                               │
         ▼                               ▼
  Auto-capture 10 face ROIs     Extract face ROI per image
  (quality assessed per frame)           │
         └───────────────────────────────┘
                      │
                      ▼
           FaceService.register_student_frames()
           ├── FaceAligner.align()  (112×112 canonical crop)
           ├── DeepFace.represent() (512-dim ArcFace embedding)
           └── Save to known_faces/embeddings.pkl
```

### Attendance Session Flow

```
Select course + lecture → Start Session
         │
         ▼
APIClient.start_session()   (signals backend / SignalR hub)
         │
         ▼
Camera loop starts
  ├── detect faces (Haar cascade)
  ├── LivenessDetector.check()  → SPOOF? skip
  ├── FaceAligner.align()
  ├── DeepFace.represent()  (ArcFace embedding)
  ├── Cosine distance vs all known embeddings
  ├── Match found (dist < 0.35)?
  │       └── APIClient.mark_attendance()
  └── Annotate frame (green = known, orange = unknown, red = spoof)
         │
         ▼ (Stop Session)
APIClient.stop_session()
```

### Liveness Detection

The liveness detector runs on each candidate face before recognition:

1. Resize face to 64×64.
2. Extract 43-dimensional feature vector (LBP + gradient + colour + FFT).
3. **Calibration phase** (first 30 frames): collect statistics, return `UNSURE`.
4. **Detection phase**: compute z-score distance from calibrated real distribution.  
   `score = exp(−z_mean / 3.0)`  
   If `score < 0.30` → **SPOOF** → skip recognition for this face.

---

## API Endpoints Used

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/Auth/login` | ❌ | Instructor login |
| `GET` | `/api/Courses` | ✅ JWT | Get instructor courses |
| `GET` | `/api/Enrollments/course/{id}` | ✅ JWT | Get enrolled students |
| `GET` | `/api/Lectures/course/{id}` | ✅ JWT | Get course lectures |
| `POST` | `/api/Attendance` | ✅ JWT | Mark student attendance |
| `POST` | `/api/Attendance/session/start` | ✅ JWT | Start attendance session |
| `POST` | `/api/Attendance/session/stop` | ✅ JWT | Stop attendance session |

---

## Known Issues & Limitations

| Issue | Notes |
|---|---|
| **LBF landmark model not bundled** | `lbfmodel.yaml` must be placed in `src/` manually. Without it, `FaceAligner` falls back to plain resize – alignment is still functional but less precise. |
| **First-run model download** | DeepFace downloads ArcFace weights (~250 MB) on first use. Ensure internet access for the first launch. |
| **Single camera assumed** | App always opens camera index `0`. For a Raspberry Pi with CSI camera, ensure the camera is accessible via `/dev/video0`. |
| **Adaptive liveness calibration** | The first 30 frames of each session are assumed to be real faces. Start sessions in a controlled environment. |
| **opencv-python conflict** | `opencv-contrib-python` and `opencv-python` cannot coexist. Uninstall `opencv-python` if previously installed. |

---

## Optional – SVM Liveness Training

If you have labelled real and spoof face samples, you can train a more robust binary SVM:

```python
from liveness_detector import LivenessDetector
import cv2, os

# Load your labelled face crops as BGR numpy arrays
real_crops  = [cv2.imread(p) for p in real_image_paths]
spoof_crops = [cv2.imread(p) for p in spoof_image_paths]

detector = LivenessDetector()
success = detector.train(real_crops, spoof_crops)
# success = True if scikit-learn is installed
```

After training, `detector.check()` automatically uses the SVM path instead of the adaptive calibration. The SVM is not persisted between sessions – re-train on startup or serialise with `pickle` yourself.

---

*Part of the **Power Campus** graduation project — Faculty Biometric Attendance Integration.*
