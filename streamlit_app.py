import streamlit as st
import pandas as pd
import numpy as np

# ==============================
# CONFIG & CONSTANTS
# ==============================
ST_TITLE = "Walmart Sales Rewards (WSR) – Attribution Health & Test Proposal"

# Hard-coded program-level context (from your narrative)
PROGRAM_GMV_YTD = 6_500_000
PROGRAM_INCREMENTAL_BUYERS = 200_000
PROGRAM_NOV_GMV = 920_000
PROGRAM_NOV_PAYOUTS = 50_000
PROGRAM_NOV_ROI = PROGRAM_NOV_GMV / PROGRAM_NOV_PAYOUTS  # ~18x

# Sample GMV drag numbers from your analysis
GMV_LOST_CHURN = 2_450_000
GMV_LOST_ACTIVE_DELTA = 1_650_000
GMV_TOTAL_DRAG = GMV_LOST_CHURN + GMV_LOST_ACTIVE_DELTA

# Expected column names – adjust here if needed
SELLER_COL = "slr_org_nm"
GMV_COL = "GMV"
CLICKS_COL = "Clicks"

# ==============================
# HELPERS
# ==============================

def load_dataframe(uploaded_file):
    if uploaded_file is None:
        return None

    if uploaded_file.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        # default to first sheet or "sheet 1"
        try:
            df = pd.read_excel(uploaded_file, sheet_name="sheet 1")
        except Exception:
            df = pd.read_excel(uploaded_file)
    return df


def compute_attrition(df_feb_nov, df_oct_nov):
    """Identify sellers present in Feb–Nov but with zero GMV in Oct–Nov."""
    feb_sellers = df_feb_nov[[SELLER_COL, GMV_COL]].groupby(SELLER_COL, as_index=False).sum()
    oct_sellers = df_oct_nov[[SELLER_COL, GMV_COL]].groupby(SELLER_COL, as_index=False).sum()

    merged = feb_sellers.merge(
        oct_sellers,
        on=SELLER_COL,
        how="left",
        suffixes=("_feb_nov", "_oct_nov")
    )

    merged[GMV_COL + "_oct_nov"] = merged[GMV_COL + "_oct_nov"].fillna(0)

    lost = merged[merged[GMV_COL + "_oct_nov"] == 0].copy()
    lost_total = lost[GMV_COL + "_feb_nov"].sum()

    return merged, lost, lost_total


def compute_efficiency(df):
    """Compute GMV/Click and flag anomalies."""
    df_eff = df.copy()
    df_eff["gmv_per_click"] = df_eff[GMV_COL] / df_eff[CLICKS_COL].replace({0: np.nan})
    # simple flags based on your narrative thresholds
    df_eff["efficiency_flag"] = np.where(
        df_eff["gmv_per_click"] < 7, "High Clicks, Low GMV",
        np.where(df_eff["gmv_per_click"] > 50, "Low Clicks, High GMV", "Normal")
    )
    return df_eff


def compute_gmv_delta(df_feb_nov, df_oct_nov):
    feb = df_feb_nov[[SELLER_COL, GMV_COL]].groupby(SELLER_COL, as_index=False).sum()
    octo = df_oct_nov[[SELLER_COL, GMV_COL]].groupby(SELLER_COL, as_index=False).sum()

    merged = feb.merge(octo, on=SELLER_COL, how="inner", suffixes=("_feb_nov", "_oct_nov"))
    merged["gmv_change"] = merged[GMV_COL + "_oct_nov"] - merged[GMV_COL + "_feb_nov"]
    merged["gmv_change_pct"] = np.where(
        merged[GMV_COL + "_feb_nov"] > 0,
        merged["gmv_change"] / merged[GMV_COL + "_feb_nov"],
        np.nan
    )
    total_delta = merged["gmv_change"].sum()
    return merged, total_delta


# ==============================
# STREAMLIT APP
# ==============================

st.set_page_config(page_title=ST_TITLE, layout="wide")
st.title(ST_TITLE)

