import streamlit as st
import pandas as pd
import plotly.express as px
from db import run_query
from utils import render_sidebar_filters, PRODUCT_COLOURS, SEVERITY_COLOURS, CHART_LAYOUT

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Analytical QC — ADC Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🔬 Analytical QC")
st.caption("DAR · SEC Purity · Endotoxin · Bioburden · Release Testing")
st.divider()

# ── Sidebar filters ──────────────────────────────────────────────────────────
products, date_from, date_to = render_sidebar_filters("Analytical QC")

# ── Data fetch ───────────────────────────────────────────────────────────────
ANALYTICAL_SQL = """
SELECT
    b.batch_number,
    b.product,
    b.manufacturing_date,
    b.batch_status,
    a.dar,
    a.dar_pass,
    a.sec_purity_pct,
    a.sec_pass,
    a.endotoxin_eu_ml,
    a.endotoxin_pass,
    a.bioburden_sterility,
    a.bioburden_pass
FROM manufacturing.batches b
JOIN analytical.analytical_results a ON b.batch_number = a.batch_number
WHERE b.product = ANY(:products)
  AND b.manufacturing_date BETWEEN :date_from AND :date_to
ORDER BY b.manufacturing_date
"""

DEVIATIONS_SQL = """
SELECT
    d.deviation_id,
    d.deviation_type,
    d.severity,
    d.status,
    d.date_raised,
    b.product
FROM quality.deviations d
JOIN manufacturing.batches b ON d.batch_number = b.batch_number
WHERE b.product = ANY(:products)
  AND b.manufacturing_date BETWEEN :date_from AND :date_to
ORDER BY d.date_raised
"""

@st.cache_data(ttl=300)
def load_analytical(products_tuple, date_from, date_to):
    return run_query(ANALYTICAL_SQL, {
        "products": list(products_tuple),
        "date_from": date_from,
        "date_to": date_to,
    })

@st.cache_data(ttl=300)
def load_deviations(products_tuple, date_from, date_to):
    return run_query(DEVIATIONS_SQL, {
        "products": list(products_tuple),
        "date_from": date_from,
        "date_to": date_to,
    })

df   = load_analytical(tuple(products), date_from, date_to)
devs = load_deviations(tuple(products), date_from, date_to)
df["manufacturing_date"] = pd.to_datetime(df["manufacturing_date"])

if df.empty:
    st.info("No analytical data matches the current filters.")
    st.stop()

colour_map = {p: PRODUCT_COLOURS[p] for p in df["product"].unique() if p in PRODUCT_COLOURS}

# ── KPI cards ────────────────────────────────────────────────────────────────
dar_pass_rate  = round(df["dar_pass"].mean() * 100, 1)
sec_pass_rate  = round(df["sec_pass"].mean() * 100, 1)
endo_pass_rate = round(df["endotoxin_pass"].mean() * 100, 1)
bio_pass_rate  = round(df["bioburden_pass"].mean() * 100, 1)

k1, k2, k3, k4 = st.columns(4)
k1.metric("DAR Pass Rate",       f"{dar_pass_rate} %",  delta=f"{dar_pass_rate - 100:.1f} %")
k2.metric("SEC Purity Pass Rate", f"{sec_pass_rate} %", delta=f"{sec_pass_rate - 100:.1f} %")
k3.metric("Endotoxin Pass Rate",  f"{endo_pass_rate} %",delta=f"{endo_pass_rate - 100:.1f} %")
k4.metric("Bioburden Pass Rate",  f"{bio_pass_rate} %", delta=f"{bio_pass_rate - 100:.1f} %")

st.divider()

# ── Row 1: DAR histogram + DAR over time ─────────────────────────────────────
col_l, col_r = st.columns(2)

with col_l:
    st.subheader("DAR Distribution by Product")
    fig_dar_hist = px.histogram(
        df,
        x="dar",
        color="product",
        color_discrete_map=colour_map,
        nbins=20,
        barmode="overlay",
        opacity=0.7,
        hover_data=["batch_number"],
        labels={"dar": "Drug-to-Antibody Ratio (DAR)", "product": "Product"},
    )
    fig_dar_hist.add_vline(
        x=3.0, line_dash="dash", line_color="red",
        annotation_text="Lower spec (3.0)", annotation_position="top left",
    )
    fig_dar_hist.add_vline(
        x=4.5, line_dash="dash", line_color="red",
        annotation_text="Upper spec (4.5)", annotation_position="top right",
    )
    fig_dar_hist.update_layout(**CHART_LAYOUT)
    st.plotly_chart(fig_dar_hist, use_container_width=True)

