
"""Schema creation and demo data seeding."""

import csv
import json
import random
from datetime import datetime, timedelta

from config import settings
from database import (
    bin_repository,
    rewards_repository,
    user_repository,
    waste_repository,
)
from database.db_connection import get_connection, query_one
from utils.helpers import bin_status


SCHEMA = """
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('student','manager','admin')),
    credits INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS waste_records(
    waste_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    category TEXT NOT NULL,
    item_label TEXT,
    confidence REAL,
    weight_kg REAL NOT NULL DEFAULT 0,
    image_path TEXT,
    model_name TEXT,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK(status IN ('pending','verified','rejected')),
    verified INTEGER NOT NULL DEFAULT 0,
    verified_by INTEGER REFERENCES users(user_id),
    verified_at TEXT,
    review_note TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ewaste_assets(
    asset_id TEXT PRIMARY KEY,
    item TEXT NOT NULL,
    item_type TEXT,
    department TEXT,
    item_condition TEXT,
    quantity INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL,
    qr_path TEXT,
    notes TEXT,
    registered_by INTEGER REFERENCES users(user_id),
    recycler_name TEXT,
    destination TEXT,
    certificate_no TEXT,
    handover_date TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS smart_bins(
    bin_id TEXT PRIMARY KEY,
    location TEXT NOT NULL,
    category TEXT NOT NULL,
    capacity_l INTEGER NOT NULL DEFAULT 120,
    fill_level REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'Normal',
    lat REAL,
    lon REAL,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS bin_readings(
    reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bin_id TEXT NOT NULL REFERENCES smart_bins(bin_id),
    fill_level REAL NOT NULL,
    recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS rewards(
    reward_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    points INTEGER NOT NULL,
    activity TEXT NOT NULL,
    ref_type TEXT,
    ref_id TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS collection_logs(
    collection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id TEXT REFERENCES ewaste_assets(asset_id),
    bin_id TEXT REFERENCES smart_bins(bin_id),
    action TEXT NOT NULL,
    destination TEXT,
    status TEXT,
    notes TEXT,
    performed_by INTEGER REFERENCES users(user_id),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notifications(
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT,
    ref TEXT,
    is_read INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_waste_user
ON waste_records(user_id, status);

CREATE INDEX IF NOT EXISTS idx_readings_bin
ON bin_readings(bin_id, recorded_at);

CREATE INDEX IF NOT EXISTS idx_rewards_user
ON rewards(user_id);

CREATE INDEX IF NOT EXISTS idx_logs_asset
ON collection_logs(asset_id);
"""


DEMO_USERS = [
    ("Campus Admin", "admin@ecotrack.demo", "admin123", "admin"),
    ("Waste Manager", "manager@ecotrack.demo", "manager123", "manager"),
    ("Siddhi Kolekar", "siddhi@ecotrack.demo", "student123", "student"),
    ("Aarav Patil", "aarav@ecotrack.demo", "student123", "student"),
    ("Meera Jadhav", "meera@ecotrack.demo", "student123", "student"),
    ("Rohan Deshmukh", "rohan@ecotrack.demo", "student123", "student"),
]


DEFAULT_BINS = [
    {
        "bin_id": "BIN-001",
        "location": "Main Canteen",
        "category": "Biodegradable",
        "capacity_l": 120,
        "lat": 16.7052,
        "lon": 74.2431,
        "fill_level": 35,
    },
    {
        "bin_id": "BIN-002",
        "location": "Library Entrance",
        "category": "Dry Recyclable",
        "capacity_l": 120,
        "lat": 16.7047,
        "lon": 74.2440,
        "fill_level": 78,
    },
    {
        "bin_id": "BIN-003",
        "location": "Computer Lab Block",
        "category": "Hazardous / E-Waste",
        "capacity_l": 80,
        "lat": 16.7056,
        "lon": 74.2427,
        "fill_level": 96,
    },
]


def init_db() -> None:
    """Create database tables and indexes."""

    conn = get_connection()

    try:
        conn.executescript(SCHEMA)
        conn.commit()

    finally:
        conn.close()


