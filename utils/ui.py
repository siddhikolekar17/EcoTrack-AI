
"""Streamlit UI helpers: page bootstrap, auth, sidebar, shared widgets."""

from __future__ import annotations

import glob
import os

import streamlit as st

from config import settings
from database import db_setup, user_repository
from modules import notifications
from utils import validators
from utils.constants import (
    EWASTE_LIFECYCLE,
    ROLE_LABELS,
    ROLE_ADMIN,
    STAFF_ROLES,
)


CSS = """
<style>
.hero {
    padding: 1.6rem 1.8rem;
    border-radius: 18px;
    color: #fff;
    margin-bottom: 1rem;
    background: linear-gradient(
        135deg,
        #0f766e 0%,
        #16a34a 60%,
        #65a30d 100%
    );
}
.hero h1 {
    margin: 0;
    font-size: 2.2rem;
    color: #fff;
}
.hero p {
    margin: .3rem 0 0;
    opacity: .95;
}
.pill {
    display: inline-block;
    padding: .15rem .75rem;
    border-radius: 999px;
    font-size: .8rem;
    font-weight: 600;
    color: #fff;
}
</style>
"""


@st.cache_resource(show_spinner="Preparing database…")
def _init_once() -> bool:
    db_setup.ensure_ready()
    return True


def current_user():
    """Return the currently authenticated user."""

    uid = st.session_state.get("user_id")

    if uid is None:
        return None

    try:
        user = user_repository.get_user(int(uid))

        if user is None:
            st.session_state.pop("user_id", None)

        return user

    except (TypeError, ValueError):
        st.session_state.pop("user_id", None)
        return None


def _logout():
    """Clear the current login session."""

    st.session_state.pop("user_id", None)
    st.session_state.pop("pred", None)
    st.session_state.pop("last_asset", None)


def sidebar(user) -> None:
    """Render shared sidebar with role-based navigation."""

    with st.sidebar:

        st.markdown("### 🌱 EcoTrack AI")

        if user:

            st.markdown(f"**{user['name']}**")

            st.caption(
                f"{ROLE_LABELS[user['role']]} · "
                f"🌱 {user['credits']} credits"
            )

            # Show alerts to staff users.
            if user["role"] in STAFF_ROLES:

                n = len(notifications.unread())

                if n:
                    st.warning(f"🔔 {n} active alert(s)")

            st.divider()

            st.markdown("### Navigation")

            # Common navigation available to logged-in users.
            links = [
                ("Dashboard", "🏠 Dashboard"),
                ("AI_Waste", "🤖 AI Waste Classifier"),
                ("E_Waste", "♻️ E-Waste Tracker"),
                ("Smart_Bin", "🗑️ Smart Bin Monitor"),
                ("Green", "🌱 Green Credits"),
                ("Analytics", "📊 Analytics"),
            ]

            for key, label in links:
                safe_page_link(key, label)

            # Admin Panel is visible only to Campus Admin.
            if user["role"] == ROLE_ADMIN:

                st.divider()

                safe_page_link(
                    "Admin_Panel",
                    "⚙️ Admin Panel",
                )

            st.divider()

            st.button(
                "Log out",
                on_click=_logout,
                key="shared_logout",
                use_container_width=True,
            )

        else:

            st.info("Log in to access EcoTrack AI modules.")


def bootstrap(
    title: str,
    icon: str,
    roles=None,
    require_auth: bool = True,
):
    """
    Initialize page, database, session authentication and role access.

    If authentication is missing, show a login form instead of leaving
    the user stuck on a warning page.
    """

    st.set_page_config(
        page_title=f"{title} · {settings.APP_NAME}",
        page_icon=icon,
        layout="wide",
    )

    _init_once()

    st.markdown(CSS, unsafe_allow_html=True)

    user = current_user()

    sidebar(user)

    if require_auth and user is None:

        st.warning(
            "Your login session is not active. "
            "Please sign in to continue."
        )

        st.title("🔐 EcoTrack AI Login")

        login_form()

        st.stop()

    # Enforce role-based access to protected pages.
    if roles and user and user["role"] not in roles:

        st.error(
            "🔒 You do not have permission to view this page."
        )

        st.stop()

    return user