st.markdown(
    """
**Purpose:**  
Give leadership a **data-backed view** of WSR’s attribution issues (attrition, efficiency anomalies, GMV drag)  
and support the ask for **dedicated FY27 budget** to run attribution tests across providers/channels.
"""
)

# ------------------------------
# SIDEBAR – DATA INPUT
# ------------------------------
st.sidebar.header("1. Upload WSR Seller Datasets")

file_feb_nov = st.sidebar.file_uploader(
    "Top Sellers – Feb–Nov 2025 (CSV or XLSX)",
    type=["csv", "xlsx"],
    key="feb_nov"
)

file_oct_nov = st.sidebar.file_uploader(
    "Top Sellers – Oct–Nov 2025 (CSV or XLSX)",
    type=["csv", "xlsx"],
    key="oct_nov"
)

st.sidebar.markdown("---")
st.sidebar.header("2. Program Context (editable)")

gmv_ytd = st.sidebar.number_input(
    "WSR GMV YTD",
    value=float(PROGRAM_GMV_YTD),
    step=100000.0
)
buyers_ytd = st.sidebar.number_input(
    "Incremental Buyers YTD",
    value=float(PROGRAM_INCREMENTAL_BUYERS),
    step=10000.0
)
nov_gmv = st.sidebar.number_input(
    "November GMV",
    value=float(PROGRAM_NOV_GMV),
    step=50000.0
)
nov_payouts = st.sidebar.number_input(
    "November Payouts",
    value=float(PROGRAM_NOV_PAYOUTS),
    step=5000.0
)
nov_roi = nov_gmv / nov_payouts if nov_payouts > 0 else 0.0

st.sidebar.markdown("---")
st.sidebar.caption("Tip: If the app errors, verify that your files contain columns named "
                   f"`{SELLER_COL}`, `{GMV_COL}`, and `{CLICKS_COL}` or update the script accordingly.")

# ------------------------------
# TOP SUMMARY – PROGRAM HEALTH
# ------------------------------
st.subheader("WSR Program Snapshot (YTD)")

col1, col2, col3, col4 = st.columns(4)
col1.metric("WSR GMV YTD", f"${gmv_ytd:,.0f}")
col2.metric("Incremental Buyers YTD", f"{buyers_ytd:,.0f}")
col3.metric("Nov GMV", f"${nov_gmv:,.0f}")
col4.metric("Nov ROI", f"{nov_roi:,.1f}x")

st.markdown(
    """
WSR is already a **high-intent, high-ROI** program — much closer to **Amazon Attribution / Brand Referral Bonus**  
than to classic coupon affiliates. The question is not *if* it works, but whether our **measurement layer keeps up**.
"""
)

# ------------------------------
# DATA-DRIVEN INSIGHTS
# ------------------------------
if file_feb_nov is None or file_oct_nov is None:
    st.warning("Please upload both the Feb–Nov and Oct–Nov files in the sidebar to see the analysis.")
    st.stop()

df_feb_nov = load_dataframe(file_feb_nov)
df_oct_nov = load_dataframe(file_oct_nov)

# Guardrails
required_cols = {SELLER_COL, GMV_COL, CLICKS_COL}
missing_feb = required_cols - set(df_feb_nov.columns)
missing_oct = required_cols - set(df_oct_nov.columns)

if missing_feb or missing_oct:
    st.error(
        f"Missing expected columns.\n\n"
        f"Feb–Nov missing: {missing_feb}\n"
        f"Oct–Nov missing: {missing_oct}\n\n"
        "Please update column names or adjust the script constants."
    )
    st.stop()

st.subheader("1. Seller Cohort Overview")

n_feb = df_feb_nov[SELLER_COL].nunique()
n_oct = df_oct_nov[SELLER_COL].nunique()

c1, c2 = st.columns(2)
c1.metric("Sellers (Feb–Nov)", f"{n_feb}")
c2.metric("Sellers (Oct–Nov)", f"{n_oct}", delta=f"{n_oct - n_feb}")

