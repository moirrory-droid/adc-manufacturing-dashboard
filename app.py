import streamlit as st
import pandas as pd
from datetime import date
from db import run_query

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ADC Manufacturing Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Header ───────────────────────────────────────────────────────────────────
st.title("🧬 ADC Manufacturing Intelligence Dashboard")
st.caption("Batch Overview · Manufacturing · Analytical · Quality")
st.divider()

# ── Sidebar filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")

    # Fetch distinct products for the multiselect
    products_df = run_query("SELECT DISTINCT product FROM manufacturing.batches ORDER BY product")
    all_products = products_df["product"].tolist()

    selected_products = st.multiselect(
        "Product",
        options=all_products,
        default=all_products,
        help="Filter by one or more ADC products.",
    )

    # Date range — default to full data range
    date_range_df = run_query(
        "SELECT MIN(manufacturing_date) AS min_d, MAX(manufacturing_date) AS max_d "
        "FROM manufacturing.batches"
    )
    min_date = date_range_df["min_d"].iloc[0]
    max_date = date_range_df["max_d"].iloc[0]

    date_from, date_to = st.date_input(
        "Manufacturing date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Filter batches by their manufacturing date.",
    )

    st.divider()
    st.caption("ADC Dashboard · Session 2")

# Guard: user cleared all products
if not selected_products:
    st.warning("Select at least one product in the sidebar.")
    st.stop()

# Guard: invalid date range (user dragged slider to same point)
if date_from > date_to:
    st.warning("Start date must be on or before end date.")
    st.stop()

# ── Main query ───────────────────────────────────────────────────────────────
SQL = """
SELECT
    b.batch_number                                          AS "Batch",
    b.product                                               AS "Product",
    b.manufacturing_date                                    AS "Mfg Date",
    b.batch_size_mg                                         AS "Batch Size (mg)",
    b.overall_yield_mg                                      AS "Yield (mg)",
    ROUND((b.overall_yield_mg / b.batch_size_mg * 100)::numeric, 1)
                                                            AS "Yield %",
    a.dar                                                   AS "DAR",
    a.sec_purity_pct                                        AS "SEC Purity %",
    a.endotoxin_eu_ml                                       AS "Endotoxin (EU/mL)",
    b.batch_status                                          AS "Status",
    COUNT(d.deviation_id)                                   AS "Deviations"
FROM manufacturing.batches b
LEFT JOIN analytical.analytical_results a
       ON b.batch_number = a.batch_number
LEFT JOIN quality.deviations d
       ON b.batch_number = d.batch_number
WHERE b.product = ANY(:products)
  AND b.manufacturing_date BETWEEN :date_from AND :date_to
GROUP BY
    b.batch_number, b.product, b.manufacturing_date,
    b.batch_size_mg, b.overall_yield_mg,
    a.dar, a.sec_purity_pct, a.endotoxin_eu_ml,
    b.batch_status
ORDER BY b.manufacturing_date DESC
"""

df = run_query(
    SQL,
    params={
        "products": selected_products,
        "date_from": date_from,
        "date_to": date_to,
    },
)

# ── KPI summary cards ────────────────────────────────────────────────────────
total     = len(df)
passed    = (df["Status"] == "Pass").sum()
pass_rate = round(passed / total * 100, 1) if total else 0
avg_yield = round(df["Yield %"].mean(), 1) if total else 0
open_devs = int(df["Deviations"].sum())

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Batches", total)
kpi2.metric("Pass Rate", f"{pass_rate} %", delta=None)
kpi3.metric("Avg Yield", f"{avg_yield} %")
kpi4.metric("Total Deviations", open_devs)

st.divider()

# ── Batch table ───────────────────────────────────────────────────────────────
st.subheader(f"Batch Records ({total})")

if df.empty:
    st.info("No batches match the current filters.")
else:
    # Colour-code the Status column
    def style_status(val):
        colour = "#d4edda" if val == "Pass" else "#f8d7da"
        text   = "#155724" if val == "Pass" else "#721c24"
        return f"background-color: {colour}; color: {text}; font-weight: 600;"

    styled = df.style.applymap(style_status, subset=["Status"])

    st.dataframe(
        styled,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Batch":               st.column_config.TextColumn("Batch", width="small"),
            "Product":             st.column_config.TextColumn("Product"),
            "Mfg Date":            st.column_config.DateColumn("Mfg Date", format="DD MMM YYYY"),
            "Batch Size (mg)":     st.column_config.NumberColumn("Batch Size (mg)", format="%.1f"),
            "Yield (mg)":          st.column_config.NumberColumn("Yield (mg)", format="%.1f"),
            "Yield %":             st.column_config.ProgressColumn(
                                       "Yield %", format="%.1f %%", min_value=0, max_value=100
                                   ),
            "DAR":                 st.column_config.NumberColumn("DAR", format="%.2f"),
            "SEC Purity %":        st.column_config.NumberColumn("SEC Purity %", format="%.2f"),
            "Endotoxin (EU/mL)":   st.column_config.NumberColumn("Endotoxin (EU/mL)", format="%.3f"),
            "Status":              st.column_config.TextColumn("Status", width="small"),
            "Deviations":          st.column_config.NumberColumn("Deviations", width="small"),
        },
    )

    # Download button
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name=f"adc_batches_{date_from}_to_{date_to}.csv",
        mime="text/csv",
    )
