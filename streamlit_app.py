import streamlit as st
import pandas as pd
import numpy as np

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="WSR Attribution Story",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# SIDEBAR – FILE UPLOADS
# =========================
st.sidebar.header("Upload Dataset Files")

file_feb_nov = st.sidebar.file_uploader(
    "Top Sellers – Feb–Nov 2025",
    type=["csv", "xlsx"]
)

file_oct_nov = st.sidebar.file_uploader(
    "Top Sellers – Oct–Nov 2025",
    type=["csv", "xlsx"]
)

SELLER_COL = "slr_org_nm"
GMV_COL = "GMV"
CLICKS_COL = "Clicks"

def load_df(f):
<<<<<<< HEAD
    if f.lower().endswith(".xlsx"):
        # First sheet, whatever its name is
        return pd.read_excel(f, sheet_name=0)
    elif f.lower().endswith(".csv"):
        # Try UTF-8 first, then fall back to latin1 if needed
        try:
            return pd.read_csv(f)
        except UnicodeDecodeError:
            return pd.read_csv(f, encoding="latin1")
    else:
        raise ValueError(f"Unsupported file type for: {f}")
=======
    if f is None:
        return None
    if f.name.endswith(".csv"):
        return pd.read_csv(f, encoding = "latin1")
    return pd.read_excel(f, sheet_name="sheet 1")
>>>>>>> parent of 51d63c8 (3rd Commit)

df_feb = load_df(file_feb_nov)
df_oct = load_df(file_oct_nov)

# =========================
# METRICS
# =========================
GMV_YTD = 6_500_000
BUYERS_YTD = 200_000
NOV_GMV = 920_000
NOV_PAYOUT = 50_000
NOV_ROI = NOV_GMV / NOV_PAYOUT

ATTRITION_LOSS = 2_450_000
ACTIVE_DELTA_LOSS = 1_650_000
TOTAL_DRAG = ATTRITION_LOSS + ACTIVE_DELTA_LOSS

# =========================
# HELPERS
# =========================

def compute_attrition(df_feb, df_oct):
    feb = df_feb.groupby(SELLER_COL)[GMV_COL].sum().reset_index()
    octt = df_oct.groupby(SELLER_COL)[GMV_COL].sum().reset_index()

    merged = feb.merge(octt, on=SELLER_COL, how="left", suffixes=("_feb", "_oct"))
    merged["GMV_oct"] = merged["GMV_oct"].fillna(0)

    lost = merged[merged["GMV_oct"] == 0]
    return merged, lost, lost["GMV_feb"].sum()

def compute_eff(df):
    df2 = df.copy()
    df2["gmv_per_click"] = df2[GMV_COL] / df2[CLICKS_COL].replace({0: np.nan})
    df2["flag"] = np.where(df2["gmv_per_click"] < 7, "High Clicks, Low GMV",
                  np.where(df2["gmv_per_click"] > 50, "Low Clicks, High GMV", "Normal"))
    return df2

def compute_delta(df_feb, df_oct):
    feb = df_feb.groupby(SELLER_COL)[GMV_COL].sum().reset_index()
    octt = df_oct.groupby(SELLER_COL)[GMV_COL].sum().reset_index()

    merged = feb.merge(octt, on=SELLER_COL, how="inner", suffixes=("_feb","_oct"))
    merged["gmv_change"] = merged["GMV_oct"] - merged["GMV_feb"]
    merged["pct"] = merged["gmv_change"] / merged["GMV_feb"]
    total_change = merged["gmv_change"].sum()
    return merged, total_change

# =========================
# TABS
# =========================

tab_tldr, tab_attrition, tab_eff, tab_delta, tab_decision = st.tabs(
    ["📌 TL;DR", "❌ Attrition", "⚡ Efficiency", "📉 GMV Delta", "🧭 Leadership Decision"]
)

