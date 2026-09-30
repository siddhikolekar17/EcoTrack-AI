# 🌱 EcoTrack AI

**Intelligent Waste Segregation & E-Waste Lifecycle Management** · UN SDG 11 · Code4Impact Track 4

AI waste classification · QR-based e-waste audit trail · smart-bin telemetry with predictive alerts · verified green credits.

---

## 🚀 Live Demo

### Streamlit Application

[🌱 Open EcoTrack AI Live Demo](https://siddhikolekar17-ecotrack-ai-app-xostlu.streamlit.app/)

---

## 💻 Source Code

### GitHub Repository

[📂 EcoTrack-AI Source Code](https://github.com/siddhikolekar17/EcoTrack-AI)

---

## 📌 Problem Statement

### Track 4 — Sustainable Cities & Communities (SDG 11)
**Campus & City Waste Segregation & E-Waste Tracker**

Improper waste segregation at source reduces recycling efficiency, while hazardous electronic waste such as discarded electronics, batteries, PCBs, and peripherals often lacks a reliable lifecycle tracking mechanism.

**EcoTrack AI** addresses this challenge through an intelligent campus waste-management platform that combines AI-based waste classification, institutional e-waste lifecycle tracking, smart-bin monitoring, community incentives, and analytics.

---

## 🎯 Objectives

- Improve waste segregation at source using AI-assisted classification.
- Track e-waste from registration through collection and recycling.
- Monitor campus smart-bin capacity and generate predictive alerts.
- Encourage sustainable participation through Green Credits.
- Provide administrators with centralized verification, monitoring, and analytics.

---

## ✨ Features

| Module | What it does |
|---|---|
| 🤖 AI Waste Classifier | Upload/camera photo → Biodegradable / Dry Recyclable / Hazardous-E-Waste, confidence, disposal guide, and image-quality check |
| ♻️ E-Waste Tracker | Register assets, automatically generate QR tags, track the 6-stage lifecycle, scan QR codes, and maintain an audit log |
| 🗑️ Smart Bin Monitor | Simulated IoT readings, bin status, hours-to-full prediction, priority route, and overflow alerts |
| 🌱 Green Credits | Ledger-based points, levels, badges, and leaderboard |
| 📊 Analytics | Category mix, trends, lifecycle funnel, bin capacity, participation, and CSV export |
| ⚙️ Admin Panel | Verification queue, user management, logs, alerts, reset, and export |

---

## 🏗️ Architecture

EcoTrack AI follows a modular architecture:

```text
                        ┌─────────────────────┐
                        │      Streamlit      │
                        │     User Interface  │
                        └──────────┬──────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
          ▼                        ▼                        ▼
 ┌────────────────┐      ┌──────────────────┐      ┌─────────────────┐
 │ AI Classifier  │      │ E-Waste Manager  │      │ Smart Bin       │
 │ & Image        │      │ & QR Lifecycle   │      │ Monitoring      │
 │ Processing     │      │ Tracking         │      │ & Prediction    │
 └───────┬────────┘      └─────────┬────────┘      └────────┬────────┘
         │                         │                        │
         └─────────────────────────┼────────────────────────┘
                                   │
                                   ▼
                         ┌──────────────────┐
                         │ Business Modules │
                         │ Analytics        │
                         │ Green Credits    │
                         │ Notifications    │
                         │ Recommendations  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Repository Layer │
                         │ Database Access  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │      SQLite      │
                         │  EcoTrack Data   │
                         └──────────────────┘
```

For detailed documentation:

- [📐 Architecture Documentation](docs/architecture.md)
- [🗄️ Database Schema](docs/database_schema.md)

---

## 🛠️ Technology Stack

### Frontend / UI

- Streamlit

### AI / Computer Vision

- TensorFlow
- Keras
- OpenCV
- Pillow
- MobileNetV2

### Data & Analytics

- Python
- Pandas
- NumPy
- Plotly

### Database

- SQLite

### Utilities

- QR Code generation
- Image processing
- Role-based authentication
- Automated testing with Pytest

---

## 👥 Team Members & Contributions

| Team Member | Role | Contribution |
|---|---|---|
| **Siddhi Kolekar** | Team Lead & Full-Stack Integration | Project coordination, Streamlit application integration, main application flow, GitHub repository setup, feature integration, deployment, and final testing |
| **Asiya Panhalkar** | AI/ML & Waste Classification | AI waste classification module, image-processing workflow, model integration, classification confidence, and disposal guidance |
| **Vaishnavi Talikoti** | Backend & Database Developer | SQLite database design, database setup, repository modules, e-waste records, user data, waste records, rewards, and data persistence logic |
| **Sanika Chougule** | UI/UX, Analytics & Testing | Streamlit page design, dashboard and analytics presentation, interface improvements, validation, test cases, documentation, and demo preparation |

---

## 📁 Project Structure

```text
EcoTrack-AI/
│
├── .streamlit/
│   └── config.toml
│
├── assets/
│   ├── background.png
│   ├── logo.png
│   └── icons/
│
├── config/
│   ├── __init__.py
│   └── settings.py
│
├── data/
│   ├── sample_bins.json
│   └── sample_waste_data.csv
│
├── database/
│   ├── __init__.py
│   ├── bin_repository.py
│   ├── db_connection.py
│   ├── db_setup.py
│   ├── ewaste_repository.py
│   ├── rewards_repository.py
│   ├── user_repository.py
│   └── waste_repository.py
│
├── docs/
│   ├── architecture.md
│   ├── database_schema.md
│   └── screenshots/
│
├── generated/
│   ├── qr_codes/
│   └── uploads/
│
├── models/
│   ├── README.md
│   └── waste_classifier/
│       ├── model_info.md
│       └── train_classifier.py
│
├── modules/
│   ├── __init__.py
│   ├── ai_classifier.py
│   ├── analytics.py
│   ├── ewaste_manager.py
│   ├── green_credits.py
│   ├── notifications.py
│   ├── qr_generator.py
│   ├── smart_bin.py
│   └── waste_recommendation.py
│
├── pages/
│   ├── 1_🏠_Dashboard.py
│   ├── 2_🤖_AI_Waste_Classifier.py
│   ├── 3_♻️_E_Waste_Tracker.py
│   ├── 4_🗑️_Smart_Bin_Monitor.py
│   ├── 5_🌱_Green_Credits.py
│   ├── 6_📊_Analytics.py
│   └── 7_⚙️_Admin_Panel.py
│
├── tests/
│   ├── conftest.py
│   ├── test_classifier.py
│   ├── test_database.py
│   ├── test_ewaste.py
│   └── test_rewards.py
│
├── utils/
│   ├── __init__.py
│   ├── constants.py
│   ├── helpers.py
│   ├── image_processing.py
│   ├── ui.py
│   └── validators.py
│
├── .gitignore
├── LICENSE
├── app.py
├── pytest.ini
├── README.md
└── requirements.txt
```

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/siddhikolekar17/EcoTrack-AI.git
cd EcoTrack-AI
```

### 2. Create a virtual environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app.py
```

The application creates `data/ecotrack.db` on first run and seeds demo data.

Python **3.10–3.12** is recommended for TensorFlow.

---

## 🔐 Demo Accounts

These credentials are for **demo/testing purposes only**.

| Role | Email | Password |
|---|---|---|
| Admin | `admin@ecotrack.demo` | `admin123` |
| Waste Manager | `manager@ecotrack.demo` | `manager123` |
| Student | `siddhi@ecotrack.demo` | `student123` |

---

## 🎬 Suggested Demo Flow

### Student Workflow

1. Log in as Student.
2. Open **AI Waste Classifier**.
3. Upload or capture a waste image.
4. View classification, confidence, and disposal guidance.
5. Submit the waste record.
6. Register an e-waste asset.
7. Generate and download its QR code.

### Admin Workflow

8. Log in as Admin.
9. Open the verification queue.
10. Verify the submitted waste record.
11. Award Green Credits.
12. Advance an e-waste asset through its lifecycle.
13. Review logs and alerts.

### Waste Manager Workflow

14. Log in as Waste Manager.
15. Open **Smart Bin Monitor**.
16. Simulate sensor readings.
17. Observe capacity prediction and overflow alerts.
18. Mark the bin as collected.

### Analytics

19. Open **Analytics**.
20. Review waste categories, trends, lifecycle funnel, participation, and bin statistics.

---

## 🤖 AI Waste Classification

The default classifier uses a pretrained **MobileNetV2-based model** with a project-specific label mapping.

The classifier supports:

- Biodegradable
- Dry Recyclable
- Hazardous / E-Waste
- Confidence reporting
- Disposal guidance
- Image-quality checking

### Important AI Note

The default pretrained model is limited for real-world waste classification.

For higher accuracy, train the model with a dedicated waste-image dataset:

```bash
python models/waste_classifier/train_classifier.py --data dataset
```

See:

`models/waste_classifier/model_info.md`

for more information.

---

## ♻️ E-Waste Lifecycle

EcoTrack AI provides an end-to-end e-waste tracking workflow using QR-based asset identification.

```text
Asset Registration
       ↓
QR Tag Generation
       ↓
Collection
       ↓
Verification
       ↓
Recycling / Processing
       ↓
Certified Recycler
```

The system maintains lifecycle information and an audit trail for each registered asset.

---

## 🗑️ Smart Bin Monitoring

The Smart Bin module supports:

- Bin capacity monitoring
- Simulated sensor readings
- Hours-to-full prediction
- Overflow detection
- Priority collection routing
- Collection status updates

The project currently uses **simulated sensor data** for the prototype.

The integration point for real IoT devices is:

```text
smart_bin.record_reading()
```

This can later be connected to MQTT, HTTP, or real sensor infrastructure.

---

## 🌱 Green Credits

The Green Credits system encourages sustainable participation through:

- Activity-based points
- Reward ledger
- Levels
- Badges
- Leaderboard
- Verified disposal/recycling contributions

Credit values used in the prototype are demo values.

---

## 📊 Analytics

The Analytics module provides:

- Waste category distribution
- Waste trends
- E-waste lifecycle funnel
- Smart-bin capacity information
- Participation statistics
- CSV export
- Dashboard visualizations

---

## 🧪 Testing

Run all tests using:

```bash
pytest -q
```

Current local test result:

```text
14 passed
```

The test suite covers core areas including:

- AI classifier behavior
- Database operations
- E-waste workflows
- Reward / Green Credits functionality

---

## ☁️ Deploy on Streamlit Community Cloud

### GitHub Repository

```text
https://github.com/siddhikolekar17/EcoTrack-AI
```

### Deployment Configuration

```text
Repository: siddhikolekar17/EcoTrack-AI
Branch: main
Main file: app.py
Python: 3.12
```

### Live Application

[🌱 Open EcoTrack AI](https://siddhikolekar17-ecotrack-ai-app-xostlu.streamlit.app/)

### Important Note

The prototype currently uses SQLite.

The SQLite database can reset when the Streamlit Cloud environment is rebuilt or redeployed.

For production deployment, a hosted database such as PostgreSQL or Supabase can be used for persistent storage.

---

## 🔒 Security & Privacy Notes

- Local database files are excluded from Git.
- Streamlit secrets should be stored using Streamlit's secrets management instead of committing credentials.
- `.env` files are excluded from version control.
- Demo credentials are intended only for prototype demonstration.
- Production deployments should add stronger authentication, rate limiting, HTTPS, and enterprise identity management.

---

## ⚠️ Limitations / Honesty Notes

- Smart-bin sensor data is currently **simulated**.
- AI classification accuracy depends on the underlying model and dataset.
- Credit values and CO₂e factors are **demo values**, not official environmental accounting figures.
- SQLite is suitable for the prototype but should be replaced with a hosted database for persistent production use.
- Authentication is designed for the hackathon prototype and should be strengthened for production deployment.

---

## 🌍 SDG Alignment

EcoTrack AI is designed for:

### UN Sustainable Development Goal 11

**Sustainable Cities and Communities**

The project supports sustainable waste-management practices through:

- Better segregation at source
- E-waste lifecycle visibility
- Smart waste collection monitoring
- Community participation
- Data-driven waste analytics

---

## 🔬 Future Scope

Potential future improvements include:

- Real IoT smart-bin hardware integration
- Higher-accuracy waste classification models
- Real-time municipal/recycler integration
- Cloud database persistence
- Mobile application support
- Advanced predictive analytics
- Automated collection-route optimization
- QR-based certified recycler verification
- Expanded campus-to-city deployment

---

## 🤝 Contributing

Contributions are welcome.

Basic workflow:

```text
Fork → Create branch → Make changes → Run tests → Commit → Pull Request
```

Before submitting changes:

```bash
pytest -q
```

Please keep contributions focused, documented, and consistent with the project's existing architecture.

---

## 📄 License

This project is licensed under the **MIT License**.

See the [LICENSE](LICENSE) file for details.

---

## 📚 Documentation

Additional project documentation:

- [Architecture](docs/architecture.md)
- [Database Schema](docs/database_schema.md)
- [Model Information](models/waste_classifier/model_info.md)

---

## 🌱 EcoTrack AI

**Intelligent Waste Segregation & E-Waste Lifecycle Management**

Built for **Code4Impact Track 4 · UN SDG 11 · Sustainable Cities & Communities**

### 🔗 Project Links

- **Live Demo:** https://siddhikolekar17-ecotrack-ai-app-xostlu.streamlit.app/
- **GitHub:** https://github.com/siddhikolekar17/EcoTrack-AI