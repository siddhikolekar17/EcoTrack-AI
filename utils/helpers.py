"""Pure helper functions (no Streamlit imports)."""
import random
import string
from datetime import datetime

from config import settings
from utils import constants as C


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value)


def generate_asset_id() -> str:
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"ECO-EW-{datetime.now():%Y%m%d}-{suffix}"


def next_bin_id(existing_ids) -> str:
    nums = []
    for b in existing_ids:
        try:
            nums.append(int(str(b).split("-")[-1]))
        except ValueError:
            pass
    return f"BIN-{(max(nums) + 1 if nums else 1):03d}"


def bin_status(fill: float) -> str:
    if fill >= settings.BIN_OVERFLOW:
        return C.BIN_OVERFLOW_STATUS
    if fill >= settings.BIN_WARNING:
        return C.BIN_WARN
    return C.BIN_NORMAL


def format_kg(value) -> str:
    return f"{float(value or 0):.1f} kg"


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
