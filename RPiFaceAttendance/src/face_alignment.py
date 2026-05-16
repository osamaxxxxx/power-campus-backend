"""
face_alignment.py
=================
Geometric face alignment using 5-point facial landmarks detected by OpenCV's
built-in face landmark detector (no extra model download required).

If a face has detectable landmarks the crop is affine-warped so that both
eyes land on fixed canonical positions, producing a standardised 112×112
image for the ArcFace embedding extractor.

Falls back transparently to a plain resize if landmark detection fails.
"""

import cv2
import numpy as np


# ---------------------------------------------------------------------------
# Canonical eye positions for a 112×112 ArcFace-style crop
# (matches the reference alignment used when ArcFace was trained)
# ---------------------------------------------------------------------------
CANONICAL_LEFT_EYE  = np.array([38.2946, 51.6963], dtype=np.float32)
CANONICAL_RIGHT_EYE = np.array([73.5318, 51.5014], dtype=np.float32)
OUTPUT_SIZE = (112, 112)


class FaceAligner:
    """
    Align a face crop so that eyes are in canonical positions.

    Usage
    -----
    aligner = FaceAligner()
    aligned = aligner.align(face_roi_bgr)   # always returns 112×112 BGR
    """

    def __init__(self):
        # OpenCV's built-in 5-point face landmark detector
        # Ships with opencv-contrib; if unavailable we fall back to resize only.
        self._detector = None
        try:
            self._detector = cv2.face.createFacemarkLBF()
            # The model is bundled inside opencv_contrib data or can be loaded
            # from file.  We attempt the file path first; if absent we skip.
            import os
            model_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "lbfmodel.yaml"
            )
            if os.path.exists(model_path):
                self._detector.loadModel(model_path)
            else:
                self._detector = None   # will use fallback
        except Exception:
            self._detector = None

        # Haar cascade used only to feed into the landmark detector
        self._cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        print(f"[FaceAligner] landmark detector: "
              f"{'LBF loaded' if self._detector else 'fallback (resize only)'}")

    # ------------------------------------------------------------------
    def align(self, face_bgr: np.ndarray) -> np.ndarray:
        """
        Align *face_bgr* (any size) and return a 112×112 BGR image.

        Steps
        -----
        1. Detect 5 landmarks (left-eye, right-eye, nose, left-mouth,
           right-mouth) via LBF if available.
        2. Compute similarity transform (scale + rotate) mapping detected
           eye centres → canonical positions.
        3. Apply warpAffine to produce the normalised crop.
        """
        if self._detector is not None:
            try:
                aligned = self._align_with_landmarks(face_bgr)
                if aligned is not None:
                    return aligned
            except Exception as e:
                print(f"[FaceAligner] landmark alignment failed ({e}), using fallback")

        # Fallback: plain resize
        return cv2.resize(face_bgr, OUTPUT_SIZE)

    # ------------------------------------------------------------------
    def _align_with_landmarks(self, face_bgr: np.ndarray):
        gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # The LBF detector needs a face rectangle
        faces = self._cascade.detectMultiScale(
            gray, scaleFactor=1.05, minNeighbors=3, minSize=(30, 30)
        )
        if len(faces) == 0:
            # Use the full image as the bounding box
            faces = np.array([[0, 0, w, h]])

        ok, landmarks = self._detector.fit(gray, faces)
        if not ok or landmarks is None or len(landmarks) == 0:
            return None

        # landmarks[0] shape: (1, 68, 2) or (1, 5, 2) depending on model
        pts = landmarks[0][0]   # shape (N, 2)

        if pts.shape[0] >= 68:
            # 68-point: average left-eye (36-41) and right-eye (42-47)
            left_eye  = pts[36:42].mean(axis=0)
            right_eye = pts[42:48].mean(axis=0)
        elif pts.shape[0] >= 5:
            # 5-point: [left_eye, right_eye, nose, left_mouth, right_mouth]
            left_eye  = pts[0]
            right_eye = pts[1]
        else:
            return None

        return self._warp(face_bgr, left_eye, right_eye)

    # ------------------------------------------------------------------
    @staticmethod
    def _warp(img: np.ndarray,
              left_eye: np.ndarray,
              right_eye: np.ndarray) -> np.ndarray:
        """
        Compute similarity transform (scale + rotate, no shear) and warp.
        """
        # Eye centres in source image
        src_pts = np.array([left_eye, right_eye], dtype=np.float32)
        # Canonical positions (scaled to OUTPUT_SIZE)
        dst_pts = np.array([CANONICAL_LEFT_EYE, CANONICAL_RIGHT_EYE],
                           dtype=np.float32)

        # Similarity transform (2×3 matrix)
        M, _ = cv2.estimateAffinePartial2D(
            src_pts, dst_pts, method=cv2.LMEDS
        )
        if M is None:
            return cv2.resize(img, OUTPUT_SIZE)

        aligned = cv2.warpAffine(img, M, OUTPUT_SIZE,
                                 flags=cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_REPLICATE)
        return aligned

    # ------------------------------------------------------------------
    @staticmethod
    def align_simple(face_bgr: np.ndarray,
                     left_eye_center: tuple,
                     right_eye_center: tuple) -> np.ndarray:
        """
        Convenience method: align when you already know eye positions
        (e.g. from an external detector like MediaPipe or dlib).

        Parameters
        ----------
        face_bgr         : The face crop BGR image.
        left_eye_center  : (x, y) pixel coords of left eye in *face_bgr*.
        right_eye_center : (x, y) pixel coords of right eye in *face_bgr*.
        """
        left_eye  = np.array(left_eye_center, dtype=np.float32)
        right_eye = np.array(right_eye_center, dtype=np.float32)
        return FaceAligner._warp(face_bgr, left_eye, right_eye)
