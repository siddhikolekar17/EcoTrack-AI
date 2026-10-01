
"""Page 1 - Sustainability dashboard."""

import plotly.express as px
import streamlit as st

from modules import analytics, notifications
from utils import ui
from utils.constants import CATEGORY_COLORS


# --------------------------------------------------
# Page setup
# --------------------------------------------------
user = ui.bootstrap("Dashboard", "🌱")
notifications.check_bins_and_alert()

st.title("🌱 Sustainability Dashboard")
st.caption(
    "Monitor campus waste, smart bins, e-waste, and green credits "
    "through a single dashboard."
)

# --------------------------------------------------
# Key performance indicators
# --------------------------------------------------
s = analytics.summary()
k = s["kg_by_category"]

st.subheader("📊 Campus Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Verified Waste",
        f"{s['total_kg']:.1f} kg",
        border=True,
    )

with col2:
    st.metric(
        "Bins Needing Collection",
        s["bins_need_collection"],
        f"{s['overflow_bins']} overflow",
        delta_color="inverse",
        border=True,
    )

with col3:
    st.metric(
        "E-Waste Assets Tracked",
        s["ewaste_assets"],
        border=True,
    )

with col4:
    st.metric(
        "Green Credits Awarded",
        f"{s['credits_awarded']:,}",
        border=True,
    )

# --------------------------------------------------
# Waste category breakdown
# --------------------------------------------------
st.subheader("♻️ Waste Category Breakdown")

cat1, cat2, cat3, cat4 = st.columns(4)

with cat1:
    st.metric(
        "🥬 Biodegradable",
        f"{k['Biodegradable']:.1f} kg",
        border=True,
    )

with cat2:
    st.metric(
        "♻️ Dry Recyclable",
        f"{k['Dry Recyclable']:.1f} kg",
        border=True,
    )

with cat3:
    st.metric(
        "⚠️ Hazardous / E-Waste",
        f"{k['Hazardous / E-Waste']:.1f} kg",
        border=True,
    )

with cat4:
    st.metric(
        "Pending Verification",
        s["pending"],
        border=True,
    )

# --------------------------------------------------
# Waste charts
# --------------------------------------------------
st.subheader("📈 Waste Analytics")

left, right = st.columns([2, 3], gap="large")

with left:
    st.markdown("**Waste Distribution by Category**")

    dist = analytics.category_distribution()

    if dist.empty:
        st.info(
            "No verified waste data is available yet. "
            "The distribution chart will appear when records are added."
        )
    else:
        fig = px.pie(
            dist,
            names="category",
            values="kg",
            hole=0.5,
            color="category",
            color_discrete_map=CATEGORY_COLORS,
        )

        fig.update_layout(
            legend_title_text="Waste Category",
            margin=dict(t=25, b=20, l=10, r=10),
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent",
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Waste: %{value:.1f} kg<br>"
                "Share: %{percent}<extra></extra>"
            ),
        )

        ui.show_chart(fig)

with right:
    st.markdown("**Daily Verified Waste — Last 30 Days**")

    trend = analytics.daily_trend(30)

    if trend.empty:
        st.info(
            "No trend data is available yet. "
            "Verified disposal records will appear here."
        )
    else:
        fig = px.bar(
            trend,
            x="day",
            y="kg",
            color="category",
            color_discrete_map=CATEGORY_COLORS,
            labels={
                "day": "Date",
                "kg": "Verified Waste (kg)",
                "category": "Waste Category",
            },
            barmode="stack",
        )

        fig.update_layout(
            legend_title_text="Waste Category",
            xaxis_title="Date",
            yaxis_title="Waste (kg)",
            margin=dict(t=25, b=20, l=10, r=10),
            hovermode="x unified",
        )

        ui.show_chart(fig)

# --------------------------------------------------
# Collection alerts
# --------------------------------------------------
st.subheader("🔔 Active Collection Alerts")

alerts = notifications.unread()

if not alerts:
    st.success(
        "No unread collection alerts. "
        "Check the Smart Bin Monitor for current bin status."
    )
else:
    st.caption(
        f"{len(alerts)} unread alert(s) require attention. "
        "Review the messages below."
    )

    for alert in alerts[:6]:
        show_alert = {
            "critical": st.error,
            "warning": st.warning,
        }.get(alert["level"], st.info)

        show_alert(
            f"**{alert['title']}** — {alert['message']}"
        )

    if len(alerts) > 6:
        st.caption(
            f"{len(alerts) - 6} additional alert(s) are not shown here."
        )

# --------------------------------------------------
# Recent disposal activity
# --------------------------------------------------
st.subheader("🕒 Recent Disposal Activity")

recent = analytics.recent_activity(10)

if recent.empty:
    st.info(
        "No recent disposal activity is available. "
        "New records will appear here when data is recorded."
    )
else:
    st.dataframe(
        recent,
        hide_index=True,
        use_container_width=True,
    )

# --------------------------------------------------
# Environmental impact
# --------------------------------------------------
st.divider()

st.subheader("🌍 Environmental Impact")

st.metric(
    "Estimated CO₂e Avoided",
    f"{s['impact_co2']} kg",
    border=True,
)

st.caption(
    "CO₂e avoidance is an illustrative estimate based on configured "
    "factors; it is not an independently audited figure."
)
