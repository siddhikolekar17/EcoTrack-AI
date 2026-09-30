# 🌱 EcoTrack AI

**Intelligent Waste Segregation & E-Waste Lifecycle Management** · UN SDG 11 · Code4Impact Track 4

AI waste classification · QR-based e-waste audit trail · smart-bin telemetry with predictive alerts · verified green credits.

## 🚀 Live Demo

### Streamlit Application

[🌱 Open EcoTrack AI Live Demo](https://siddhikolekar17-ecotrack-ai-app-xostlu.streamlit.app/)

## 💻 Source Code

### GitHub Repository

[📂 EcoTrack-AI Source Code](https://github.com/siddhikolekar17/EcoTrack-AI)

## Features

| Module | What it does |
|---|---|
| 🤖 AI Waste Classifier | Upload/camera photo → Biodegradable / Dry Recyclable / Hazardous-E-Waste, confidence, disposal guide, quality (blur) check |
| ♻️ E-Waste Tracker | Register assets, auto QR tag, 6-stage lifecycle to certified recycler, QR scan lookup, full audit log |
| 🗑️ Smart Bin Monitor | Simulated IoT readings, map, hours-to-full prediction, priority route, overflow alerts |
| 🌱 Green Credits | Ledger-based points, levels, badges, leaderboard |
| 📊 Analytics | Category mix, trends, lifecycle funnel, bin capacity, participation, CSV export |
| ⚙️ Admin Panel | Verification queue, users, logs, alerts, reset/export |

## Quick Start

```bash
python -m venv .venv && .venv\Scripts\activate     # Windows
# Linux/macOS: source .venv/bin/activate

pip install -r requirements.txt

streamlit run app.py