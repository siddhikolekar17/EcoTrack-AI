"""Page 3 - E-waste lifecycle auditor with QR asset tags."""
import pandas as pd
import streamlit as st

from database import ewaste_repository
from modules import ewaste_manager, qr_generator
from utils import image_processing, ui, validators
from utils.constants import (EWASTE_CONDITIONS, EWASTE_LIFECYCLE, EWASTE_TYPES, STAFF_ROLES)

import itertools
_btn_ids = itertools.count()

user = ui.bootstrap("E-Waste Tracker", "♻️")
is_staff = user["role"] in STAFF_ROLES
st.title("♻️ E-Waste Lifecycle Tracker")
st.caption("Asset tagging from lab decommission to certified e-recycler, with a full audit trail.")

tabs = st.tabs(["➕ Register asset", "📋 Registry", "🔄 Lifecycle (staff)", "🔎 Scan / Lookup"])


def show_timeline(asset_id: str) -> None:
    logs = ewaste_repository.list_logs(asset_id=asset_id)
    if logs:
        df = pd.DataFrame(logs)[["created_at", "action", "performed_by_name", "destination", "notes"]]
        df.columns = ["Time", "Stage", "By", "Destination", "Notes"]
        st.dataframe(df, hide_index=True)


def show_asset(asset: dict) -> None:
    c1, c2 = st.columns([1, 2], gap="large")
    with c1:
        if asset.get("qr_path"):
            ui.show_image(asset["qr_path"], asset["asset_id"])
            with open(asset["qr_path"], "rb") as fh:
                st.download_button("⬇️ Download QR tag", fh.read(), f"{asset['asset_id']}.png", "image/png",
                                   key=f"dl_{asset['asset_id']}_{next(_btn_ids)}")
    with c2:
        st.markdown(f"**{asset['item']}** · `{asset['asset_id']}`")
        st.write(f"{asset['item_type']} · {asset['quantity']} unit(s) · {asset['department']}")
        st.write(f"Condition: {asset['item_condition']} · Registered by {asset.get('registered_by_name') or '—'}")
        if asset.get("recycler_name"):
            st.write(f"Recycler: **{asset['recycler_name']}** → {asset.get('destination')}")
        if asset.get("certificate_no"):
            st.success(f"Certificate: {asset['certificate_no']}")
        ui.lifecycle_tracker(asset["status"])
    show_timeline(asset["asset_id"])


with tabs[0]:
    with st.form("register_asset", clear_on_submit=True):
        c1, c2 = st.columns(2)
        item = c1.text_input("Item name *", placeholder="e.g. Dell Latitude E6440")
        item_type = c2.selectbox("Item type", EWASTE_TYPES)
        dept = c1.text_input("Department / laboratory *", placeholder="e.g. Computer Science Lab")
        cond = c2.selectbox("Condition", EWASTE_CONDITIONS)
        qty = c1.number_input("Quantity", 1, 1000, 1)
        notes = st.text_area("Notes (serial no., hazards, etc.)", max_chars=300)
        if st.form_submit_button("Register & generate QR", type="primary"):
            err = None if item.strip() and dept.strip() else "Item name and department are required."
            err = err or validators.validate_quantity(qty)
            if err:
                st.error(err)
            else:
                asset = ewaste_manager.register_asset(
                    user["user_id"], validators.clean_text(item, 80), item_type,
                    validators.clean_text(dept, 80), cond, int(qty), validators.clean_text(notes, 300))
                st.session_state["last_asset"] = asset["asset_id"]
    last = st.session_state.get("last_asset")
    if last and ewaste_repository.get_asset(last):
        st.success("Asset registered. Print the QR tag and attach it to the item.")
        show_asset(ewaste_repository.get_asset(last))

with tabs[1]:
    status_filter = st.selectbox("Filter by stage", ["All"] + EWASTE_LIFECYCLE)
    assets = ewaste_repository.list_assets(
        status=None if status_filter == "All" else status_filter,
        user_id=None if is_staff else user["user_id"])
    if not assets:
        st.info("No assets found.")
    else:
        df = pd.DataFrame(assets)[["asset_id", "item", "item_type", "department", "quantity", "status",
                                   "registered_by_name", "created_at"]]
        st.dataframe(df, hide_index=True)
        pick = st.selectbox("Open asset", [a["asset_id"] for a in assets],
                            format_func=lambda i: f"{i} — {next(a['item'] for a in assets if a['asset_id'] == i)}")
        show_asset(ewaste_repository.get_asset(pick))

with tabs[2]:
    if not is_staff:
        st.info("🔒 Only waste managers and admins can advance lifecycle stages.")
    else:
        open_assets = [a for a in ewaste_repository.list_assets() if a["status"] != EWASTE_LIFECYCLE[-1]]
        if not open_assets:
            st.success("All assets have completed recycling. 🎉")
        else:
            aid = st.selectbox("Asset to update", [a["asset_id"] for a in open_assets],
                               format_func=lambda i: f"{i} — {next(a['item'] for a in open_assets if a['asset_id'] == i)}")
            asset = ewaste_repository.get_asset(aid)
            nxt = ewaste_manager.next_stage(asset["status"])
            ui.lifecycle_tracker(asset["status"])
            st.markdown(f"**Next stage → {nxt}**")
            with st.form("advance"):
                recycler = destination = certificate = ""
                if nxt == "Recycler Handover":
                    recycler = st.text_input("Certified recycler name *")
                    destination = st.text_input("Destination facility *")
                if nxt == "Recycling Completed":
                    certificate = st.text_input("Recycling certificate number *")
                notes = st.text_input("Notes (optional)")
                if st.form_submit_button(f"Advance to “{nxt}”", type="primary"):
                    try:
                        ewaste_manager.advance(aid, user["user_id"], recycler, destination, certificate, notes)
                        st.success(f"{aid} moved to {nxt}.")
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))

with tabs[3]:
    st.write("Scan an asset's QR code with the camera, or type the asset ID.")
    shot = st.camera_input("Scan QR", key="qr_scan")
    code = st.text_input("…or enter asset ID")
    text = None
    if shot:
        text = qr_generator.decode_qr(image_processing.load_image(shot))
        if not text:
            st.warning("No QR code detected – try again with better lighting.")
    text = text or code
    if text:
        found = ewaste_repository.get_asset(qr_generator.extract_asset_id(text) or "")
        if found:
            if not is_staff and found["registered_by"] != user["user_id"]:
                st.info(f"Asset {found['asset_id']} is at stage **{found['status']}**.")
            else:
                show_asset(found)
        else:
            st.error("Asset not found.")
