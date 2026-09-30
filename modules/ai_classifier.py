"""AI waste classification.

Backends (auto-selected, best first):
  1. custom   - models/waste_classifier/model.keras + labels.json (your trained model)
  2. imagenet - pretrained MobileNetV2 (ImageNet) with a label -> waste-category mapping
  3. heuristic- colour-statistics guess. NOT AI; always flagged for manual verification.
"""
from __future__ import annotations

import functools
import json
import re
from dataclasses import dataclass, field

import numpy as np
from PIL import Image

from config import settings
from utils import image_processing
from utils.constants import CAT_BIO, CAT_DRY, CAT_HAZ, CATEGORIES

HAZ_KEYS = (
    "cellular telephone", "cell phone", "mobile phone", "laptop", "notebook", "mouse", "computer keyboard",
    "keyboard", "space bar", "monitor", "screen", "desktop computer", "hard disc", "hard disk", "modem",
    "printer", "remote control", "joystick", "ipod", "battery", "circuit", "pcb", "router", "radio",
    "tape player", "cassette player", "projector", "photocopier", "television", "loudspeaker", "speaker",
    "oscilloscope", "syringe", "power drill", "electric guitar", "iron",
)
DRY_KEYS = (
    "water bottle", "water jug", "pop bottle", "beer bottle", "wine bottle", "pill bottle", "bottle",
    "plastic bag", "carton", "cardboard", "envelope", "packet", "paper towel", "tissue", "can", "tin",
    "milk can", "bucket", "pail", "crate", "box", "book jacket", "newspaper", "jar", "cup", "mug",
    "bag", "wrapper", "toilet tissue",
)
BIO_KEYS = (
    "banana", "orange", "lemon", "strawberry", "pineapple", "granny smith", "pomegranate", "fig",
    "broccoli", "cauliflower", "cucumber", "zucchini", "mushroom", "corn", "ear", "head cabbage",
    "artichoke", "bell pepper", "custard apple", "jackfruit", "acorn squash", "butternut squash",
    "spaghetti squash", "hay", "leaf", "french loaf", "bagel", "pretzel", "pizza", "cheeseburger",
    "hotdog", "burrito", "carbonara", "guacamole", "mashed potato", "meat loaf", "dough", "apple",
)


def _matches(label: str, keywords) -> bool:
    norm = " " + re.sub(r"[^a-z0-9]+", " ", label.lower()) + " "
    return any(f" {k} " in norm for k in keywords)


def map_label_to_category(label: str) -> str | None:
    """Map a free-text model label to one of the three waste categories (hazard first = cautious)."""
    for keys, cat in ((HAZ_KEYS, CAT_HAZ), (DRY_KEYS, CAT_DRY), (BIO_KEYS, CAT_BIO)):
        if _matches(label, keys):
            return cat
    return None


@dataclass
class Prediction:
    category: str | None
    label: str
    confidence: float
    backend: str
    is_ai: bool
    needs_verification: bool
    message: str = ""
    top_k: list = field(default_factory=list)  # [(label, prob, mapped_category)]


@functools.lru_cache(maxsize=1)
def _load_backend():
    try:
        import tensorflow as tf  # noqa: WPS433
    except Exception:
        return ("heuristic", None)
    custom, labels = settings.MODEL_DIR / "model.keras", settings.MODEL_DIR / "labels.json"
    try:
        if custom.exists() and labels.exists():
            return ("custom", (tf.keras.models.load_model(custom), json.loads(labels.read_text())))
        return ("imagenet", tf.keras.applications.MobileNetV2(weights="imagenet"))
    except Exception:
        return ("heuristic", None)


def backend_name() -> str:
    kind = _load_backend()[0]
    return {"custom": "Custom-trained model", "imagenet": "MobileNetV2 (ImageNet, mapped)",
            "heuristic": "Colour heuristic (NOT AI - install TensorFlow)"}[kind]


def classify_heuristic(img: Image.Image) -> Prediction:
    hue, sat, val = image_processing.color_stats(img)
    if val < 0.28:
        cat = CAT_HAZ
    elif sat > 0.38 and 0.05 < hue < 0.45:
        cat = CAT_BIO
    else:
        cat = CAT_DRY
    return Prediction(cat, "colour-based guess", 0.35, "heuristic", False, True,
                      "Heuristic estimate only - this is not an AI prediction. Please confirm the category.")


def _finish(category, label, conf, backend, top_k) -> Prediction:
    needs = category is None or category == CAT_HAZ or conf < settings.CONFIDENCE_THRESHOLD
    if category is None:
        msg = "Item not confidently recognised as waste - please choose the category manually."
    elif category == CAT_HAZ:
        msg = "Hazardous / e-waste items always go through admin verification."
    elif conf < settings.CONFIDENCE_THRESHOLD:
        msg = "Low confidence - an admin will double-check this submission."
    else:
        msg = ""
    return Prediction(category, label, float(conf), backend, True, needs, msg, top_k)


def classify_image(img: Image.Image) -> Prediction:
    kind, model = _load_backend()
    if kind == "heuristic":
        return classify_heuristic(img)
    try:
        arr = image_processing.to_model_array(img, 224)
        if kind == "custom":
            net, labels = model
            probs = net.predict(arr, verbose=0)[0]
            order = np.argsort(probs)[::-1][:3]
            top = [(labels[i], float(probs[i]), labels[i]) for i in order]
            best = top[0]
            return _finish(best[2] if best[2] in CATEGORIES else None, best[0], best[1], "custom", top)

        import tensorflow as tf
        x = tf.keras.applications.mobilenet_v2.preprocess_input(arr.copy())
        decoded = tf.keras.applications.mobilenet_v2.decode_predictions(model.predict(x, verbose=0), top=8)[0]
        top, totals = [], {}
        for _, name, prob in decoded:
            cat = map_label_to_category(name.replace("_", " "))
            top.append((name.replace("_", " "), float(prob), cat))
            if cat:
                totals[cat] = totals.get(cat, 0.0) + float(prob)
        if not totals:
            return _finish(None, top[0][0], top[0][1], "imagenet", top)
        best_cat = max(totals, key=totals.get)
        best_label = next(t[0] for t in top if t[2] == best_cat)
        return _finish(best_cat, best_label, totals[best_cat], "imagenet", top)
    except Exception as exc:  # never crash the UI on model errors
        pred = classify_heuristic(img)
        pred.message = f"Model error ({exc.__class__.__name__}); showing heuristic estimate (not AI)."
        return pred