st.markdown(
    """
We compare **Top Sellers (Feb–Nov)** vs **Oct–Nov** to understand:
- Who churned out of WSR
- How efficiency (GMV per click) looks across sellers
- How GMV shifted for those who stayed
"""
)

# ------------------------------
# 1) ATTRITION – LOST SELLERS
# ------------------------------
st.subheader("2. Attrition – Sellers Lost & GMV at Risk")

merged_attr, lost_sellers_df, lost_total_gmv = compute_attrition(df_feb_nov, df_oct_nov)

c1, c2, c3 = st.columns(3)
c1.metric("Total Sellers (Feb–Nov)", f"{n_feb}")
c2.metric("Lost Sellers (GMV → 0 in Oct–Nov)", f"{lost_sellers_df[SELLER_COL].nunique()}")
c3.metric("GMV at Risk (Lost Sellers)", f"${lost_total_gmv:,.0f}")

st.markdown("**Top Lost Sellers by GMV (from Feb–Nov)**")
st.dataframe(
    lost_sellers_df[[SELLER_COL, f"{GMV_COL}_feb_nov"]]
    .sort_values(by=f"{GMV_COL}_feb_nov", ascending=False)
    .head(10)
    .rename(columns={f"{GMV_COL}_feb_nov": "GMV_Feb_Nov"})
)

st.bar_chart(
    lost_sellers_df
    .sort_values(by=f"{GMV_COL}_feb_nov", ascending=False)
    .head(10)
    .set_index(SELLER_COL)[f"{GMV_COL}_feb_nov"],
    use_container_width=True
)

st.caption(
    f"Across the full cohort, lost sellers represent **≈ ${lost_total_gmv:,.0f} GMV**. "
    "In your earlier sample, three sellers like XIUXIAN, shenzhenshixinmiaodianzi, and pcplanet alone represented ~$2.36M."
)

# ------------------------------
# 2) EFFICIENCY – GMV PER CLICK
# ------------------------------
st.subheader("3. Efficiency Anomalies – GMV per Click")

df_eff = compute_efficiency(df_feb_nov)

# Summary stats
high_clicks_low_gmv = df_eff[df_eff["efficiency_flag"] == "High Clicks, Low GMV"]
low_clicks_high_gmv = df_eff[df_eff["efficiency_flag"] == "Low Clicks, High GMV"]

col_a, col_b, col_c = st.columns(3)
col_a.metric("Total Sellers (Feb–Nov)", f"{df_eff[SELLER_COL].nunique()}")
col_b.metric("High Clicks, Low GMV", f"{high_clicks_low_gmv[SELLER_COL].nunique()}")
col_c.metric("Low Clicks, High GMV", f"{low_clicks_high_gmv[SELLER_COL].nunique()}")

st.markdown("**High Clicks, Low GMV per Click (Potential Undercounting)**")
st.dataframe(
    high_clicks_low_gmv[[SELLER_COL, CLICKS_COL, GMV_COL, "gmv_per_click"]]
    .sort_values(by="gmv_per_click")
    .head(10)
)

st.markdown("**Low Clicks, Very High GMV per Click (Potential Missing Clicks / Mis-grouped Conversions)**")
st.dataframe(
    low_clicks_high_gmv[[SELLER_COL, CLICKS_COL, GMV_COL, "gmv_per_click"]]
    .sort_values(by="gmv_per_click", ascending=False)
    .head(10)
)

st.markdown("**Clicks vs GMV Scatter (Colored by Efficiency Flag)**")
scatter_df = df_eff.copy()
scatter_df["flag_color"] = scatter_df["efficiency_flag"].map(
    {
        "High Clicks, Low GMV": "red",
        "Low Clicks, High GMV": "orange",
        "Normal": "blue",
    }
)

st.scatter_chart(
    scatter_df,
    x=CLICKS_COL,
    y=GMV_COL,
    color="flag_color",
    use_container_width=True
)