# ======================================================
# TAB 1 — TL;DR
# ======================================================
with tab_tldr:
    st.title("📌 TL;DR — WSR Attribution Story")
    st.subheader("WSR is working too well for us to remain blind.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("WSR GMV YTD", f"${GMV_YTD:,.0f}")
    c2.metric("Incremental Buyers YTD", f"{BUYERS_YTD:,.0f}")
    c3.metric("November GMV", f"${NOV_GMV:,.0f}")
    c4.metric("ROI in November", f"{NOV_ROI:,.1f}×")

    st.markdown(
        f"""
### 🚨 Attribution is now the #1 blocker to scaling a $1B+ program  
Across the top-seller dataset:

- **$2.45M** GMV lost from churn  
- **$1.65M** GMV decline among active sellers  
- **≈ $4.1M GMV drag** in this cohort alone  

These losses are driven not by demand — **but by measurement failure**.
"""
    )

    st.info("Upload Feb–Nov & Oct–Nov datasets in the sidebar to enable all tabs.")

# ======================================================
# TAB 2 — ATTRITION
# ======================================================
with tab_attrition:
    st.title("❌ Seller Attrition — $2.45M GMV Lost")
    if df_feb is None or df_oct is None:
        st.warning("Upload files to view analysis.")
        st.stop()

    merged, lost_sellers, lost_gmv = compute_attrition(df_feb, df_oct)

    c1, c2 = st.columns(2)
    c1.metric("Total Sellers (Feb–Nov)", merged[SELLER_COL].nunique())
    c2.metric("Lost Sellers (GMV → 0)", lost_sellers[SELLER_COL].nunique())

    st.metric("GMV Lost From Seller Attrition", f"${lost_gmv:,.0f}")

    st.markdown("### Top Churned Sellers")
    st.dataframe(
        lost_sellers[[SELLER_COL, "GMV_feb"]]
        .sort_values("GMV_feb", ascending=False)
        .head(15)
        .rename(columns={"GMV_feb": "GMV Feb–Nov"})
    )

    st.bar_chart(
        lost_sellers.set_index(SELLER_COL)["GMV_feb"].sort_values(ascending=False).head(20)
    )

    st.markdown(
        """
**Examples from dataset:**

- **XIUXIAN TRADE CO LTD** — $1.85M  
- **shenzhenshixinmiaodianzi…** — $467K  
- **pcplanet** — $41K  

👉 These three alone represent **$2.36M of the $2.45M** churn loss.
"""
    )

# ======================================================
# TAB 3 — EFFICIENCY
# ======================================================
with tab_eff:
    st.title("⚡ Efficiency Anomalies — Undercounted Conversions")

    df_eff = compute_eff(df_feb)

    high = df_eff[df_eff["flag"] == "High Clicks, Low GMV"]
    low = df_eff[df_eff["flag"] == "Low Clicks, High GMV"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Sellers", df_eff[SELLER_COL].nunique())
    c2.metric("High Clicks → Low GMV", high[SELLER_COL].nunique())
    c3.metric("Low Clicks → High GMV", low[SELLER_COL].nunique())

    st.subheader("🔴 High Clicks, Low GMV (Missing Conversions)")
    st.table(
        high[[SELLER_COL, CLICKS_COL, GMV_COL, "gmv_per_click"]]
        .sort_values("gmv_per_click")
        .head(10)
    )

    st.subheader("🟠 Low Clicks, High GMV (Missing Clicks)")
    st.table(
        low[[SELLER_COL, CLICKS_COL, GMV_COL, "gmv_per_click"]]
        .sort_values("gmv_per_click", ascending=False)
        .head(10)
    )

    st.subheader("Scatter: Clicks vs GMV")
    scatter_df = df_eff.copy()
    scatter_df["color"] = scatter_df["flag"].map({
        "High Clicks, Low GMV": "red",
        "Low Clicks, High GMV": "orange",
        "Normal": "blue"
    })
    st.scatter_chart(scatter_df, x=CLICKS_COL, y=GMV_COL, color="color")

    st.markdown(
        """
**Interpretation:**
- High clicks + low GMV → conversions happening but **not attributed**  
- Low clicks + high GMV → conversions grouped incorrectly or **missing click IDs**  

These patterns **cannot** be explained by shopper behavior.

They point directly to **attribution plumbing failures**.
"""
    )

# ======================================================
# TAB 4 — GMV DELTA
# ======================================================
with tab_delta:
    st.title("📉 GMV Delta Among Active Sellers — $1.65M Down")

    delta_df, total_delta = compute_delta(df_feb, df_oct)

    st.metric("Total GMV Decline (Active Sellers)", f"${total_delta:,.0f}")

    st.subheader("Top Decliners")
    st.dataframe(
        delta_df
        .sort_values("gmv_change")
        .head(15)
        [[SELLER_COL, "GMV_feb", "GMV_oct", "gmv_change", "pct"]]
    )

    st.bar_chart(
        delta_df.sort_values("gmv_change").head(20).set_index(SELLER_COL)["gmv_change"]
    )

    st.markdown(
        """
### What this shows
Even sellers who *stayed active* saw:

- Abrupt GMV declines  
- Drops far beyond seasonality  
- Sharp pullbacks tied to **reporting mistrust**

This is *lost opportunity*, not lost demand.
"""
    )

# ======================================================
# TAB 5 — LEADERSHIP DECISION
# ======================================================
with tab_decision:
    st.title("🧭 Leadership Decision — Fund Attribution Testing in FY27")

    c1, c2 = st.columns(2)
    c1.metric("GMV Lost From Churn", f"${ATTRITION_LOSS:,.0f}")
    c2.metric("GMV Lost From Active Sellers", f"${ACTIVE_DELTA_LOSS:,.0f}")

    st.metric("Total GMV Drag Identified", f"${TOTAL_DRAG:,.0f}")

    st.markdown(
        """
## Why This Matters
WSR behaves like **Amazon Attribution / Brand Referral Bonus**, but our measurement stack still behaves like an **affiliate network**.

Attribution is not a reporting feature —  
**it is the gating factor for WSR’s $1B+ potential.**

---

## **Decision Needed**
### ✔ Do we allocate dedicated FY27 budget to run structured attribution tests?

If **YES**, we will run:

---

### **Test 1 — First Touch vs Last Touch (Google + Meta)**
- Quantifies under-attribution  
- Defines a seller-readable, transparent rule set  

---

### **Test 2 — WSR vs Amazon Brand Referral A/B**
- Direct like-for-like comparison  
- Shows the true ROI delta  
- Identifies gaps in our attribution model  

---

## Outcome
- Restored seller trust  
- Reduced GMV drag  
- Measurement-grade foundation for a $1B+ WSR program  
"""
    )

