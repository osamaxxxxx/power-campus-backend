"""
liveness_detector.py
====================
Lightweight liveness / anti-spoofing module that runs entirely on CPU
with no external model download.

Algorithm
---------
1. Extract Local Binary Pattern (LBP) histogram from the face crop –
   a classical texture descriptor that differs markedly between
   a real 3-D face and a flat 2-D spoof (printed photo or screen replay).
2. Also extract gradient magnitude statistics and colour channel variance.
3. Feed the concatenated feature vector to a trained SVM classifier.

Because we cannot ship a pre-trained SVM binary in the repository, the
detector starts in "adaptive" mode:
  • It collects feature statistics for real faces across the first few
    recognised frames and builds a simple one-class threshold detector.
  • Optionally you can call  train(real_samples, spoof_samples)  with BGR
    face crops to fit a proper binary SVM (requires scikit-learn).

Status values returned
----------------------
  REAL   – face passed the liveness check
  SPOOF  – face classified as a spoof attack
  UNSURE – not enough calibration data yet (treated as REAL by FaceService)
"""

from __future__ import annotations

import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional


# ── Result dataclass ─────────────────────────────────────────────────────────

@dataclass
class LivenessResult:
    status: str          # "REAL" | "SPOOF" | "UNSURE"
    score: float         # higher = more likely real (0.0 – 1.0)
    confidence: float    # 0.0 – 1.0
    features: dict = field(default_factory=dict)

    @property
    def is_live(self) -> bool:
        return self.status in ("REAL", "UNSURE")


# ── Feature extraction helpers ────────────────────────────────────────────────

def _lbp_histogram(gray: np.ndarray, num_points: int = 8,
                   radius: int = 1, num_bins: int = 32) -> np.ndarray:
    """
    Uniform LBP histogram (OpenCV-based, no skimage needed).
    Uses a circular neighbourhood with `num_points` sampling points.
    """
    h, w = gray.shape
    lbp   = np.zeros_like(gray, dtype=np.float32)

    for i in range(num_points):
        angle  = 2 * np.pi * i / num_points
        ox     = int(round(radius * np.cos(angle)))
        oy     = int(round(radius * np.sin(angle)))

        # Shifted version of the image
        shifted = np.roll(np.roll(gray.astype(np.float32), oy, axis=0), ox, axis=1)
        lbp    += ((shifted >= gray.astype(np.float32)).astype(np.float32)
                   * (2 ** i))

    hist, _ = np.histogram(lbp, bins=num_bins, range=(0, 2 ** num_points))
    total   = hist.sum() + 1e-6
    return (hist / total).astype(np.float32)


def _gradient_stats(gray: np.ndarray) -> np.ndarray:
    """Magnitude statistics of Sobel gradients – spoof faces tend to be flatter."""
    sobelx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    mag    = np.sqrt(sobelx ** 2 + sobely ** 2)
    return np.array([
        mag.mean(),
        mag.std(),
        float(np.percentile(mag, 25)),
        float(np.percentile(mag, 75)),
    ], dtype=np.float32)


def _colour_stats(bgr: np.ndarray) -> np.ndarray:
    """Per-channel mean & std – printed/screen attacks have shifted colour."""
    stats = []
    for c in range(3):
        ch = bgr[:, :, c].astype(np.float32)
        stats.extend([ch.mean() / 255.0, ch.std() / 255.0])
    return np.array(stats, dtype=np.float32)


def _fft_high_freq(gray: np.ndarray) -> np.ndarray:
    """
    Energy in high-frequency band of the FFT.
    Spoof images (especially screen replays) show Moiré patterns.
    """
    f   = np.fft.fft2(gray.astype(np.float32))
    fs  = np.fft.fftshift(f)
    mag = np.log1p(np.abs(fs))
    h, w = mag.shape
    # Exclude the low-frequency centre (inner 25 %)
    mask             = np.ones((h, w), dtype=bool)
    cy, cx           = h // 2, w // 2
    r                = min(h, w) // 8
    mask[cy-r:cy+r, cx-r:cx+r] = False
    hf_energy        = mag[mask].mean()
    total_energy     = mag.mean() + 1e-6
    return np.array([hf_energy / total_energy], dtype=np.float32)


def extract_features(face_bgr: np.ndarray) -> np.ndarray:
    """
    Build the full feature vector for a face crop.
    Input: BGR image (any size, will be resized to 64×64).
    Output: 1-D float32 array of length ~71.
    """
    face  = cv2.resize(face_bgr, (64, 64))
    gray  = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

    lbp   = _lbp_histogram(gray)            # 32-dim
    grad  = _gradient_stats(gray)           # 4-dim
    col   = _colour_stats(face)             # 6-dim
    fft   = _fft_high_freq(gray)            # 1-dim

    return np.concatenate([lbp, grad, col, fft])   # 43-dim total


# ── Main detector class ───────────────────────────────────────────────────────