st.caption(
    "Red = many clicks but low GMV per click; Orange = few clicks but very high GMV per click. "
    "Both patterns are more consistent with **attribution misalignment** than with normal shopper behavior."
)

# ------------------------------
# 3) GMV DELTAS – ACTIVE SELLERS
# ------------------------------
st.subheader("4. GMV Delta – Performance Among Active Sellers")

gmv_delta_df, total_delta = compute_gmv_delta(df_feb_nov, df_oct_nov)

st.metric("Total GMV Change (Overlapping Sellers)", f"${total_delta:,.0f}")

st.markdown("**Top 15 Sellers by GMV Decline**")
decliners = gmv_delta_df.sort_values(by="gmv_change").head(15)
st.dataframe(
    decliners[[SELLER_COL, f"{GMV_COL}_feb_nov", f"{GMV_COL}_oct_nov", "gmv_change", "gmv_change_pct"]]
)

st.bar_chart(
    decliners.set_index(SELLER_COL)["gmv_change"],
    use_container_width=True
)

st.caption(
    "Several top sellers show GMV drops far beyond normal seasonality, often after raising attribution concerns. "
    "This suggests **lost trust in reporting**, not loss of underlying demand."
)

# ------------------------------
# 4) GMV DRAG SUMMARY
# ------------------------------
st.subheader("5. GMV Drag Summary (Sample Cohort)")

summary_df = pd.DataFrame(
    {
        "Component": ["Lost sellers (churn)", "Declines among active sellers"],
        "GMV Impact": [GMV_LOST_CHURN, GMV_LOST_ACTIVE_DELTA],
    }
)
summary_df["GMV Impact (formatted)"] = summary_df["GMV Impact"].map(lambda x: f"${x:,.0f}")

st.table(summary_df[["Component", "GMV Impact (formatted)"]])

st.metric("Total GMV Drag (Sample)", f"${GMV_TOTAL_DRAG:,.0f}")

st.caption(
    f"Even recovering **20–30%** of this ≈ **${0.2 * GMV_TOTAL_DRAG:,.0f}–${0.3 * GMV_TOTAL_DRAG:,.0f} GMV** from this cohort alone. "
    "Scaled to full-program volume, the upside is much larger."
)

# ------------------------------
# 5) LEADERSHIP ASK – TEST PLAN
# ------------------------------
st.subheader("6. Leadership Decision & Test Plan")

st.markdown(
    """
### Decision

**Do we agree** that we must allocate **dedicated FY27 budget** to run structured attribution tests  
across providers and channels to restore trust, recover GMV drag, and unlock WSR’s growth?

If **yes**, we propose to run the following tests:

---

#### Test 1 – First-Touch vs Last-Touch (Google & Meta)

- **Design:** Side-by-side measurement comparing first-touch vs last-touch models  
  across Google Ads and Meta campaigns driving WSR traffic.
- **Goal:** Quantify under-attribution in current last-touch setup  
  and define an updated, transparent attribution rule set for sellers and partners.

---

#### Test 2 – WSR vs Amazon Brand Referral

- **Design:** Matched campaigns where selected sellers run equivalent budgets, creatives,  
  and targeting on **WSR** and **Amazon Brand Referral Bonus**.
- **Goal:** Measure true ROI and incrementality of WSR vs Amazon under aligned attribution,  
  and identify where we must close the gap (windows, event capture, tagging).

---

**Outcome of These Tests Will Drive:**

- Our **WSR attribution model** (window, touch rules, event capture)
- Our **WSR API roadmap** (tag design, campaign + product reporting)
- Our **seller narrative**: WSR as the most transparent, performance-grade way to drive offsite traffic to Walmart.
"""
)

st.success(
    "WSR is already a high-ROI program with +$1B potential. The constraint is no longer demand or economics, "
    "but **attribution trust**. This app surfaces the data-driven case to fix that."
)

