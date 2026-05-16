import cv2
import numpy as np
from deepface import DeepFace
import os
import pickle
from face_alignment import FaceAligner
from liveness_detector import LivenessDetector

class FaceService:
    MODEL_NAME   = 'ArcFace'   # More accurate than VGG-Face
    THRESHOLD    = 0.35        # Cosine-distance threshold for ArcFace
    MIN_FACE_PX  = 80          # Minimum face width/height in pixels
    BLUR_THRESH  = 80          # Laplacian variance – below = too blurry
    TARGET_IMGS  = 10          # Default number of captures per student

    def __init__(self, faces_dir='known_faces'):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        os.environ["DEEPFACE_HOME"] = base_dir

        weights_dir = os.path.join(base_dir, ".deepface", "weights")
        os.makedirs(weights_dir, exist_ok=True)

        # OpenCV Haar cascade – no extra download needed
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        self.faces_dir       = os.path.join(base_dir, faces_dir)
        self.embeddings_file = os.path.join(self.faces_dir, 'embeddings.pkl')
        # Format: { student_id: [emb1, emb2, ...] }
        self.known_embeddings = {}

        self.aligner = FaceAligner()
        self.liveness = LivenessDetector()

        os.makedirs(self.faces_dir, exist_ok=True)
        self.load_embeddings()

    # ------------------------------------------------------------------ #
    #  Persistence                                                         #
    # ------------------------------------------------------------------ #

    def load_embeddings(self):
        if os.path.exists(self.embeddings_file):
            with open(self.embeddings_file, 'rb') as f:
                data = pickle.load(f)
            for k, v in data.items():
                # Migrate old single-embedding format → list
                if isinstance(v, list) and v and isinstance(v[0], (int, float)):
                    self.known_embeddings[k] = [v]
                else:
                    self.known_embeddings[k] = v

    def save_embeddings(self):
        with open(self.embeddings_file, 'wb') as f:
            pickle.dump(self.known_embeddings, f)

    # ------------------------------------------------------------------ #
    #  Face detection & quality                                            #
    # ------------------------------------------------------------------ #

    def detect_faces(self, frame):
        """Return list of (x, y, w, h) for every face found."""
        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5,
            minSize=(self.MIN_FACE_PX, self.MIN_FACE_PX)
        )
        return faces if len(faces) else []

    def assess_quality(self, frame):
        """
        Evaluate frame quality for registration.
        Returns (face_roi, box, is_good, status_message)
        """
        faces = self.detect_faces(frame)
        if len(faces) == 0:
            return None, None, False, "No face detected – look at the camera"

        # Largest face wins
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])

        if w < self.MIN_FACE_PX or h < self.MIN_FACE_PX:
            return None, (x, y, w, h), False, "Move closer to the camera"

        # Crop with small padding
        pad = 15
        x1 = max(0, x - pad)
        y1 = max(0, y - pad)
        x2 = min(frame.shape[1], x + w + pad)
        y2 = min(frame.shape[0], y + h + pad)
        face_roi = frame[y1:y2, x1:x2]

        # Sharpness check
        gray_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        blur_var = cv2.Laplacian(gray_roi, cv2.CV_64F).var()

        if blur_var < self.BLUR_THRESH:
            return face_roi, (x, y, w, h), False, "Hold still – image is blurry"

        return face_roi, (x, y, w, h), True, "Good quality – capturing…"

    # ------------------------------------------------------------------ #
    #  Embedding extraction                                                #
    # ------------------------------------------------------------------ #

    def extract_embedding(self, face_roi):
        """Extract ArcFace embedding from a pre-cropped face ROI."""
        try:
            aligned_face = self.aligner.align(face_roi)
            result  = DeepFace.represent(
                aligned_face,
                model_name=self.MODEL_NAME,
                enforce_detection=False,
                detector_backend='skip'
            )
            if result:
                return result[0]['embedding']
        except Exception as e:
            print(f"[FaceService] embedding error: {e}")
        return None

    # ------------------------------------------------------------------ #
    #  Registration                                                        #
    # ------------------------------------------------------------------ #

    def register_student_frames(self, student_id, face_rois):
        """
        Register a student from a list of pre-cropped face ROIs.
        Replaces any existing embeddings for this student.
        Returns (stored_count, attempted_count).
        """
        embeddings = []
        for roi in face_rois:
            emb = self.extract_embedding(roi)
            if emb:
                embeddings.append(emb)

        if embeddings:
            self.known_embeddings[student_id] = embeddings
            self.save_embeddings()

        return len(embeddings), len(face_rois)

    def get_embedding_count(self, student_id):
        return len(self.known_embeddings.get(student_id, []))

    def clear_student(self, student_id):
        if student_id in self.known_embeddings:
            del self.known_embeddings[student_id]
            self.save_embeddings()
            return True
        return False

    # ------------------------------------------------------------------ #
    #  Recognition                                                         #
    # ------------------------------------------------------------------ #

    def recognize_face(self, frame):
        """
        Detect all faces in frame, match against stored embeddings.
        Returns (list_of_matched_student_ids, annotated_frame).
        """
        detected_students = []
        try:
            faces = self.detect_faces(frame)
            for (x, y, w, h) in faces:
                pad = 10
                x1 = max(0, x - pad)
                y1 = max(0, y - pad)
                x2 = min(frame.shape[1], x + w + pad)
                y2 = min(frame.shape[0], y + h + pad)
                face_roi = frame[y1:y2, x1:x2]

                if face_roi.size == 0:
                    continue

                # Liveness check
                liveness_res = self.liveness.check(face_roi)
                if not liveness_res.is_live:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    cv2.putText(frame, "Spoof", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)
                    continue

                curr_emb = self.extract_embedding(face_roi)
                if curr_emb is None:
                    continue

                best_match = None
                min_dist   = self.THRESHOLD

                # Vote across all stored embeddings for each student
                for sid, embeddings in self.known_embeddings.items():
                    for known_emb in embeddings:
                        if len(curr_emb) != len(known_emb):
                            continue
                        dist = self.cosine_distance(curr_emb, known_emb)
                        if dist < min_dist:
                            min_dist   = dist
                            best_match = sid

                if best_match:
                    detected_students.append(best_match)
                    live_text = "Real" if liveness_res.status == "REAL" else "Live?"
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame, f"ID:{best_match} ({live_text})", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)
                else:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 165, 255), 2)
                    cv2.putText(frame, "Unknown", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 165, 255), 2)

        except Exception as e:
            print(f"[FaceService] recognize error: {e}")

        return detected_students, frame

    # ------------------------------------------------------------------ #
    #  Utility                                                             #
    # ------------------------------------------------------------------ #

    @staticmethod
    def cosine_distance(a, b):
        a = np.array(a, dtype=np.float64)
        b = np.array(b, dtype=np.float64)
        return 1.0 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
