"""Page 2 - AI waste classifier (camera / upload)."""
import streamlit as st

from config import settings
from database import waste_repository
from modules import ai_classifier, green_credits, waste_recommendation
from utils import image_processing, ui, validators
from utils.constants import CAT_HAZ, CATEGORIES, CATEGORY_ICONS

user = ui.bootstrap("AI Waste Classifier", "🤖")
st.title("🤖 AI Waste Classifier")
st.caption(f"Model backend: **{ai_classifier.backend_name()}**")

mode = st.radio("Image source", ["📁 Upload image", "📷 Use camera"], horizontal=True)
file = (st.file_uploader("Upload a waste photo", type=["jpg", "jpeg", "png", "webp"])
        if mode.startswith("📁") else st.camera_input("Take a photo of the item"))

if not file:
    st.info("Add a clear photo of a single item on a plain background for best results.")
    st.stop()

img = image_processing.load_image(file)
sig = (getattr(file, "name", "camera"), file.size)
left, right = st.columns([2, 3], gap="large")
with left:
    ui.show_image(img, "Preview")
    if image_processing.blur_score(img) < settings.BLUR_THRESHOLD:
        st.warning("Image looks blurry – results may be unreliable.")

with right:
    if st.button("🔍 Analyze waste", type="primary"):
        with st.spinner("Analyzing image…"):
            st.session_state["pred"] = (sig, ai_classifier.classify_image(img))
    stored = st.session_state.get("pred")
    if not stored or stored[0] != sig:
        st.stop()
    pred = stored[1]

    if not pred.is_ai:
        st.warning(pred.message)
    if pred.category:
        st.markdown(f"### {CATEGORY_ICONS[pred.category]} {pred.category}")
        st.progress(min(pred.confidence, 1.0), text=f"Model confidence: {pred.confidence:.0%} · detected “{pred.label}”")
    else:
        st.markdown("### ❓ Not recognised")
        st.caption(f"Closest model label: “{pred.label}”")
    if pred.is_ai and pred.message:
        (st.error if pred.category == CAT_HAZ else st.warning)(pred.message)
    if pred.top_k:
        with st.expander("Top predictions"):
            for lbl, p, cat in pred.top_k:
                st.write(f"{lbl} — {p:.1%}" + (f"  → *{cat}*" if cat else ""))

    rec = waste_recommendation.get_recommendation(pred.category)
    if rec:
        st.markdown(f"**Disposal:** {rec['bin']}")
        for step in rec["steps"]:
            st.markdown(f"- {step}")
        st.caption(rec["avoid"])
        if pred.category == CAT_HAZ:
            ui.safe_page_link("E_Waste", "♻️ Register this item in the E-Waste Tracker")

    st.divider()
    st.subheader("Save disposal record")
    with st.form("save_waste"):
        default = CATEGORIES.index(pred.category) if pred.category else 0
        category = st.selectbox("Confirm category", CATEGORIES, index=default)
        label = st.text_input("Item description", value=pred.label if pred.category else "")
        weight = st.number_input("Approx. weight (kg)", 0.01, 500.0, 0.5, 0.05)
        if category != pred.category:
            st.caption("You changed the AI category – an admin will review it.")
        if st.form_submit_button("Submit for verification", type="primary"):
            err = validators.validate_weight(weight)
            if err:
                st.error(err)
            else:
                path = image_processing.save_upload(img, user["user_id"])
                wid = waste_repository.add_record(
                    user["user_id"], category, validators.clean_text(label, 80), pred.confidence,
                    float(weight), path, pred.backend)
                st.session_state.pop("pred", None)
                st.success(f"Submission #{wid} saved. You'll earn "
                           f"{green_credits.points_for(category)} credits once an admin verifies it.")