class LivenessDetector:
    """
    Liveness / anti-spoofing detector.

    Modes
    -----
    • **Adaptive** (default) – calibrates from real-face observations at
      runtime.  No pre-trained weights needed.  Suitable for production
      after ~30 real frames have been processed.

    • **SVM** – full binary classifier (requires scikit-learn installed).
      Call  train(real_crops, spoof_crops)  to fit and activate it.

    Parameters
    ----------
    spoof_threshold : float
        Score below this → SPOOF.  Increase to be stricter (more rejections).
    min_calibration_frames : int
        Adaptive mode: frames before switching from UNSURE to REAL/SPOOF.
    """

    FEATURE_LEN = 43   # Must match extract_features() output length

    def __init__(self,
                 spoof_threshold: float = 0.30,
                 min_calibration_frames: int = 30):
        self.spoof_threshold        = spoof_threshold
        self.min_calibration_frames = min_calibration_frames

        # Adaptive calibration state
        self._real_mean: Optional[np.ndarray] = None
        self._real_std:  Optional[np.ndarray] = None
        self._calib_buffer: List[np.ndarray]  = []
        self._calibrated: bool                = False

        # SVM classifier (optional)
        self._svm = None

        print("[LivenessDetector] initialised – adaptive mode")

    # ── Public API ─────────────────────────────────────────────────────────

    def check(self, face_bgr: np.ndarray) -> LivenessResult:
        """
        Run liveness check on a pre-cropped face BGR image.
        Returns a LivenessResult.
        """
        if face_bgr is None or face_bgr.size == 0:
            return LivenessResult("UNSURE", 0.5, 0.0)

        feats = extract_features(face_bgr)

        # SVM path
        if self._svm is not None:
            return self._svm_check(feats)

        # Adaptive path
        return self._adaptive_check(feats)

    def train(self,
              real_crops:  List[np.ndarray],
              spoof_crops: List[np.ndarray]) -> bool:
        """
        Train a binary SVM classifier.
        Requires scikit-learn (`pip install scikit-learn`).

        Parameters
        ----------
        real_crops  : list of BGR face images labelled as REAL
        spoof_crops : list of BGR face images labelled as SPOOF

        Returns True on success, False if scikit-learn is unavailable.
        """
        try:
            from sklearn.svm import SVC
            from sklearn.preprocessing import StandardScaler
            from sklearn.pipeline import Pipeline
        except ImportError:
            print("[LivenessDetector] scikit-learn not installed – "
                  "run: pip install scikit-learn")
            return False

        real_feats  = [extract_features(img) for img in real_crops]
        spoof_feats = [extract_features(img) for img in spoof_crops]

        X = np.vstack(real_feats + spoof_feats)
        y = np.array([1] * len(real_feats) + [0] * len(spoof_feats))

        self._svm = Pipeline([
            ("scaler", StandardScaler()),
            ("svm",    SVC(kernel="rbf", probability=True,
                           class_weight="balanced", C=10.0, gamma="scale"))
        ])
        self._svm.fit(X, y)
        print(f"[LivenessDetector] SVM trained on "
              f"{len(real_feats)} real + {len(spoof_feats)} spoof samples")
        return True

    def reset_calibration(self):
        """Clear adaptive calibration state (e.g. when camera changes)."""
        self._real_mean    = None
        self._real_std     = None
        self._calib_buffer = []
        self._calibrated   = False
        print("[LivenessDetector] calibration reset")

    # ── Private helpers ─────────────────────────────────────────────────────

    def _adaptive_check(self, feats: np.ndarray) -> LivenessResult:
        """
        Adaptive one-class detector:
        - During calibration we assume the first N frames are real and
          build a mean/std model.
        - After calibration we compute z-score distance; large deviation
          → SPOOF.
        """
        if not self._calibrated:
            self._calib_buffer.append(feats)
            if len(self._calib_buffer) >= self.min_calibration_frames:
                arr             = np.array(self._calib_buffer)
                self._real_mean = arr.mean(axis=0)
                self._real_std  = arr.std(axis=0) + 1e-6
                self._calibrated = True
                print("[LivenessDetector] adaptive calibration complete "
                      f"({len(self._calib_buffer)} frames)")
            return LivenessResult("UNSURE", 0.5, 0.0,
                                  {"calibrated": False,
                                   "frames_collected": len(self._calib_buffer)})

        # z-score distance from calibrated real distribution
        z     = np.abs((feats - self._real_mean) / self._real_std)
        dist  = z.mean()          # mean normalised deviation

        # Convert distance to a 0–1 score (closer to 0 dist → score near 1)
        score = float(np.exp(-dist / 3.0))  # exponential decay

        if score < self.spoof_threshold:
            status = "SPOOF"
        else:
            status = "REAL"

        return LivenessResult(
            status     = status,
            score      = score,
            confidence = min(1.0, abs(score - self.spoof_threshold) * 5),
            features   = {"z_mean": float(dist), "score": score}
        )

    def _svm_check(self, feats: np.ndarray) -> LivenessResult:
        prob   = self._svm.predict_proba(feats.reshape(1, -1))[0]
        # prob[1] = probability of class 1 (REAL)
        score  = float(prob[1])
        status = "REAL" if score >= self.spoof_threshold else "SPOOF"
        return LivenessResult(
            status     = status,
            score      = score,
            confidence = float(abs(score - 0.5) * 2),
            features   = {"real_prob": score, "spoof_prob": float(prob[0])}
        )
