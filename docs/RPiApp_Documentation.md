# Power Campus Raspberry Pi Attendance App

The Raspberry Pi Face Attendance App is a localized edge-computing Python application. It uses connected cameras to capture student faces, recognize them locally, and automatically push attendance logs to the backend API.

## Architecture & Tech Stack

- **Language**: Python 3.x
- **Computer Vision Framework**: OpenCV (for camera capture and image processing)
- **Face Detection Model**: YOLOv8 (`yolov8n.pt`) via the `ultralytics` package for highly accurate and fast bounding box detection.
- **Face Recognition Model**: DeepFace (Facenet model) for verifying and identifying faces based on stored embeddings.
- **GUI Framework**: Tkinter (for rendering the desktop UI on the Raspberry Pi touch screen or connected display).
- **HTTP Client**: `requests` library for synchronizing data with the .NET Backend API.
- **Concurrency**: `threading` module to ensure the GUI remains responsive while heavy AI tasks (face recognition) run in the background.

## Directory Structure
The application is located in `RPiFaceAttendance/`:

- `/src/main.py`: The entry point script.
- `/src/gui_app.py`: Contains the Tkinter classes for the main window, layout, and event handling.
- `/src/face_service.py`: Contains the core logic for YOLOv8 face detection, DeepFace encoding, and face matching.
- `/src/api_client.py`: Manages communication (Authentication, Fetching Courses, Syncing Attendance) with the backend API.
- `/src/known_faces/`: Local directory where captured student face embeddings or reference images are stored.
- `/requirements.txt`: Python package dependencies.

## Key Workflows

### 1. Initialization and Login
- Upon startup, the app displays a login screen.
- An Administrator or Instructor logs in.
- `api_client.py` sends a request to the Backend API and receives a JWT token, which is stored in memory for subsequent API calls.

### 2. Course Selection
- After logging in, the app fetches the list of available/assigned courses from the backend.
- The instructor selects a specific course to start an attendance session.

### 3. Face Registration (Adding a New Student)
- If a student is not in the system, they can be added locally.
- The camera captures their face, YOLOv8 detects the bounding box, and DeepFace extracts the unique facial embedding.
- The embedding is saved locally in `known_faces` associated with the student's ID or Name.

### 4. Real-time Attendance Marking
- Once a session starts, the camera continuously feeds frames to the system.
- YOLOv8 detects faces in the frame.
- DeepFace compares the detected faces against the `known_faces` local database.
- If a match is found and passes the confidence threshold, the student is marked as "Present".
- To prevent UI freezing, this heavy processing is offloaded to a background thread.
- The system pushes the attendance record (`CourseId`, `StudentId`, `Date`, `Status="Present"`) to the Backend API via `api_client.py`.

## Setup & Execution

### Prerequisites
- Python 3.8+
- A connected Web Camera or Raspberry Pi Camera Module.

### Installation
1. Navigate to the app directory:
   ```bash
   cd RPiFaceAttendance
   ```
2. Create and activate a virtual environment (Recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Installing DeepFace and Ultralytics on a Raspberry Pi may require additional system dependencies like CMake, libgl1-mesa-glx, etc.)*

### Configuration
Update the Backend API URL inside `src/api_client.py` to point to the server's local network IP (e.g., `http://192.168.1.100:5000/api`).

### Running the App
Run the entry point script:
```bash
python src/main.py
```
The application window will open, activate the camera, and prompt for login.
