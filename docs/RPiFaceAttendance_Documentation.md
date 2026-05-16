# RPiFaceAttendance Documentation

This document gives a concise overview of the **RPiFaceAttendance** Python module that provides biometric face‑based attendance tracking for the Power Campus system.

---

## What is RPiFaceAttendance?
- A standalone desktop application (Windows/Linux/Raspberry Pi) written in Python.
- Uses a webcam to detect faces, verify liveness, extract ArcFace embeddings, and automatically mark attendance via the Power Campus REST API.
- Provides three main UI screens (Login, Register Face, Attendance Session) built with **CustomTkinter**.

---

## Quick Start
1. **Clone the repository** and navigate to the `RPiFaceAttendance` folder.
2. Set up a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # or source .venv/bin/activate on Linux/macOS
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   cd src
   python main.py
   ```
4. Log in with an instructor account, select a course/lecture, and start a session.

---

## Core Modules
| Module | Purpose |
|---|---|
| `gui_app.py` | CustomTkinter UI and interaction logic |
| `face_service.py` | Face detection, quality assessment, alignment, embedding extraction, registration, recognition |
| `face_alignment.py` | Aligns faces to the canonical ArcFace 112×112 format |
| `liveness_detector.py` | Adaptive anti‑spoofing (LBP, gradient, colour, FFT) – optional SVM training |
| `api_client.py` | Thin wrapper around Power Campus API (login, courses, attendance) |
| `yolov8n.pt` | Tiny YOLOv8 model bundled for optional object detection |

---

## Architecture Diagram
```
┌─────────────────────────────────────────────────────────┐
│                     gui_app.py  (App)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐│
│  │  Login View  │  │  Reg. View   │  │  Att. View    ││
│  └──────┬───────┘  └──────┬───────┘  └──────┬────────┘│
│         ▼                 ▼                  ▼          │
│      APIClient       FaceService          FaceService │
│         │           /    |    \              |          │
│         │    FaceAligner  |  LivenessDetector│          │
│         │          DeepFace (ArcFace)        │          │
│         ▼                                   ▼          │
│   Power Campus REST API            OpenCV Camera Loop │
└─────────────────────────────────────────────────────────┘
```

---

## Liveness Detection Details
- **Adaptive mode (default)**: First 30 frames are assumed to be genuine; builds mean/std model.
- **Score** = `exp(-z_mean/3)`.  `score < 0.30` ⇒ **SPOOF**.
- **Optional SVM**: Call `LivenessDetector.train(real_crops, spoof_crops)` after installing `scikit-learn`.

---

## FAQ
- **Where are embeddings stored?** `src/known_faces/embeddings.pkl` (pickle format).
- **What if I see `opencv-python` conflicts?** Uninstall it (`pip uninstall opencv-python`) and keep `opencv-contrib-python`.
- **Can I run this on a Raspberry Pi?** Yes – ensure the Pi camera is accessible as `/dev/video0` and install the required system dependencies (e.g., `libgl1-mesa-glx`).

---

*For the full reference, see the `README.md` in the `RPiFaceAttendance` directory.*
