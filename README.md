# 🌱 EcoTrack AI
**Intelligent Waste Segregation & E-Waste Lifecycle Management** · UN SDG 11 · Code4Impact Track 4

AI waste classification · QR-based e-waste audit trail · smart-bin telemetry with predictive alerts · verified green credits.

## Features
| Module | What it does |
|---|---|
| 🤖 AI Waste Classifier | Upload/camera photo → Biodegradable / Dry Recyclable / Hazardous-E-Waste, confidence, disposal guide, quality (blur) check |
| ♻️ E-Waste Tracker | Register assets, auto QR tag, 6-stage lifecycle to certified recycler, QR scan lookup, full audit log |
| 🗑️ Smart Bin Monitor | Simulated IoT readings, map, hours-to-full prediction, priority route, overflow alerts |
| 🌱 Green Credits | Ledger-based points, levels, badges, leaderboard |
| 📊 Analytics | Category mix, trends, lifecycle funnel, bin capacity, participation, CSV export |
| ⚙️ Admin Panel | Verification queue, users, logs, alerts, reset/export |

## Quick start
```bash
python -m venv .venv && .venv\Scripts\activate      # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```
First run creates `data/ecotrack.db` and seeds demo data. Python 3.10–3.12 is recommended for TensorFlow.
Run without TensorFlow (`pip install` everything except the last line): the app still works, but the classifier falls back to a colour heuristic that is **clearly labelled as not AI**.

### Demo accounts
| Role | Email | Password |
|---|---|---|
| Admin | admin@ecotrack.demo | admin123 |
| Waste Manager | manager@ecotrack.demo | manager123 |
| Student | siddhi@ecotrack.demo | student123 |

### Suggested demo flow (3 min)
1. Student: classify a photo → submit. 2. Student: register an e-waste asset → download QR.
3. Admin: verify the submission (credits awarded) → advance the asset through the lifecycle.
4. Manager: simulate sensor ticks → watch predictions/alerts → mark a bin collected. 5. Show Analytics.

## Tests
```bash
pytest -q
```

## Improving the AI
Default model = pretrained MobileNetV2 with label mapping (limited on real waste). For better accuracy train on your own photos:
`python models/waste_classifier/train_classifier.py --data dataset` – see `models/waste_classifier/model_info.md`.

## Deploy (Streamlit Community Cloud)
Push to GitHub → share.streamlit.io → select repo, main file `app.py`. Note: the SQLite file resets on redeploy; use a hosted DB (Supabase/PostgreSQL) for persistence.

## Limitations / honesty notes
- Bin sensor data is **simulated**; the `smart_bin.record_reading()` function is the integration point for real IoT (MQTT/HTTP).
- Credit values and CO₂e factors are demo values, not official figures.
- Auth is suitable for a demo (hashed passwords + roles) – add HTTPS, rate limiting and SSO for production.

## Project structure
See `docs/architecture.md` and `docs/database_schema.md`.

## Contributing
Fork → branch → `pytest` → pull request. MIT licensed (see `LICENSE`).
