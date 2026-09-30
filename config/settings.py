"""Central application configuration."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "ecotrack.db"
QR_DIR = BASE_DIR / "generated" / "qr_codes"
UPLOAD_DIR = BASE_DIR / "generated" / "uploads"
MODEL_DIR = BASE_DIR / "models" / "waste_classifier"
ASSETS_DIR = BASE_DIR / "assets"

APP_NAME = "EcoTrack AI"
APP_TAGLINE = "Intelligent Waste Segregation & E-Waste Lifecycle Management"

# Green credit rules (demo values - tune for your campus policy)
CREDIT_RULES = {
    "Biodegradable": 5,
    "Dry Recyclable": 10,
    "Hazardous / E-Waste": 25,
    "ewaste_verified": 25,      # asset verified by admin
    "recycling_completed": 15,  # certified recycling closed
}

# Smart bin thresholds (percent full)
BIN_WARNING = 70
BIN_OVERFLOW = 90

# AI classifier
CONFIDENCE_THRESHOLD = 0.50   # below this -> manual verification flag
BLUR_THRESHOLD = 60.0         # Laplacian variance below this -> "blurry" warning

# Illustrative CO2e avoided per kg correctly segregated (NOT audited figures)
IMPACT_FACTORS = {
    "Biodegradable": 0.30,
    "Dry Recyclable": 1.50,
    "Hazardous / E-Waste": 2.00,
}

# Campus map centre for demo bins (Kolhapur)
MAP_CENTER = (16.7050, 74.2433)
