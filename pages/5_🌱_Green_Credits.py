"""Page 5 - Green credits, badges, leaderboard."""
import pandas as pd
import plotly.express as px
import streamlit as st

from config import settings
from database import rewards_repository, user_repository, waste_repository
from modules import green_credits
from utils import ui
from utils.constants import STAFF_ROLES

user = ui.bootstrap("Green Credits", "🌱")
st.title("🌱 Green Credits")

profile = user
if user["role"] in STAFF_ROLES:
    students = user_repository.list_users("student")
    if students:
        pick = st.selectbox("View student", students, format_func=lambda s: s["name"])
        profile = user_repository.get_user(pick["user_id"])
    else:
        st.info("No students registered yet.")
        st.stop()

level, nxt = green_credits.level_for(profile["credits"])
c = st.columns(4)
c[0].metric("Green credits", profile["credits"], border=True)
c[1].metric("Level", level, border=True)
c[2].metric("Leaderboard rank", f"#{user_repository.rank_of(profile['user_id']) or '—'}", border=True)
c[3].metric("Verified disposals", waste_repository.count_verified(profile["user_id"]), border=True)
if nxt:
    st.progress(min(profile["credits"] / nxt, 1.0), text=f"{profile['credits']} / {nxt} credits to next level")

st.subheader("🏅 Badges")
badges = green_credits.badges_for(profile["user_id"], profile["credits"])
st.write("  ".join(f"`{b}`" for b in badges) if badges else "Earn your first badge with 10 credits!")

left, right = st.columns([3, 2], gap="large")
with left:
    st.subheader("🏆 Leaderboard")
    lb = pd.DataFrame(user_repository.leaderboard(10))
    if not lb.empty:
        fig = px.bar(lb.sort_values("credits"), x="credits", y="name", orientation="h",
                     color="credits", color_continuous_scale="Greens")
        fig.update_layout(coloraxis_showscale=False, yaxis_title=None)
        ui.show_chart(fig)
with right:
    st.subheader("📜 Reward rules (demo values)")
    rules = pd.DataFrame([
        ("Biodegradable disposal (verified)", settings.CREDIT_RULES["Biodegradable"]),
        ("Dry recyclable disposal (verified)", settings.CREDIT_RULES["Dry Recyclable"]),
        ("Hazardous / e-waste disposal (verified)", settings.CREDIT_RULES["Hazardous / E-Waste"]),
        ("E-waste asset verified by admin", settings.CREDIT_RULES["ewaste_verified"]),
        ("Certified recycling completed", settings.CREDIT_RULES["recycling_completed"]),
    ], columns=["Activity", "Credits"])
    st.dataframe(rules, hide_index=True)

st.subheader("🧾 Credit history")
hist = pd.DataFrame(rewards_repository.list_rewards(profile["user_id"], 50))
if hist.empty:
    st.info("No credits yet — classify and submit some waste!")
else:
    st.dataframe(hist[["created_at", "activity", "points"]].rename(
        columns={"created_at": "Time", "activity": "Activity", "points": "Credits"}), hide_index=True)

st.subheader("My submissions")
subs = pd.DataFrame(waste_repository.list_records(user_id=profile["user_id"], limit=30))
if not subs.empty:
    st.dataframe(subs[["created_at", "category", "item_label", "weight_kg", "status"]], hide_index=True)
