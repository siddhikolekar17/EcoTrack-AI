"""Shared constants: categories, statuses, lifecycle stages, badges."""

CAT_BIO = "Biodegradable"
CAT_DRY = "Dry Recyclable"
CAT_HAZ = "Hazardous / E-Waste"
CATEGORIES = [CAT_BIO, CAT_DRY, CAT_HAZ]
CATEGORY_COLORS = {CAT_BIO: "#16a34a", CAT_DRY: "#2563eb", CAT_HAZ: "#dc2626"}
CATEGORY_ICONS = {CAT_BIO: "🥬", CAT_DRY: "♻️", CAT_HAZ: "⚠️"}

ROLE_STUDENT, ROLE_MANAGER, ROLE_ADMIN = "student", "manager", "admin"
ROLES = (ROLE_STUDENT, ROLE_MANAGER, ROLE_ADMIN)
STAFF_ROLES = (ROLE_MANAGER, ROLE_ADMIN)
ROLE_LABELS = {ROLE_STUDENT: "Student", ROLE_MANAGER: "Waste Manager", ROLE_ADMIN: "Campus Admin"}

WASTE_PENDING, WASTE_VERIFIED, WASTE_REJECTED = "pending", "verified", "rejected"

EWASTE_LIFECYCLE = [
    "Registered",
    "QR Generated",
    "Collected",
    "Verified",
    "Recycler Handover",
    "Recycling Completed",
]
EWASTE_TYPES = [
    "Laptop / Desktop", "Lithium Battery", "PCB / Circuit Board", "Monitor / Display",
    "Peripheral (keyboard, mouse)", "Networking Equipment", "Lab Instrument",
    "Mobile Phone / Tablet", "Printer / Scanner", "Other",
]
EWASTE_CONDITIONS = ["Working", "Damaged", "Dead / Non-functional", "Swollen / Leaking (handle with care)"]

BIN_NORMAL, BIN_WARN, BIN_OVERFLOW_STATUS = "Normal", "Warning", "Overflow Alert"
BIN_COLORS = {BIN_NORMAL: "#16a34a", BIN_WARN: "#f59e0b", BIN_OVERFLOW_STATUS: "#dc2626"}

# (name, minimum credits, icon)
CREDIT_BADGES = [
    ("Green Starter", 10, "🌱"),
    ("Eco Warrior", 50, "🌿"),
    ("Planet Guardian", 150, "🌍"),
    ("Campus Champion", 300, "🏆"),
]
