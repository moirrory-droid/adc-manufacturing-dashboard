import streamlit as st
import pandas as pd
import plotly.express as px
from db import run_query
from utils import render_sidebar_filters, PRODUCT_COLOURS, CHART_LAYOUT

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Process Analytics — ADC Dashboard",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("⚗️ Process Analytics")
st.caption("Conjugation efficiency · Purification recovery · Overall yield trends")
st.divider()

# ── Sidebar filters ──────────────────────────────────────────────────────────
products, date_from, date_to = render_sidebar_filters("Process Analytics")

# ── Data fetch ───────────────────────────────────────────────────────────────
SQL = """
SELECT
    b.batch_number,
    b.product,
    b.manufacturing_date,
    b.batch_size_mg,
    b.overall_yield_mg,
    ROUND((b.overall_yield_mg / b.batch_size_mg * 100)::numeric, 1) AS overall_yield_pct,
    b.batch_status,
    bc.reaction_temperature_c,
    bc.reaction_time_hrs,
    bc.dmso_concentration_pct,
    bc.conjugation_yield_pct,
    p.tff_passes,
    p.purification_recovery_pct,
    p.final_concentration_mg_ml
FROM manufacturing.batches b
LEFT JOIN manufacturing.bioconjugation bc ON b.batch_number = bc.batch_number
LEFT JOIN manufacturing.purification p    ON b.batch_number = p.batch_number
WHERE b.product = ANY(:products)
  AND b.manufacturing_date BETWEEN :date_from AND :date_to
ORDER BY b.manufacturing_date
"""

@st.cache_data(ttl=300)
def load_data(products_tuple, date_from, date_to):
    return run_query(SQL, {
        "products": list(products_tuple),
        "date_from": date_from,
        "date_to": date_to,
    })

df = load_data(tuple(products), date_from, date_to)
df["manufacturing_date"] = pd.to_datetime(df["manufacturing_date"])

if df.empty:
    st.info("No data matches the current filters.")
    st.stop()

# ── KPI cards ────────────────────────────────────────────────────────────────
avg_conj   = round(df["conjugation_yield_pct"].mean(), 1)
avg_purif  = round(df["purification_recovery_pct"].mean(), 1)
avg_yield  = round(df["overall_yield_pct"].mean(), 1)
avg_conc   = round(df["final_concentration_mg_ml"].mean(), 2)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Avg Conjugation Yield", f"{avg_conj} %")
k2.metric("Avg Purification Recovery", f"{avg_purif} %")
k3.metric("Avg Overall Yield", f"{avg_yield} %")
k4.metric("Avg Final Concentration", f"{avg_conc} mg/mL")

st.divider()

# ── Chart 1 — Overall Yield % Over Time ──────────────────────────────────────
st.subheader("Overall Yield % Over Time")

colour_map = {p: PRODUCT_COLOURS[p] for p in df["product"].unique() if p in PRODUCT_COLOURS}

fig_yield = px.scatter(
    df,
    x="manufacturing_date",
    y="overall_yield_pct",
    color="product",
    symbol="batch_status",
    symbol_map={"Pass": "circle", "Fail": "x"},
    color_discrete_map=colour_map,
    hover_data={"batch_number": True, "conjugation_yield_pct": True,
                "purification_recovery_pct": True, "manufacturing_date": False},
    labels={
        "manufacturing_date": "Manufacturing Date",
        "overall_yield_pct": "Overall Yield (%)",
        "product": "Product",
        "batch_status": "Status",
    },
    trendline="lowess",
    trendline_scope="overall",
    trendline_color_override="#888888",
)
fig_yield.add_hline(
    y=75, line_dash="dash", line_color="red",
    annotation_text="Min acceptable yield (75%)",
    annotation_position="bottom right",
)
fig_yield.update_layout(**CHART_LAYOUT)
fig_yield.update_yaxes(range=[30, 105])
st.plotly_chart(fig_yield, use_container_width=True)

st.divider()

# ── Row 2: Conjugation box + Temperature scatter ──────────────────────────────
col_l, col_r = st.columns(2)

with col_l:
    st.subheader("Conjugation Yield by Product")
    fig_box = px.box(
        df,
        x="product",
        y="conjugation_yield_pct",
        color="product",
        color_discrete_map=colour_map,
        points="all",
        hover_data=["batch_number", "batch_status"],
        labels={
            "product": "Product",
            "conjugation_yield_pct": "Conjugation Yield (%)",
        },
    )
    fig_box.update_layout(**CHART_LAYOUT, showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

with col_r:
    st.subheader("Conjugation Yield vs. Reaction Temperature")
    fig_temp = px.scatter(
        df,
        x="reaction_temperature_c",
        y="conjugation_yield_pct",
        color="product",
        color_discrete_map=colour_map,
        hover_data=["batch_number", "dmso_concentration_pct", "batch_status"],
        labels={
            "reaction_temperature_c": "Reaction Temperature (°C)",
            "conjugation_yield_pct": "Conjugation Yield (%)",
            "product": "Product",
        },
    )
    fig_temp.add_vline(
        x=25.0, line_dash="dash", line_color="#888888",
        annotation_text="Setpoint (25°C)",
        annotation_position="top left",
    )
    fig_temp.update_layout(**CHART_LAYOUT)
    st.plotly_chart(fig_temp, use_container_width=True)

st.divider()

# ── Row 3: Purification trend + Step yield comparison ────────────────────────
col_l2, col_r2 = st.columns(2)

with col_l2:
    st.subheader("Purification Recovery Over Time")
    fig_purif = px.line(
        df,
        x="manufacturing_date",
        y="purification_recovery_pct",
        color="product",
        color_discrete_map=colour_map,
        markers=True,
        hover_data=["batch_number", "tff_passes"],
        labels={
            "manufacturing_date": "Manufacturing Date",
            "purification_recovery_pct": "Purification Recovery (%)",
            "product": "Product",
        },
    )
    fig_purif.add_hline(
        y=80, line_dash="dash", line_color="red",
        annotation_text="Min acceptable (80%)",
        annotation_position="bottom right",
    )
    fig_purif.update_layout(**CHART_LAYOUT)
    st.plotly_chart(fig_purif, use_container_width=True)

with col_r2:
    st.subheader("Step Yield: Conjugation vs. Purification")

    # Reshape to long form for grouped bar
    step_df = df[["batch_number", "manufacturing_date", "product",
                  "conjugation_yield_pct", "purification_recovery_pct"]].copy()
    step_df = step_df.sort_values("manufacturing_date").tail(20)  # last 20 batches
    step_long = step_df.melt(
        id_vars=["batch_number", "manufacturing_date", "product"],
        value_vars=["conjugation_yield_pct", "purification_recovery_pct"],
        var_name="Step",
        value_name="Yield (%)",
    )
    step_long["Step"] = step_long["Step"].map({
        "conjugation_yield_pct": "Conjugation",
        "purification_recovery_pct": "Purification",
    })

    fig_steps = px.bar(
        step_long,
        x="batch_number",
        y="Yield (%)",
        color="Step",
        barmode="group",
        color_discrete_map={"Conjugation": "#0F52BA", "Purification": "#20B2AA"},
        hover_data=["product", "manufacturing_date"],
        labels={"batch_number": "Batch"},
    )
    fig_steps.update_layout(**CHART_LAYOUT)
    fig_steps.update_xaxes(tickangle=45)
    st.plotly_chart(fig_steps, use_container_width=True)
    st.caption("Showing last 20 batches by manufacturing date.")
