"""Page 7 - Admin panel (admin role only)."""
import os

import pandas as pd
import streamlit as st

from config import settings
from database import bin_repository, db_setup, ewaste_repository, user_repository, waste_repository
from modules import green_credits, notifications
from utils import ui, validators
from utils.constants import ROLES, ROLE_ADMIN, WASTE_PENDING

user = ui.bootstrap("Admin Panel", "⚙️", roles=[ROLE_ADMIN])
st.title("⚙️ Admin Panel")

tabs = st.tabs(["✅ Verify submissions", "👥 Users", "🗑️ Bins", "♻️ E-waste review", "📜 Logs", "🔔 Alerts", "🧰 System"])

with tabs[0]:
    pending = waste_repository.list_records(status=WASTE_PENDING, limit=30)
    st.write(f"**{len(pending)}** submission(s) awaiting review.")
    for rec in pending:
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 3, 2])
            if rec["image_path"] and os.path.exists(rec["image_path"]):
                c1.image(rec["image_path"], width=120)
            conf = f"{rec['confidence']:.0%}" if rec["confidence"] is not None else "n/a"
            c2.markdown(f"**#{rec['waste_id']} · {rec['category']}** — {rec['item_label'] or 'item'}")
            c2.caption(f"{rec['student']} · {rec['weight_kg']} kg · confidence {conf} · "
                       f"model: {rec['model_name']} · {rec['created_at']}")
            note = c3.text_input("Review note", key=f"n{rec['waste_id']}")
            b1, b2 = c3.columns(2)
            if b1.button("✅ Approve", key=f"a{rec['waste_id']}"):
                pts = green_credits.verify_submission(rec["waste_id"], user["user_id"], True, note)
                st.toast(f"Approved · {pts} credits awarded")
                st.rerun()
            if b2.button("❌ Reject", key=f"r{rec['waste_id']}"):
                green_credits.verify_submission(rec["waste_id"], user["user_id"], False, note)
                st.rerun()

with tabs[1]:
    st.dataframe(pd.DataFrame(user_repository.list_users()), hide_index=True)
    with st.form("new_user", clear_on_submit=True):
        st.markdown("**Create account**")
        c1, c2, c3, c4 = st.columns(4)
        name, email = c1.text_input("Name"), c2.text_input("Email")
        pw, role = c3.text_input("Password", type="password"), c4.selectbox("Role", ROLES)
        if st.form_submit_button("Create"):
            err = validators.validate_name(name) or validators.validate_email(email) or validators.validate_password(pw)
            if err:
                st.error(err)
            else:
                try:
                    user_repository.create_user(name, email, pw, role)
                    st.success("User created.")
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))

with tabs[2]:
    st.dataframe(pd.DataFrame(bin_repository.list_bins()), hide_index=True)
    st.caption("Register or empty bins from the Smart Bin Monitor page.")

with tabs[3]:
    assets = ewaste_repository.list_assets()
    if assets:
        st.dataframe(pd.DataFrame(assets)[["asset_id", "item", "department", "quantity", "status",
                                           "recycler_name", "certificate_no", "registered_by_name"]],
                     hide_index=True)
    ui.safe_page_link("E_Waste", "Open the lifecycle tab to advance assets →")

with tabs[4]:
    logs = ewaste_repository.list_logs(limit=300)
    if logs:
        st.dataframe(pd.DataFrame(logs)[["created_at", "asset_id", "bin_id", "action", "destination",
                                         "performed_by_name", "notes"]], hide_index=True)
    else:
        st.info("No collection logs yet.")

with tabs[5]:
    if st.button("Mark all as read"):
        notifications.mark_all_read()
        st.rerun()
    alerts = notifications.list_all(100)
    if alerts:
        st.dataframe(pd.DataFrame(alerts)[["created_at", "level", "title", "message", "is_read"]], hide_index=True)

with tabs[6]:
    if settings.DB_PATH.exists():
        st.download_button("⬇️ Download SQLite database", settings.DB_PATH.read_bytes(), "ecotrack.db")
    st.warning("Resetting deletes ALL data and restores the demo dataset.")
    if st.checkbox("I understand") and st.button("♻️ Reset demo data", type="primary"):
        db_setup.reset_demo()
        st.session_state.pop("user_id", None)
        st.rerun()