def login_form() -> None:
    """Display login and student registration forms."""

    tab_in, tab_up = st.tabs(
        ["🔑 Log in", "🆕 Register (student)"]
    )

    with tab_in:

        with st.form("login"):

            email = st.text_input(
                "Email",
                key="login_email",
            )

            pw = st.text_input(
                "Password",
                type="password",
                key="login_password",
            )

            submitted = st.form_submit_button(
                "Log in",
                type="primary",
            )

            if submitted:

                u = user_repository.authenticate(email, pw)

                if u:

                    st.session_state["user_id"] = int(
                        u["user_id"]
                    )

                    st.success(
                        f"Welcome, {u['name']}! Login successful."
                    )

                    st.rerun()

                else:

                    st.error("Invalid email or password.")

    with tab_up:

        with st.form("register"):

            name = st.text_input("Full name")

            email = st.text_input(
                "Email",
                key="reg_email",
            )

            pw = st.text_input(
                "Password (min 6 chars)",
                type="password",
                key="reg_pw",
            )

            if st.form_submit_button("Create account"):

                err = (
                    validators.validate_name(name)
                    or validators.validate_email(email)
                    or validators.validate_password(pw)
                )

                if err:

                    st.error(err)

                else:

                    try:

                        uid = user_repository.create_user(
                            name,
                            email,
                            pw,
                        )

                        st.session_state["user_id"] = int(uid)

                        st.success(
                            "Account created successfully!"
                        )

                        st.rerun()

                    except ValueError as exc:

                        st.error(str(exc))


def page_path(key: str) -> str | None:
    """Find a page file by keyword, including emoji filenames."""

    for p in sorted(
        glob.glob(
            str(settings.BASE_DIR / "pages" / "*.py")
        )
    ):

        if key.lower() in os.path.basename(p).lower():

            return os.path.relpath(
                p,
                settings.BASE_DIR,
            ).replace(os.sep, "/")

    return None


def safe_page_link(key: str, label: str) -> None:
    """Create a safe Streamlit page link."""

    path = page_path(key)

    if not path:
        return

    try:

        st.page_link(
            path,
            label=label,
        )

    except Exception:

        st.caption(f"Open **{label}** from the sidebar.")


def show_image(src, caption=None) -> None:
    """Display an image with compatibility fallback."""

    try:

        st.image(
            src,
            caption=caption,
            width="stretch",
        )

    except Exception:

        st.image(
            src,
            caption=caption,
            use_container_width=True,
        )


def show_chart(fig, key=None) -> None:
    """Display Plotly chart."""

    fig.update_layout(
        margin=dict(l=10, r=10, t=40, b=10)
    )

    try:

        st.plotly_chart(
            fig,
            width="stretch",
            key=key,
        )

    except Exception:

        st.plotly_chart(
            fig,
            use_container_width=True,
            key=key,
        )


def pill(text: str, color: str) -> str:

    return (
        f'<span class="pill" '
        f'style="background:{color}">{text}</span>'
    )


def lifecycle_tracker(status: str) -> None:
    """Display the six-stage e-waste lifecycle."""

    idx = EWASTE_LIFECYCLE.index(status)

    st.progress(
        (idx + 1) / len(EWASTE_LIFECYCLE),
        text=(
            f"Stage {idx + 1} of "
            f"{len(EWASTE_LIFECYCLE)}: {status}"
        ),
    )

    cols = st.columns(len(EWASTE_LIFECYCLE))

    for i, (col, stage) in enumerate(
        zip(cols, EWASTE_LIFECYCLE)
    ):

        icon = "✅" if i <= idx else "⬜"

        col.markdown(
            f"{icon}<br><small>{stage}</small>",
            unsafe_allow_html=True,
        )