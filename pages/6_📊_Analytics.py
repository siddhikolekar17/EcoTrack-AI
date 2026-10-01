
"""Page 6 - Analytics & Sustainability Impact."""

import plotly.express as px
import streamlit as st

from modules import analytics, smart_bin
from utils import ui
from utils.constants import BIN_COLORS, CATEGORY_COLORS


# --------------------------------------------------
# Page setup
# --------------------------------------------------
user = ui.bootstrap("Analytics", "📊")

st.title("📊 Analytics & Sustainability Impact")
st.caption(
    "Explore waste trends, e-waste lifecycle, smart-bin capacity, "
    "and student participation."
)


# --------------------------------------------------
# Key performance indicators
# --------------------------------------------------
s = analytics.summary()

st.subheader("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Verified Disposals",
        s["verified"],
        border=True,
    )

with col2:
    st.metric(
        "Total Verified Waste",
        f"{s['total_kg']:.1f} kg",
        border=True,
    )

with col3:
    st.metric(
        "Estimated CO₂e Avoided",
        f"{s['impact_co2']} kg",
        border=True,
    )

with col4:
    st.metric(
        "Credits Awarded",
        f"{s['credits_awarded']:,}",
        border=True,
    )

st.caption(
    "CO₂e avoidance uses illustrative per-kilogram factors from "
    "config/settings.py. These are estimates, not audited measurements."
)

st.divider()


# --------------------------------------------------
# Analytics tabs
# --------------------------------------------------
tab_waste, tab_ewaste, tab_bins, tab_participation = st.tabs(
    [
        "♻️ Waste Analytics",
        "🔋 E-Waste Lifecycle",
        "🗑️ Smart Bins",
        "👥 Participation",
    ]
)


# --------------------------------------------------
# Tab 1: Waste analytics
# --------------------------------------------------
with tab_waste:
    st.subheader("Waste Trends and Distribution")

    days = st.slider(
        "Select trend period (days)",
        min_value=7,
        max_value=90,
        value=30,
        help="Choose the number of days shown in the waste trend chart.",
    )

    dist = analytics.category_distribution()
    trend = analytics.daily_trend(days)

    chart_left, chart_right = st.columns(2, gap="large")

    with chart_left:
        st.markdown("**Waste Distribution by Category**")

        if dist.empty:
            st.info(
                "No verified waste records are available for the "
                "category distribution chart."
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

            fig.update_traces(
                textposition="inside",
                textinfo="percent",
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Waste: %{value:.1f} kg<br>"
                    "Share: %{percent}<extra></extra>"
                ),
            )

            fig.update_layout(
                legend_title_text="Waste Category",
                margin=dict(t=25, b=20, l=10, r=10),
            )

            ui.show_chart(fig)

    with chart_right:
        st.markdown(f"**Daily Waste — Last {days} Days**")

        if trend.empty:
            st.info(
                "No daily trend data is available for the selected period."
            )
        else:
            fig = px.area(
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
            )

            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Waste (kg)",
                legend_title_text="Waste Category",
                hovermode="x unified",
                margin=dict(t=25, b=20, l=10, r=10),
            )

            ui.show_chart(fig)


# --------------------------------------------------
# Tab 2: E-waste lifecycle
# --------------------------------------------------
with tab_ewaste:
    st.subheader("E-Waste Lifecycle Overview")

    es = analytics.ewaste_status()

    if es.empty:
        st.info(
            "No e-waste assets are available yet. "
            "Lifecycle analytics will appear when assets are recorded."
        )
    else:
        fig = px.funnel(
            es,
            x="assets",
            y="status",
            title="Assets by Lifecycle Stage",
            labels={
                "assets": "Number of Assets",
                "status": "Lifecycle Stage",
            },
        )

        fig.update_layout(
            margin=dict(t=40, b=20, l=10, r=10),
        )

        ui.show_chart(fig)

        st.markdown("**Lifecycle Records**")
        st.dataframe(
            es,
            hide_index=True,
            use_container_width=True,
        )


# --------------------------------------------------
# Tab 3: Smart-bin monitoring
# --------------------------------------------------
with tab_bins:
    st.subheader("Smart-Bin Capacity Monitoring")

    df = smart_bin.bins_dataframe()

    if df.empty:
        st.info(
            "No smart-bin records are available. "
            "Capacity analytics will appear when bin data is added."
        )
    else:
        fig = px.bar(
            df.sort_values("bin_id"),
            x="bin_id",
            y="fill_level",
            color="status",
            color_discrete_map=BIN_COLORS,
            hover_data=["location"],
            labels={
                "bin_id": "Bin ID",
                "fill_level": "Fill Level (%)",
                "status": "Bin Status",
                "location": "Location",
            },
            title="Current Smart-Bin Capacity",
        )

        fig.update_yaxes(
            range=[0, 100],
            title="Capacity (%)",
        )

        fig.update_layout(
            xaxis_title="Bin ID",
            legend_title_text="Bin Status",
            margin=dict(t=40, b=20, l=10, r=10),
        )

        ui.show_chart(fig)

        st.caption(
            f"Total smart-bin records displayed: {len(df)}"
        )


# --------------------------------------------------
# Tab 4: Student participation
# --------------------------------------------------
with tab_participation:
    st.subheader("Student Participation")

    part = analytics.participation()

    if part.empty:
        st.info(
            "No student participation data is available yet. "
            "Verified disposal activity will appear here when recorded."
        )
    else:
        fig = px.bar(
            part,
            x="student",
            y="verified_disposals",
            color="kg",
            color_continuous_scale="Greens",
            labels={
                "student": "Student",
                "verified_disposals": "Verified Disposals",
                "kg": "Waste (kg)",
            },
            title="Verified Disposals per Student",
        )

        fig.update_layout(
            xaxis_title="Student",
            yaxis_title="Verified Disposals",
            margin=dict(t=40, b=20, l=10, r=10),
        )

        ui.show_chart(fig)

        st.markdown("**Participation Records**")
        st.dataframe(
            part,
            hide_index=True,
            use_container_width=True,
        )


# --------------------------------------------------
# CSV export
# --------------------------------------------------
st.divider()
st.subheader("⬇️ Export Waste Records")

records = analytics.all_waste_records()
csv_data = records.to_csv(index=False)

st.caption(
    "Download waste records in CSV format for further analysis."
)

st.download_button(
    label="Download Waste Records (CSV)",
    data=csv_data,
    file_name="ecotrack_waste_records.csv",
    mime="text/csv",
    disabled=records.empty,
)
