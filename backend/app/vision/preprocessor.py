import cv2
import numpy as np
from typing import Tuple

def preprocess_face(img: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
    """
    Takes an image (BGR) and bounding box (x, y, w, h), crops the face ROI,
    converts to grayscale, resizes to 48x48, normalizes pixels [0, 1],
    and reshapes to input shape tensor (1, 48, 48, 1).
    """
    x, y, w, h = bbox
    
    # Ensure coordinates stay within image bounds
    h_img, w_img = img.shape[:2]
    x = max(0, x)
    y = max(0, y)
    w = min(w_img - x, w)
    h = min(h_img - y, h)
    
    roi_bgr = img[y:y + h, x:x + w]
    roi_gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
    
    roi_resized = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)
    
    # Normalize pixel intensity 0..255 -> 0.0..1.0
    normalized = roi_resized.astype("float32") / 255.0
    
    # Reshape to (1, 48, 48, 1) for Keras batch prediction
    tensor = np.expand_dims(np.expand_dims(normalized, axis=-1), axis=0)
    return tensor