with col_r:
    st.subheader("DAR Over Time")
    fig_dar_time = px.scatter(
        df,
        x="manufacturing_date",
        y="dar",
        color="product",
        color_discrete_map=colour_map,
        symbol="dar_pass",
        symbol_map={True: "circle", False: "x"},
        hover_data=["batch_number", "batch_status"],
        labels={
            "manufacturing_date": "Manufacturing Date",
            "dar": "DAR",
            "product": "Product",
            "dar_pass": "DAR Pass",
        },
    )
    fig_dar_time.add_hrect(
        y0=3.0, y1=4.5, fillcolor="green", opacity=0.07, line_width=0,
        annotation_text="Specification 3.0–4.5",
        annotation_position="top left",
    )
    fig_dar_time.update_layout(**CHART_LAYOUT)
    st.plotly_chart(fig_dar_time, use_container_width=True)

st.divider()

# ── Row 2: SEC purity trend + Endotoxin distribution ─────────────────────────
col_l2, col_r2 = st.columns(2)

with col_l2:
    st.subheader("SEC Purity % Over Time")
    fig_sec = px.line(
        df,
        x="manufacturing_date",
        y="sec_purity_pct",
        color="product",
        color_discrete_map=colour_map,
        markers=True,
        hover_data=["batch_number", "sec_pass"],
        labels={
            "manufacturing_date": "Manufacturing Date",
            "sec_purity_pct": "SEC Purity (%)",
            "product": "Product",
        },
    )
    fig_sec.add_hline(
        y=95.0, line_dash="dash", line_color="red",
        annotation_text="Min specification (95%)",
        annotation_position="bottom right",
    )
    fig_sec.update_yaxes(range=[88, 102])
    fig_sec.update_layout(**CHART_LAYOUT)
    st.plotly_chart(fig_sec, use_container_width=True)

with col_r2:
    st.subheader("Endotoxin Distribution (log scale)")
    fig_endo = px.histogram(
        df,
        x="endotoxin_eu_ml",
        color="product",
        color_discrete_map=colour_map,
        nbins=20,
        barmode="overlay",
        opacity=0.7,
        log_x=True,
        hover_data=["batch_number"],
        labels={
            "endotoxin_eu_ml": "Endotoxin (EU/mL) — log scale",
            "product": "Product",
        },
    )
    fig_endo.add_vline(
        x=1.0, line_dash="dash", line_color="red",
        annotation_text="Limit: 1.0 EU/mL",
        annotation_position="top right",
    )
    fig_endo.update_layout(**CHART_LAYOUT)
    st.plotly_chart(fig_endo, use_container_width=True)

st.divider()

# ── Row 3: Release test pass-rate heatmap (full width) ───────────────────────
st.subheader("Release Test Pass Rates by Product")

pivot = (
    df.groupby("product")[["dar_pass", "sec_pass", "endotoxin_pass", "bioburden_pass"]]
    .mean() * 100
)
pivot.columns = ["DAR", "SEC Purity", "Endotoxin", "Bioburden"]
pivot = pivot.reset_index().set_index("product")

fig_heat = px.imshow(
    pivot,
    text_auto=".1f",
    color_continuous_scale="RdYlGn",
    range_color=[80, 100],
    labels={"color": "Pass Rate (%)"},
    aspect="auto",
)
fig_heat.update_layout(**CHART_LAYOUT, coloraxis_colorbar_title="Pass Rate (%)")
fig_heat.update_xaxes(side="bottom")
st.plotly_chart(fig_heat, use_container_width=True)

st.divider()

# ── Row 4: Deviations by type and severity ───────────────────────────────────
st.subheader("Deviations by Type and Severity")

if devs.empty:
    st.info("No deviations recorded for the current filter selection.")
else:
    dev_counts = (
        devs.groupby(["deviation_type", "severity"])
        .size()
        .reset_index(name="count")
    )
    fig_devs = px.bar(
        dev_counts,
        x="deviation_type",
        y="count",
        color="severity",
        barmode="stack",
        color_discrete_map=SEVERITY_COLOURS,
        labels={
            "deviation_type": "Deviation Type",
            "count": "Count",
            "severity": "Severity",
        },
        category_orders={"severity": ["Minor", "Major", "Critical"]},
    )
    fig_devs.update_layout(**CHART_LAYOUT)
    fig_devs.update_xaxes(tickangle=20)

    col_dev, _ = st.columns([2, 1])
    with col_dev:
        st.plotly_chart(fig_devs, use_container_width=True)
