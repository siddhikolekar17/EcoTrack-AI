"""Image loading, preprocessing and quality checks."""
from __future__ import annotations

import uuid
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

from config import settings


def load_image(file) -> Image.Image:
    """Load an uploaded / camera file into an RGB PIL image (EXIF-corrected)."""
    img = Image.open(file)
    img = ImageOps.exif_transpose(img)
    return img.convert("RGB")


def to_model_array(img: Image.Image, size: int = 224) -> np.ndarray:
    """Return float32 array of shape (1, size, size, 3) with raw 0-255 values."""
    resized = ImageOps.fit(img, (size, size), method=Image.Resampling.BILINEAR)
    return np.asarray(resized, dtype="float32")[None, ...]


def blur_score(img: Image.Image) -> float:
    """Variance of Laplacian (higher = sharper). Uses OpenCV when available."""
    gray = np.asarray(img.convert("L").resize((320, 320)), dtype="float32")
    try:
        import cv2

        return float(cv2.Laplacian(gray, cv2.CV_32F).var())
    except Exception:
        lap = (-4 * gray[1:-1, 1:-1] + gray[:-2, 1:-1] + gray[2:, 1:-1]
               + gray[1:-1, :-2] + gray[1:-1, 2:])
        return float(lap.var())


def color_stats(img: Image.Image) -> tuple[float, float, float]:
    """Mean (hue 0-1, saturation 0-1, value 0-1) of a downsized HSV image."""
    hsv = np.asarray(img.resize((64, 64)).convert("HSV"), dtype="float32") / 255.0
    return float(hsv[..., 0].mean()), float(hsv[..., 1].mean()), float(hsv[..., 2].mean())


def save_upload(img: Image.Image, user_id: int) -> str:
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    path = Path(settings.UPLOAD_DIR) / f"u{user_id}_{uuid.uuid4().hex[:10]}.jpg"
    ImageOps.contain(img, (900, 900)).save(path, "JPEG", quality=85)
    return str(path)
