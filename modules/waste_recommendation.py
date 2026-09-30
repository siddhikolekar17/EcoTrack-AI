"""Disposal guidance and illustrative impact estimates."""
from config import settings
from utils.constants import CAT_BIO, CAT_DRY, CAT_HAZ

RECOMMENDATIONS = {
    CAT_BIO: {
        "bin": "🟢 Green bin",
        "steps": ["Drop food scraps, peels and leaves into the green bin.",
                  "Keep it free of plastic, foil and packaging.",
                  "Campus compost pit / biogas unit collects this stream."],
        "avoid": "Do not mix with plastics, glass or metal.",
    },
    CAT_DRY: {
        "bin": "🔵 Blue bin",
        "steps": ["Empty and rinse bottles, cans and containers.",
                  "Flatten cardboard and keep paper dry.",
                  "Place in the blue bin for the recycler pick-up."],
        "avoid": "Greasy food-contaminated paper cannot be recycled - use the green bin.",
    },
    CAT_HAZ: {
        "bin": "🔴 Red hazardous / e-waste point",
        "steps": ["Never put in a general bin - batteries can ignite in compactors.",
                  "Tape the terminals of loose lithium batteries; handle swollen cells with gloves.",
                  "Register the item in the E-Waste Tracker to get a QR asset tag.",
                  "Hand over at the campus e-waste collection point."],
        "avoid": "Do not open, crush or burn electronics and batteries.",
    },
}


def get_recommendation(category: str | None) -> dict | None:
    return RECOMMENDATIONS.get(category)


def estimate_impact(category: str, weight_kg: float) -> float:
    """Illustrative CO2e avoided (kg). Factors are demo values, not audited data."""
    return round(settings.IMPACT_FACTORS.get(category, 0.0) * float(weight_kg), 2)
