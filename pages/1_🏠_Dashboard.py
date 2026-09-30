"""Page 1 - Sustainability dashboard."""
import plotly.express as px
import streamlit as st

from modules import analytics, notifications
from utils import ui
from utils.constants import CATEGORY_COLORS, STAFF_ROLES

user = ui.bootstrap("Dashboard", "🏠")
notifications.check_bins_and_alert()

st.title("🏠 Sustainability Dashboard")
st.caption("Live campus overview — verified waste, smart bins, e-waste and green credits.")

s = analytics.summary()
k = s["kg_by_category"]
r1 = st.columns(4)
r1[0].metric("Total verified waste", f"{s['total_kg']:.1f} kg", border=True)
r1[1].metric("Bins needing collection", s["bins_need_collection"], f"{s['overflow_bins']} overflow",
             delta_color="inverse", border=True)
r1[2].metric("E-waste assets tracked", s["ewaste_assets"], border=True)
r1[3].metric("Green credits awarded", f"{s['credits_awarded']:,}", border=True)
r2 = st.columns(4)
r2[0].metric("🥬 Biodegradable", f"{k['Biodegradable']:.1f} kg", border=True)
r2[1].metric("♻️ Dry recyclable", f"{k['Dry Recyclable']:.1f} kg", border=True)
r2[2].metric("⚠️ Hazardous / e-waste", f"{k['Hazardous / E-Waste']:.1f} kg", border=True)
r2[3].metric("Pending verification", s["pending"], border=True)

left, right = st.columns([2, 3], gap="large")
with left:
    dist = analytics.category_distribution()
    if dist.empty:
        st.info("No verified waste yet.")
    else:
        fig = px.pie(dist, names="category", values="kg", hole=0.5, color="category",
                     color_discrete_map=CATEGORY_COLORS, title="Waste by category (kg)")
        ui.show_chart(fig)
with right:
    trend = analytics.daily_trend(30)
    if trend.empty:
        st.info("No trend data yet.")
    else:
        fig = px.bar(trend, x="day", y="kg", color="category", color_discrete_map=CATEGORY_COLORS,
                     title="Daily verified waste – last 30 days")
        ui.show_chart(fig)

st.subheader("🔔 Active collection alerts")
alerts = notifications.unread()
if not alerts:
    st.success("All bins are within safe limits.")
for a in alerts[:6]:
    {"critical": st.error, "warning": st.warning}.get(a["level"], st.info)(f"**{a['title']}** — {a['message']}")

st.subheader("🕒 Recent disposal activity")
st.dataframe(analytics.recent_activity(10), hide_index=True)
st.caption(f"🌍 Estimated CO₂e avoided: **{s['impact_co2']} kg** (illustrative factors, not an audited figure).")
