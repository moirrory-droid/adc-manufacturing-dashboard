import streamlit as st
from db import run_query

# ── Brand colours (matching .streamlit/config.toml) ─────────────────────────
PRODUCT_COLOURS = {
    "ADC-001 (HER2-MMAE)": "#0F52BA",  # pharmaceutical blue
    "ADC-002 (TROP2-DXd)": "#20B2AA",  # teal
    "ADC-003 (CD30-MMAE)": "#FF6B35",  # amber-orange
}

SEVERITY_COLOURS = {
    "Minor":    "#ffc107",
    "Major":    "#fd7e14",
    "Critical": "#dc3545",
}

CHART_LAYOUT = dict(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#F8F9FB",
    font_color="#1A1A2E",
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)


def render_sidebar_filters(page_label: str = "") -> tuple:
    """
    Render the standard product multiselect + date range filters in the sidebar.
    Returns (selected_products, date_from, date_to).
    Calls st.stop() if the selection is invalid.
    """
    with st.sidebar:
        st.header("Filters")

        products_df = run_query(
            "SELECT DISTINCT product FROM manufacturing.batches ORDER BY product"
        )
        all_products = products_df["product"].tolist()

        selected_products = st.multiselect(
            "Product",
            options=all_products,
            default=all_products,
            help="Filter by one or more ADC products.",
        )

        date_range_df = run_query(
            "SELECT MIN(manufacturing_date) AS min_d, "
            "MAX(manufacturing_date) AS max_d "
            "FROM manufacturing.batches"
        )
        min_date = date_range_df["min_d"].iloc[0]
        max_date = date_range_df["max_d"].iloc[0]

        date_from, date_to = st.date_input(
            "Manufacturing date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

        st.divider()
        if page_label:
            st.caption(f"ADC Dashboard · {page_label}")

    if not selected_products:
        st.warning("Select at least one product in the sidebar.")
        st.stop()

    if date_from > date_to:
        st.warning("Start date must be on or before end date.")
        st.stop()

    return selected_products, date_from, date_to
