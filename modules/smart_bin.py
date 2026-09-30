"""Smart-bin telemetry: status, predictive full-time, priority, simulation."""
from __future__ import annotations

import random

import numpy as np
import pandas as pd

from database import bin_repository, ewaste_repository
from utils.constants import BIN_COLORS
from utils.helpers import bin_status, clamp, now_iso, parse_iso

status_for = bin_status


def _since_last_collection(readings: list[dict]) -> list[dict]:
    """Drop readings before the most recent emptying (a drop of >10 points)."""
    start = 0
    for i in range(1, len(readings)):
        if readings[i - 1]["fill_level"] - readings[i]["fill_level"] > 10:
            start = i
    return readings[start:]


def predict_hours_to_full(readings: list[dict], target: float = 100.0):
    """Linear fit on recent readings -> hours until the bin reaches `target`%. None if unknown."""
    pts = _since_last_collection(readings)
    if len(pts) < 3:
        return None
    t0 = parse_iso(pts[0]["recorded_at"])
    xs = np.array([(parse_iso(p["recorded_at"]) - t0).total_seconds() / 3600 for p in pts])
    ys = np.array([p["fill_level"] for p in pts], dtype=float)
    if xs.max() - xs.min() < 0.5:
        return None
    slope, _ = np.polyfit(xs, ys, 1)
    if slope <= 0.05:
        return None
    return round(max((target - ys[-1]) / slope, 0.0), 1)


def priority_score(fill: float, hours_to_full) -> float:
    bonus = 0
    if hours_to_full is not None:
        bonus = 20 if hours_to_full < 6 else 10 if hours_to_full < 12 else 0
    return round(min(fill + bonus, 120), 1)


def priority_label(score: float) -> str:
    return "Critical" if score >= 100 else "High" if score >= 80 else "Medium" if score >= 60 else "Low"


def record_reading(bin_id: str, fill: float) -> str:
    fill = round(clamp(fill, 0, 100), 1)
    bin_repository.update_fill(bin_id, fill)
    return bin_status(fill)


def simulate_tick(rng: random.Random | None = None) -> int:
    """Advance every bin by a random amount, as an IoT sensor would report."""
    rng = rng or random.Random()
    bins = bin_repository.list_bins()
    for b in bins:
        record_reading(b["bin_id"], b["fill_level"] + rng.uniform(0.5, 7.0))
    return len(bins)


def collect(bin_id: str, user_id: int) -> None:
    """Mark a bin emptied and write a collection log entry."""
    b = bin_repository.get_bin(bin_id)
    if not b:
        raise ValueError("Unknown bin.")
    before = b["fill_level"]
    record_reading(bin_id, 0.0)
    ewaste_repository.add_log("Bin collected", bin_id=bin_id, status="Emptied",
                              notes=f"Collected at {before:.0f}% full", performed_by=user_id)


def bins_dataframe() -> pd.DataFrame:
    rows = []
    for b in bin_repository.list_bins():
        hrs = predict_hours_to_full(bin_repository.get_readings(b["bin_id"], hours=24))
        score = priority_score(b["fill_level"], hrs)
        rows.append({**b, "hours_to_full": hrs, "score": score, "priority": priority_label(score),
                     "color": BIN_COLORS[b["status"]], "size": 25 + b["fill_level"] * 0.6})
    cols = ["bin_id", "location", "category", "capacity_l", "fill_level", "status", "lat", "lon",
            "updated_at", "hours_to_full", "score", "priority", "color", "size"]
    df = pd.DataFrame(rows, columns=cols)
    return df.sort_values("score", ascending=False).reset_index(drop=True)


def collection_route(df: pd.DataFrame) -> pd.DataFrame:
    """Bins that need collecting now (warning or worse, or predicted full within 12 h)."""
    mask = (df["fill_level"] >= 70) | (df["hours_to_full"].fillna(999) < 12)
    return df[mask].sort_values("score", ascending=False)
