from PIL import Image

from modules import ai_classifier
from utils.constants import CAT_BIO, CAT_DRY, CAT_HAZ


def test_label_mapping():
    assert ai_classifier.map_label_to_category("banana") == CAT_BIO
    assert ai_classifier.map_label_to_category("water bottle") == CAT_DRY
    assert ai_classifier.map_label_to_category("laptop") == CAT_HAZ
    assert ai_classifier.map_label_to_category("cellular telephone") == CAT_HAZ
    assert ai_classifier.map_label_to_category("volcano") is None


def test_word_boundary_matching():
    # 'can' must not match inside 'scanner' / 'candle'
    assert ai_classifier.map_label_to_category("candle") is None


def test_heuristic_is_never_presented_as_ai():
    pred = ai_classifier.classify_heuristic(Image.new("RGB", (64, 64), (30, 160, 40)))
    assert pred.is_ai is False and pred.needs_verification is True


def test_hazard_always_needs_verification():
    pred = ai_classifier._finish(CAT_HAZ, "battery", 0.99, "imagenet", [])
    assert pred.needs_verification
