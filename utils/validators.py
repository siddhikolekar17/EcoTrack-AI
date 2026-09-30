"""Input validators. Each returns an error string, or None when valid."""
import re

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def clean_text(value, max_len: int = 200) -> str:
    return (value or "").strip()[:max_len]


def validate_email(email: str):
    return None if _EMAIL.match(email or "") else "Enter a valid email address."


def validate_password(password: str):
    return None if len(password or "") >= 6 else "Password must be at least 6 characters."


def validate_name(name: str):
    return None if len((name or "").strip()) >= 2 else "Enter your full name."


def validate_weight(weight):
    try:
        w = float(weight)
    except (TypeError, ValueError):
        return "Weight must be a number."
    return None if 0 < w <= 500 else "Weight must be between 0 and 500 kg."


def validate_quantity(quantity):
    try:
        q = int(quantity)
    except (TypeError, ValueError):
        return "Quantity must be a whole number."
    return None if 1 <= q <= 1000 else "Quantity must be between 1 and 1000."
