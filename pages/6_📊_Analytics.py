"""Page 6 - Analytics & impact."""
import plotly.express as px
import streamlit as st

from modules import analytics, smart_bin
from utils import ui
from utils.constants import BIN_COLORS, CATEGORY_COLORS

user = ui.bootstrap("Analytics", "📊")
st.title("📊 Analytics & Sustainability Impact")

s = analytics.summary()
m = st.columns(4)
m[0].metric("Verified disposals", s["verified"], border=True)
m[1].metric("Total verified waste", f"{s['total_kg']:.1f} kg", border=True)
m[2].metric("Est. CO₂e avoided", f"{s['impact_co2']} kg", border=True)
m[3].metric("Credits awarded", f"{s['credits_awarded']:,}", border=True)
st.caption("CO₂e uses illustrative per-kg factors from config/settings.py — replace with audited values.")

t1, t2, t3, t4 = st.tabs(["Waste", "E-waste lifecycle", "Smart bins", "Participation"])
with t1:
    days = st.slider("Trend window (days)", 7, 90, 30)
    a, b = st.columns(2)
    dist = analytics.category_distribution()
    if not dist.empty:
        with a:
            ui.show_chart(px.pie(dist, names="category", values="kg", hole=0.45, color="category",
                                 color_discrete_map=CATEGORY_COLORS, title="Category distribution (kg)"))
    trend = analytics.daily_trend(days)
    if not trend.empty:
        with b:
            ui.show_chart(px.area(trend, x="day", y="kg", color="category", color_discrete_map=CATEGORY_COLORS,
                                  title="Daily collection trend"))
with t2:
    es = analytics.ewaste_status()
    if es.empty:
        st.info("No e-waste assets yet.")
    else:
        ui.show_chart(px.funnel(es, x="assets", y="status", title="Assets by lifecycle stage"))
        st.dataframe(es, hide_index=True)
with t3:
    df = smart_bin.bins_dataframe()
    if not df.empty:
        fig = px.bar(df.sort_values("bin_id"), x="bin_id", y="fill_level", color="status",
                     color_discrete_map=BIN_COLORS, title="Current bin capacity (%)", hover_data=["location"])
        fig.update_yaxes(range=[0, 100])
        ui.show_chart(fig)
with t4:
    part = analytics.participation()
    if not part.empty:
        ui.show_chart(px.bar(part, x="student", y="verified_disposals", color="kg",
                             title="Verified disposals per student", color_continuous_scale="Greens"))
        st.dataframe(part, hide_index=True)

st.subheader("⬇️ Export")
st.download_button("Download all waste records (CSV)", analytics.all_waste_records().to_csv(index=False),
                   "ecotrack_waste_records.csv", "text/csv")
