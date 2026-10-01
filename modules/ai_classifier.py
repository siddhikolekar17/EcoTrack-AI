"""AI waste classification.

Backends (auto-selected, best first):
  1. custom    - models/waste_classifier/model.keras + labels.json
  2. imagenet  - pretrained MobileNetV2 with a label -> waste-category mapping
  3. heuristic - colour-statistics guess. NOT AI; always flagged for verification.

The classifier returns a structured Prediction containing:
- waste category
- detected item label
- confidence score
- AI backend
- verification status
- disposal guidance
- alternative predictions
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


# ---------------------------------------------------------------------------
# ImageNet label mappings
# ---------------------------------------------------------------------------

# Electronic and hazardous items are checked first because incorrectly
# classifying e-waste as ordinary recyclable waste can create safety risks.
HAZ_KEYS = (
    "cellular telephone", "cell phone", "mobile phone", "laptop", "notebook",
    "mouse", "computer keyboard", "keyboard", "space bar", "monitor",
    "screen", "desktop computer", "hard disc", "hard disk", "modem",
    "printer", "remote control", "joystick", "ipod", "battery", "circuit",
    "pcb", "router", "radio", "tape player", "cassette player", "projector",
    "photocopier", "television", "loudspeaker", "speaker", "oscilloscope",
    "syringe", "power drill", "electric guitar", "iron",
)

# Common dry/recyclable materials and containers.
DRY_KEYS = (
    "water bottle", "water jug", "pop bottle", "beer bottle", "wine bottle",
    "pill bottle", "bottle", "plastic bag", "carton", "cardboard", "envelope",
    "packet", "paper towel", "tissue", "can", "tin", "milk can", "bucket",
    "pail", "crate", "box", "book jacket", "newspaper", "jar", "cup", "mug",
    "bag", "wrapper", "toilet tissue",
)

# Common biodegradable food and organic items.
BIO_KEYS = (
    "banana", "orange", "lemon", "strawberry", "pineapple", "granny smith",
    "pomegranate", "fig", "broccoli", "cauliflower", "cucumber", "zucchini",
    "mushroom", "corn", "ear", "head cabbage", "artichoke", "bell pepper",
    "custard apple", "jackfruit", "acorn squash", "butternut squash",
    "spaghetti squash", "hay", "leaf", "french loaf", "bagel", "pretzel",
    "pizza", "cheeseburger", "hotdog", "burrito", "carbonara", "guacamole",
    "mashed potato", "meat loaf", "dough", "apple",
)


# ---------------------------------------------------------------------------
# Disposal guidance
# ---------------------------------------------------------------------------

# Category-specific disposal recommendations shown with the AI result.
DISPOSAL_GUIDANCE = {
    CAT_BIO: (
        "Place this item in the biodegradable/wet-waste bin. "
        "Keep it separate from dry and hazardous waste."
    ),
    CAT_DRY: (
        "Place this item in the dry/recyclable-waste bin. "
        "Keep recyclable materials clean and separated."
    ),
    CAT_HAZ: (
        "Do not place this item in normal waste bins. "
        "Submit electronic or hazardous items to an authorised "
        "e-waste/hazardous-waste collection facility."
    ),
}


def get_disposal_guidance(category: str | None) -> str:
    """Return disposal guidance based on the predicted waste category."""
    return DISPOSAL_GUIDANCE.get(
        category,
        "Category could not be determined. Please verify the item manually.",
    )


def _matches(label: str, keywords) -> bool:
    """Check whether a model label matches one of the known waste keywords."""
    norm = " " + re.sub(r"[^a-z0-9]+", " ", label.lower()) + " "
    return any(f" {k} " in norm for k in keywords)


def map_label_to_category(label: str) -> str | None:
    """Map a model label to one of the supported waste categories.

    Hazardous/e-waste is checked first to make the classification safer.
    """
    for keys, category in (
        (HAZ_KEYS, CAT_HAZ),
        (DRY_KEYS, CAT_DRY),
        (BIO_KEYS, CAT_BIO),
    ):
        if _matches(label, keys):
            return category

    return None


# ---------------------------------------------------------------------------
# Prediction result
# ---------------------------------------------------------------------------

@dataclass
class Prediction:
    """Structured result returned by the waste classifier."""

    category: str | None
    label: str
    confidence: float
    backend: str
    is_ai: bool
    needs_verification: bool
    message: str = ""
    disposal_guidance: str = ""
    top_k: list = field(default_factory=list)

    @property
    def confidence_percent(self) -> float:
        """Return confidence as a percentage for UI display."""
        return round(self.confidence * 100, 1)


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=1)
def _load_backend():
    """Load the best available classification backend once."""
    try:
        import tensorflow as tf  # noqa: WPS433
    except Exception:
        return ("heuristic", None)

    custom = settings.MODEL_DIR / "model.keras"
    labels = settings.MODEL_DIR / "labels.json"

    try:
        # Prefer the project's own trained model when available.
        if custom.exists() and labels.exists():
            return (
                "custom",
                (
                    tf.keras.models.load_model(custom),
                    json.loads(labels.read_text()),
                ),
            )

        # Otherwise use MobileNetV2 as the fallback AI model.
        return (
            "imagenet",
            tf.keras.applications.MobileNetV2(weights="imagenet"),
        )
    except Exception:
        return ("heuristic", None)


def backend_name() -> str:
    """Return a human-readable name for the active classification backend."""
    kind = _load_backend()[0]

    return {
        "custom": "Custom-trained model",
        "imagenet": "MobileNetV2 (ImageNet, mapped)",
        "heuristic": "Colour heuristic (NOT AI - install TensorFlow)",
    }[kind]


# ---------------------------------------------------------------------------
# Heuristic fallback
# ---------------------------------------------------------------------------

def classify_heuristic(img: Image.Image) -> Prediction:
    """Provide a basic non-AI estimate when TensorFlow is unavailable.

    Heuristic results always require manual verification.
    """
    hue, sat, val = image_processing.color_stats(img)

    if val < 0.28:
        category = CAT_HAZ
    elif sat > 0.38 and 0.05 < hue < 0.45:
        category = CAT_BIO
    else:
        category = CAT_DRY

    return Prediction(
        category=category,
        label="colour-based guess",
        confidence=0.35,
        backend="heuristic",
        is_ai=False,
        needs_verification=True,
        message=(
            "Heuristic estimate only - this is not an AI prediction. "
            "Please confirm the category."
        ),
        disposal_guidance=get_disposal_guidance(category),
        top_k=[],
    )


# ---------------------------------------------------------------------------
# Final result handling
# ---------------------------------------------------------------------------

def _finish(category, label, conf, backend, top_k) -> Prediction:
    """Build the final AI prediction with confidence and safety checks."""

    conf = float(conf)

    # Hazardous items and low-confidence results always require verification.
    needs_verification = (
        category is None
        or category == CAT_HAZ
        or conf < settings.CONFIDENCE_THRESHOLD
    )

    if category is None:
        message = (
            "Item could not be confidently classified. "
            "Please select the category manually."
        )
    elif category == CAT_HAZ:
        message = (
            "Hazardous / e-waste item detected. "
            "Admin verification is required."
        )
    elif conf < settings.CONFIDENCE_THRESHOLD:
        message = (
            f"Low confidence ({conf * 100:.1f}%). "
            "An admin should verify this classification."
        )
    else:
        message = (
            f"AI classification confidence: {conf * 100:.1f}%."
        )

    return Prediction(
        category=category,
        label=label,
        confidence=conf,
        backend=backend,
        is_ai=True,
        needs_verification=needs_verification,
        message=message,
        disposal_guidance=get_disposal_guidance(category),
        top_k=top_k,
    )


# ---------------------------------------------------------------------------
# Main image classification
# ---------------------------------------------------------------------------

def classify_image(img: Image.Image) -> Prediction:
    """Classify a waste image using the best available AI backend."""

    kind, model = _load_backend()

    # TensorFlow is unavailable, so use the clearly labelled fallback.
    if kind == "heuristic":
        return classify_heuristic(img)

    try:
        arr = image_processing.to_model_array(img, 224)

        # ---------------------------------------------------------------
        # Custom-trained model
        # ---------------------------------------------------------------
        if kind == "custom":
            net, labels = model

            probabilities = net.predict(arr, verbose=0)[0]
            order = np.argsort(probabilities)[::-1][:3]

            top = [
                (
                    labels[i],
                    float(probabilities[i]),
                    labels[i],
                )
                for i in order
            ]

            best = top[0]

            # Support both direct category labels and free-text labels.
            category = (
                best[2]
                if best[2] in CATEGORIES
                else map_label_to_category(best[0])
            )

            return _finish(
                category,
                best[0],
                best[1],
                "custom",
                top,
            )

        # ---------------------------------------------------------------
        # MobileNetV2 / ImageNet
        # ---------------------------------------------------------------
        import tensorflow as tf

        x = tf.keras.applications.mobilenet_v2.preprocess_input(
            arr.copy()
        )

        decoded = tf.keras.applications.mobilenet_v2.decode_predictions(
            model.predict(x, verbose=0),
            top=8,
        )[0]

        top = []
        category_totals = {}

        # Convert ImageNet labels into the project's three waste categories.
        for _, name, probability in decoded:
            clean_name = name.replace("_", " ")
            probability = float(probability)

            category = map_label_to_category(clean_name)

            top.append(
                (
                    clean_name,
                    probability,
                    category,
                )
            )

            if category:
                category_totals[category] = (
                    category_totals.get(category, 0.0)
                    + probability
                )

        # No recognised waste category was found.
        if not category_totals:
            return _finish(
                None,
                top[0][0],
                top[0][1],
                "imagenet",
                top,
            )

        # Select the category with the strongest combined probability.
        best_category = max(
            category_totals,
            key=category_totals.get,
        )

        best_label = next(
            item[0]
            for item in top
            if item[2] == best_category
        )

        return _finish(
            best_category,
            best_label,
            category_totals[best_category],
            "imagenet",
            top,
        )

    except Exception as exc:
        # Never allow a model error to crash the Streamlit application.
        prediction = classify_heuristic(img)

        prediction.message = (
            f"Model error ({exc.__class__.__name__}); "
            "showing a heuristic estimate (not AI). "
            "Manual verification is required."
        )

        return prediction