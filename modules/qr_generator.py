"""QR code generation and decoding for e-waste asset tags."""
from __future__ import annotations

import io
import json
from pathlib import Path

import numpy as np
import qrcode
from qrcode.constants import ERROR_CORRECT_H

from config import settings


def build_payload(asset_id: str, item: str = "", department: str = "") -> str:
    return json.dumps({"app": "EcoTrack AI", "asset_id": asset_id, "item": item, "dept": department},
                      separators=(",", ":"))


def _make(payload: str):
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=8, border=3)
    qr.add_data(payload)
    qr.make(fit=True)
    return qr.make_image(fill_color="#0f5132", back_color="white").convert("RGB")


def generate_qr(asset_id: str, payload: str | None = None) -> str:
    """Save a QR PNG for the asset and return its path."""
    settings.QR_DIR.mkdir(parents=True, exist_ok=True)
    path = Path(settings.QR_DIR) / f"{asset_id}.png"
    _make(payload or build_payload(asset_id)).save(path)
    return str(path)


def qr_png_bytes(payload: str) -> bytes:
    buf = io.BytesIO()
    _make(payload).save(buf, format="PNG")
    return buf.getvalue()


def extract_asset_id(text: str) -> str | None:
    """Accept either the JSON payload or a bare asset ID."""
    text = (text or "").strip()
    try:
        data = json.loads(text)
        return data.get("asset_id")
    except (ValueError, AttributeError):
        return text or None


def decode_qr(img) -> str | None:
    """Decode a QR code from a PIL image using OpenCV. Returns the raw text or None."""
    try:
        import cv2
    except Exception:
        return None
    arr = cv2.cvtColor(np.asarray(img.convert("RGB")), cv2.COLOR_RGB2BGR)
    text, _, _ = cv2.QRCodeDetector().detectAndDecode(arr)
    return text or None