def _load_json(path):
    """Load JSON data safely."""

    try:
        return json.loads(path.read_text(encoding="utf-8"))

    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def seed_demo_data() -> None:
    """Populate demo users, bins, sensor history, waste and e-waste."""

    from modules import ewaste_manager

    rnd = random.Random(42)
    now = datetime.now()

    # Create demo users
    for name, email, pw, role in DEMO_USERS:
        try:
            user_repository.create_user(name, email, pw, role)

        except ValueError:
            pass

    admin = user_repository.get_user_by_email(
        "admin@ecotrack.demo"
    )

    # Create smart bins
    bins = (
        _load_json(settings.DATA_DIR / "sample_bins.json")
        or DEFAULT_BINS
    )

    for b in bins:

        if bin_repository.get_bin(b["bin_id"]):
            continue

        final = float(b["fill_level"])

        bin_repository.add_bin(
            b["bin_id"],
            b["location"],
            b["category"],
            b["capacity_l"],
            b["lat"],
            b["lon"],
            fill_level=0.0,
        )

        start = max(
            2.0,
            final - rnd.uniform(18, 38),
        )

        for i in range(13):

            ts = (
                now - timedelta(hours=24 - 2 * i)
            ).isoformat(timespec="seconds")

            val = (
                start
                + (final - start) * i / 12
                + rnd.uniform(-1.2, 1.2)
            )

            bin_repository.add_reading_only(
                b["bin_id"],
                round(max(0, min(100, val)), 1),
                ts,
            )

        bin_repository.update_fill(
            b["bin_id"],
            final,
        )

    # Seed historical waste records
    csv_path = settings.DATA_DIR / "sample_waste_data.csv"

    if (
        csv_path.exists()
        and not query_one(
            "SELECT 1 AS x FROM waste_records LIMIT 1"
        )
    ):

        with open(
            csv_path,
            newline="",
            encoding="utf-8",
        ) as fh:

            for row in csv.DictReader(fh):

                u = user_repository.get_user_by_email(
                    row["student_email"]
                )

                if not u:
                    continue

                created = (
                    now
                    - timedelta(
                        days=int(row["days_ago"]),
                        hours=rnd.randint(0, 10),
                    )
                ).isoformat(timespec="seconds")

                wid = waste_repository.add_record(
                    u["user_id"],
                    row["category"],
                    row["item_label"],
                    round(rnd.uniform(0.72, 0.97), 2),
                    float(row["weight_kg"]),
                    None,
                    "seed-data",
                    created,
                )

                if row["status"] == "verified":

                    waste_repository.set_status(
                        wid,
                        "verified",
                        admin["user_id"],
                        "seed",
                        created,
                    )

                    rewards_repository.add_reward(
                        u["user_id"],
                        settings.CREDIT_RULES[row["category"]],
                        f"Verified disposal: {row['category']}",
                        "waste",
                        wid,
                        created,
                    )

    # Seed demo e-waste assets
    if not query_one(
        "SELECT 1 AS x FROM ewaste_assets LIMIT 1"
    ):

        sid = user_repository.get_user_by_email(
            "siddhi@ecotrack.demo"
        )["user_id"]

        aid = user_repository.get_user_by_email(
            "aarav@ecotrack.demo"
        )["user_id"]

        mid = user_repository.get_user_by_email(
            "meera@ecotrack.demo"
        )["user_id"]

        demo_assets = [
            (
                "Dell Latitude E6440",
                "Laptop / Desktop",
                "Computer Science Lab",
                "Dead / Non-functional",
                1,
                sid,
                2,
            ),
            (
                "Li-ion battery packs",
                "Lithium Battery",
                "Electronics Lab",
                "Swollen / Leaking (handle with care)",
                6,
                aid,
                1,
            ),
            (
                "Arduino / PCB scrap",
                "PCB / Circuit Board",
                "ECE Department",
                "Damaged",
                12,
                mid,
                3,
            ),
            (
                "CRT monitors",
                "Monitor / Display",
                "Physics Lab",
                "Dead / Non-functional",
                4,
                sid,
                4,
            ),
            (
                "Old keyboards & mice",
                "Peripheral (keyboard, mouse)",
                "AI & ML Lab",
                "Working",
                20,
                aid,
                0,
            ),
        ]

        for (
            item,
            typ,
            dept,
            cond,
            qty,
            owner,
            steps,
        ) in demo_assets:

            asset = ewaste_manager.register_asset(
                owner,
                item,
                typ,
                dept,
                cond,
                qty,
            )

            for _ in range(steps):

                ewaste_manager.advance(
                    asset["asset_id"],
                    admin["user_id"],
                    recycler="GreenCycle Recyclers Pvt Ltd",
                    destination="Pune Authorised E-Waste Facility",
                    certificate="CERT-DEMO-2026-001",
                    notes="Seeded demo data",
                )


def ensure_ready() -> None:
    """Create tables and seed demo data on first run."""

    init_db()

    if user_repository.count_users() == 0:
        seed_demo_data()


def reset_demo() -> None:
    """
    Safely reset demo records without deleting the SQLite file.

    This avoids Windows WinError 32 caused by deleting a database
    that is currently open or locked by another process.
    """

    # Ensure all tables exist
    init_db()

    conn = get_connection()

    try:
        # Disable FK checks before beginning the transaction
        conn.execute("PRAGMA foreign_keys = OFF")

        # Start a write transaction
        conn.execute("BEGIN IMMEDIATE")

        # Delete dependent records first
        tables = [
            "collection_logs",
            "bin_readings",
            "rewards",
            "waste_records",
            "ewaste_assets",
            "smart_bins",
            "notifications",
            "users",
        ]

        for table in tables:
            conn.execute(f"DELETE FROM {table}")

        # Reset auto-increment counters
        conn.execute(
            """
            DELETE FROM sqlite_sequence
            WHERE name IN (
                'users',
                'waste_records',
                'bin_readings',
                'rewards',
                'collection_logs',
                'notifications'
            )
            """
        )

        # Save database changes
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    # Remove old QR images safely
    try:
        for p in settings.QR_DIR.glob("*.png"):

            try:
                p.unlink()

            except OSError:
                # A locked QR image should not break database reset
                continue

    except OSError:
        pass

    # Restore demo users, bins, waste and e-waste records
    seed_demo_data()