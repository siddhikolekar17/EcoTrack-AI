
"""EcoTrack AI - Home / login page (Streamlit entry point)."""

import streamlit as st

from config import settings
from modules import analytics
from utils import ui
from utils.constants import ROLE_LABELS


# Initialize Home page without forcing authentication
user = ui.bootstrap(
    "Home",
    "🌱",
    require_auth=False,
)


# Hero section
st.markdown(
    f"""
    <div class="hero">
        <h1>🌱 {settings.APP_NAME}</h1>
        <p>{settings.APP_TAGLINE}</p>
        <p>
            <small>
                SDG 11 · Sustainable Cities & Communities
                · Code4Impact Track 4
            </small>
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------
# LOGIN / PUBLIC HOME
# -----------------------------------------

if user is None:

    left, right = st.columns(
        [3, 2],
        gap="large",
    )

    with left:

        st.subheader("What EcoTrack AI does")

        st.markdown(
            """
            - 🤖 **AI Waste Classifier** – Photo classification into
              Biodegradable / Dry Recyclable / Hazardous-E-Waste.

            - ♻️ **E-Waste Lifecycle Auditor** – QR-tagged assets
              tracked from lab decommission to recycler handover.

            - 🗑️ **Smart Bin Telemetry** – Fill levels, predictive
              collection alerts and overflow monitoring.

            - 🌱 **Green Credits** – Verified disposal earns points,
              badges and leaderboard recognition.

            - 📊 **Analytics & Admin** – Verification queue,
              reports and campus-wide impact.
            """
        )

        with st.expander("Demo accounts (seeded sample data)"):

            st.markdown(
                """
                | Role | Email | Password |
                |---|---|---|
                | Campus Admin | admin@ecotrack.demo | admin123 |
                | Waste Manager | manager@ecotrack.demo | manager123 |
                | Student | siddhi@ecotrack.demo | student123 |
                """
            )

            st.caption(
                "Change or remove these accounts before real deployment."
            )

    with right:

        st.subheader("🔐 Login to EcoTrack AI")

        ui.login_form()


# -----------------------------------------
# AUTHENTICATED HOME
# -----------------------------------------

else:

    st.success(
        f"Welcome back, **{user['name']}** "
        f"({ROLE_LABELS[user['role']]}) 👋"
    )

    # Dashboard summary
    try:

        s = analytics.summary()

        c = st.columns(4)

        c[0].metric(
            "Verified waste",
            f"{s['total_kg']:.1f} kg",
            border=True,
        )

        c[1].metric(
            "Bins needing collection",
            s["bins_need_collection"],
            border=True,
        )

        c[2].metric(
            "E-waste assets",
            s["ewaste_assets"],
            border=True,
        )

        c[3].metric(
            "Your green credits",
            user["credits"],
            border=True,
        )

    except Exception as e:

        st.warning(
            "Your login is active, but the dashboard summary "
            "could not be loaded."
        )

        st.caption(str(e))

    # Navigation
    st.subheader("🚀 Jump to a module")

    links = [
        ("Dashboard", "🏠 Dashboard"),
        ("Classifier", "🤖 AI Waste Classifier"),
        ("E_Waste", "♻️ E-Waste Tracker"),
        ("Smart_Bin", "🗑️ Smart Bin Monitor"),
        ("Green", "🌱 Green Credits"),
        ("Analytics", "📊 Analytics"),
    ]

    if user["role"] == "admin":
        links.append(
            ("Admin", "⚙️ Admin Panel")
        )

    cols = st.columns(4)

    for i, (key, label) in enumerate(links):

        with cols[i % 4]:

            ui.safe_page_link(
                key,
                label,
            )