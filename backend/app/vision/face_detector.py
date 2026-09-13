import cv2
import numpy as np
from pathlib import Path
from typing import Tuple
from app.core.exceptions import NoFaceDetectedException, InvalidImageException

# Absolute path to the models directory, anchored at this file's location.
# This file lives at: backend/app/vision/face_detector.py
# So: __file__ -> .../vision/ -> up 1 -> .../app/ -> models/
_VISION_DIR = Path(__file__).resolve().parent          # .../vision/
_APP_DIR = _VISION_DIR.parent                          # .../app/
_CASCADE_DEFAULT = _APP_DIR / "models" / "haarcascade_frontalface_default.xml"


class FaceDetector:
    """
    OpenCV Haar Cascade face detector.
    Requires opencv-python-headless 4.x (CascadeClassifier API).
    Falls back to absolute model path resolution from __file__ location.
    """

    def __init__(self, cascade_path: str):
        # Check that CascadeClassifier is available (removed in cv2 5.0)
        if not hasattr(cv2, "CascadeClassifier"):
            raise RuntimeError(
                f"cv2.CascadeClassifier not found (installed cv2 version: {cv2.__version__}). "
                "MoodTunes requires opencv-python-headless==4.x. "
                "Reinstall: pip install 'opencv-python-headless==4.10.0.84'"
            )

        # Resolve cascade path absolutely
        cascade_p = Path(cascade_path)
        if not cascade_p.is_absolute():
            # Try relative to backend dir
            backend_dir = _APP_DIR.parent
            cascade_p = (backend_dir / cascade_path).resolve()

        # Fallback to canonical location if resolved path doesn't exist
        if not cascade_p.exists():
            cascade_p = _CASCADE_DEFAULT

        if not cascade_p.exists():
            raise RuntimeError(
                f"Haar Cascade XML not found. Tried: '{cascade_path}' and '{_CASCADE_DEFAULT}'"
            )

        self.cascade = cv2.CascadeClassifier(str(cascade_p))
        if self.cascade.empty():
            raise RuntimeError(
                f"Failed to load Haar Cascade classifier from '{cascade_p}'"
            )

    def detect_largest_face(self, image_bytes: bytes) -> Tuple[np.ndarray, Tuple[int, int, int, int]]:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise InvalidImageException("Could not decode image from provided bytes.")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = self.cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
        )

        if len(faces) == 0:
            raise NoFaceDetectedException()

        largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
        return img, tuple(largest_face)
