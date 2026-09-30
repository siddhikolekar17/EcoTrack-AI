"""Page 4 - Smart bin telemetry (simulated IoT)."""
import plotly.express as px
import streamlit as st

from database import bin_repository
from modules import notifications, smart_bin
from utils import helpers, ui
from utils.constants import BIN_COLORS, CATEGORIES, STAFF_ROLES

user = ui.bootstrap("Smart Bin Monitor", "🗑️")
is_staff = user["role"] in STAFF_ROLES
st.title("🗑️ Smart Bin Monitor")
st.caption("Simulated sensor telemetry · predictive collection alerts · overflow flags.")

if is_staff:
    c1, c2, _ = st.columns([1, 1, 3])
    if c1.button("📡 Simulate sensor tick"):
        smart_bin.simulate_tick()
        st.rerun()
    if c2.button("🔔 Refresh alerts"):
        st.toast(f"{notifications.check_bins_and_alert()} new alert(s)")
notifications.check_bins_and_alert()

df = smart_bin.bins_dataframe()
if df.empty:
    st.info("No bins registered yet.")
    st.stop()

m = st.columns(4)
m[0].metric("Active bins", len(df), border=True)
m[1].metric("Need collection", int((df.fill_level >= 70).sum()), border=True)
m[2].metric("Overflow alerts", int((df.fill_level >= 90).sum()), delta_color="inverse", border=True)
m[3].metric("Avg fill", f"{df.fill_level.mean():.0f}%", border=True)

st.subheader("Campus map")
st.map(df, latitude="lat", longitude="lon", color="color", size="size")
st.caption("🟢 normal · 🟠 warning (≥70%) · 🔴 overflow (≥90%). Demo coordinates are approximate.")

st.subheader("Live bin status")
cols = st.columns(4)
for i, row in df.sort_values("bin_id").reset_index(drop=True).iterrows():
    with cols[i % 4], st.container(border=True):
        st.markdown(f"**{row.bin_id}** · {row.category}")
        st.caption(row.location)
        st.progress(min(row.fill_level, 100) / 100, text=f"{row.fill_level:.0f}% · {row.status}")
        eta = "—" if row.hours_to_full is None or row.hours_to_full != row.hours_to_full \
            else f"{row.hours_to_full:.1f} h"
        st.caption(f"Predicted full in: {eta} · Priority: **{row.priority}**")

st.subheader("🚚 Collection priority")
route = smart_bin.collection_route(df)
if route.empty:
    st.success("No collections required right now.")
else:
    view = route[["bin_id", "location", "category", "fill_level", "hours_to_full", "priority"]].copy()
    view.columns = ["Bin", "Location", "Category", "Fill %", "Hours to full", "Priority"]
    st.dataframe(view, hide_index=True)

st.subheader("📈 Fill history")
sel = st.selectbox("Bin", df.bin_id.tolist(), key="hist_bin")
readings = bin_repository.get_readings(sel, hours=48)
if readings:
    import pandas as pd
    hist = pd.DataFrame(readings)
    hist["recorded_at"] = pd.to_datetime(hist["recorded_at"])
    fig = px.line(hist, x="recorded_at", y="fill_level", markers=True, title=f"{sel} fill level (%)")
    fig.add_hline(y=70, line_dash="dot", line_color=BIN_COLORS["Warning"])
    fig.add_hline(y=90, line_dash="dot", line_color=BIN_COLORS["Overflow Alert"])
    fig.update_yaxes(range=[0, 105])
    ui.show_chart(fig)

if is_staff:
    st.subheader("🛠️ Staff controls")
    t1, t2, t3 = st.tabs(["Mark collected", "Manual sensor reading", "Register bin"])
    with t1:
        b = st.selectbox("Bin to empty", df.bin_id.tolist(), key="collect_bin")
        if st.button("✅ Mark collected"):
            smart_bin.collect(b, user["user_id"])
            notifications.check_bins_and_alert()
            st.success(f"{b} emptied and logged.")
            st.rerun()
    with t2:
        b = st.selectbox("Bin", df.bin_id.tolist(), key="manual_bin")
        val = st.slider("Fill level (%)", 0, 100, int(bin_repository.get_bin(b)["fill_level"]))
        if st.button("Save reading"):
            smart_bin.record_reading(b, float(val))
            st.rerun()
    with t3:
        with st.form("add_bin", clear_on_submit=True):
            loc = st.text_input("Location *")
            cat = st.selectbox("Waste category", CATEGORIES)
            cap = st.number_input("Capacity (litres)", 20, 1000, 120)
            lat = st.number_input("Latitude", value=16.7050, format="%.5f")
            lon = st.number_input("Longitude", value=74.2433, format="%.5f")
            if st.form_submit_button("Add bin"):
                if not loc.strip():
                    st.error("Location is required.")
                else:
                    new_id = helpers.next_bin_id([x["bin_id"] for x in bin_repository.list_bins()])
                    bin_repository.add_bin(new_id, loc.strip(), cat, int(cap), lat, lon)
                    st.success(f"Registered {new_id}.")
                    st.rerun()
