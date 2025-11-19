import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="WSR Attribution Test — Exec View",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# DATA LOADERS
# -------------------------------

@st.cache_data
def load_excel(path):
    return pd.read_excel(path, sheet_name=0)

@st.cache_data
def load_csv(path: str) -> pd.DataFrame:
    """
    Robust CSV loader for Streamlit Cloud.
    - Tries UTF-8 first
    - Falls back to latin1
    - Ignores bad lines instead of crashing
    """
    try:
        return pd.read_csv(
            path,
            encoding="utf-8",
            engine="python",
            on_bad_lines="skip"
        )
    except UnicodeDecodeError:
        return pd.read_csv(
            path,
            encoding="latin1",
            engine="python",
            on_bad_lines="skip"
        )
#helper function 
def prepare_df(df: pd.DataFrame, label: str) -> pd.DataFrame:
    # Show columns in the UI (helps debugging)
    st.write(f"📄 Columns in {label} file:", list(df.columns))

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # Try to detect the GMV column by name
    possible_gmv_keys = ["gmv", "total_gmv", "gmv_usd", "gross_merc", "grossmerchandise"]
    gmv_col = None
    for col in df.columns:
        if any(key in col for key in possible_gmv_keys):
            gmv_col = col
            break

    if gmv_col is None:
        st.error(f"❌ No GMV-like column found in {label} file. Available columns: {list(df.columns)}")
        # Create an empty GMV column so the rest of the app doesn't crash
        df["gmv"] = 0.0
    else:
        st.success(f"✅ Using '{gmv_col}' as GMV column for {label}.")
        df["gmv"] = pd.to_numeric(df[gmv_col], errors="coerce")

    return df

df_feb = load_excel("data/Top Sellers-Feb-November-25.xlsx")
st.write("Columns in Feb–Nov file:", df_feb.columns.tolist())
df_oct = load_csv("data/Top Sellers-Oct-Nov-25.csv")


df_feb = prepare_df(df_feb, "Feb–Nov")
df_oct = prepare_df(df_oct, "Oct–Nov")

# Normalize column names
df_feb.columns = df_feb.columns.str.lower()
df_oct.columns = df_oct.columns.str.lower()


# -------------------------------
# HELPERS
# -------------------------------

def walmart_header(title, subtitle=None):
    st.markdown(f"""
        <div style='padding: 12px 0;'>
            <h1 style='color:#0071CE; margin-bottom:0;'>{title}</h1>
            {f"<p style='font-size:18px; color:#4D4D4D;'>{subtitle}</p>" if subtitle else ""}
            <hr style='margin-top:6px; margin-bottom:18px; border: 1px solid #E6E6E6;'/>
        </div>
    """, unsafe_allow_html=True)


# =============================================================
# TAB LAYOUT — ONE TAB PER SLIDE
# =============================================================

tabs = st.tabs([
    "1. Title",
    "2. TL;DR",
    "3. Attrition Problem",
    "4. Efficiency Issues",
    "5. GMV Delta",
    "6. Strategic Importance",
    "7. FY27 Test Program",
    "8. Leadership Decision"
])

# =============================================================
# SLIDE 1 — TITLE
# =============================================================
with tabs[0]:
    walmart_header("Walmart Sales Rewards (WSR)", "FY27 Attribution Test Program")

    st.markdown("""
    ### Objective  
    Align leadership on investing in a cross-provider attribution modernization program to restore seller confidence, recover suppressed GMV, and unlock a +$1B performance channel.
    """)

    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Walmart_logo.svg/2560px-Walmart_logo.svg.png", width=280)


# =============================================================
# SLIDE 2 — TL;DR
# =============================================================
with tabs[1]:
    walmart_header("TL;DR — Why Now")

    col1, col2 = st.columns([0.55, 0.45])

    with col1:
        st.markdown("""
        ### WSR is working — too well for us to remain blind  
        - **YTD GMV:** ~$6.5M  
        - **Incremental buyers:** ~200,000  
        - **ROI:** ~18× (e.g., $920K GMV in November vs $50K payouts)  
        - **Traffic quality:** High-intent (Google Ads, Meta) — more like **Amazon Brand Referral Bonus (~$10B)** than affiliates  

        ### The problem  
        - Sellers & solution providers **cannot reconcile WSR attribution**
        - Conversions undercounted  
        - Clicks mismatched  
        - Campaign effectiveness unclear  

        ### The ask  
        **Fund a FY27 attribution test program** to modernize measurement and unlock growth.
        """)

    with col2:
        # ROI donut chart
        fig = go.Figure(go.Pie(
            labels=["Payouts ($50K)", "GMV ($920K)"],
            values=[50, 920],
            hole=0.55,
            marker_colors=["#FFC220", "#0071CE"]
        ))
        fig.update_layout(title="November ROI Snapshot", showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

# =============================================================
# SLIDE 3 — ATTRITION
# =============================================================
with tabs[2]:
    walmart_header("Attribution Problem: Seller Attrition → –$2.45M GMV Lost")

    st.markdown("""
    ### What happened  
    - **295** sellers in Feb–Nov dataset  
    - **149** still active in Oct–Nov  
    - **145** churned (GMV → 0)  
    - **Lost GMV from churned sellers:** **$2.45M**  

    These are not small sellers — they are high-value contributors who disappeared when attribution could not be reconciled.
    """)

    lost_sellers = df_feb.merge(df_oct, on="seller_id", how="left", suffixes=("_feb", "_oct"))
    lost_sellers = lost_sellers[lost_sellers["gmv_oct"].isna()]

    st.markdown("### Largest Churned Sellers")
    st.dataframe(
        lost_sellers[["slr_org_nm_feb", "gmv_feb"]]
        .sort_values(by="gmv_feb", ascending=False)
        .head(10)
    )

    fig = px.bar(
        lost_sellers.sort_values("gmv_feb", ascending=False).head(10),
        x="slr_org_nm_feb",
        y="gmv_feb",
        title="Top Churned Seller GMV (Lost)",
        color_discrete_sequence=["#0071CE"]
    )
    st.plotly_chart(fig, use_container_width=True)

# =============================================================
# SLIDE 4 — EFFICIENCY ISSUES
# =============================================================
with tabs[3]:
    walmart_header("Attribution Problem: Efficiency Signals Show Misalignment")

    st.markdown("""
    ### Pattern A — High Clicks, Low GMV per Click  
    Strong indicator that **conversions are missing**.
    """)

    pattern_a = df_feb[df_feb["gmv"]/df_feb["clicks"] < 3].nsmallest(10, "gmv")
    pattern_a["gmv_per_click"] = pattern_a["gmv"] / pattern_a["clicks"]

    st.dataframe(pattern_a[["slr_org_nm", "clicks", "gmv", "gmv_per_click"]])

    st.markdown("### Pattern B — Low Clicks, High GMV per Click (missing click IDs)")
    pattern_b = df_feb[df_feb["gmv"]/df_feb["clicks"] > 100].nlargest(10, "gmv")
    pattern_b["gmv_per_click"] = pattern_b["gmv"] / pattern_b["clicks"]

    st.dataframe(pattern_b[["slr_org_nm", "clicks", "gmv", "gmv_per_click"]])

# =============================================================
# SLIDE 5 — GMV DELTA
# =============================================================
with tabs[4]:
    walmart_header("GMV Delta Among Active Sellers → –$1.65M")

    merged = df_feb.merge(df_oct, on="seller_id", how="inner", suffixes=("_feb", "_oct"))
    merged["gmv_change"] = merged["gmv_oct"] - merged["gmv_feb"]

    st.markdown("### GMV Change Among Overlapping Sellers")
    st.dataframe(
        merged[["slr_org_nm_feb", "gmv_feb", "gmv_oct", "gmv_change"]]
        .sort_values("gmv_change")
        .head(10)
    )

    total_drag = merged["gmv_change"].sum()
    st.metric("Total GMV Change (Feb–Nov → Oct–Nov)", f"{total_drag:,.0f}")

    fig = px.bar(
        merged.sort_values("gmv_change").head(20),
        x="slr_org_nm_feb",
        y="gmv_change",
        title="Top 20 GMV Declines",
        color="gmv_change",
        color_continuous_scale="Bluered"
    )
    st.plotly_chart(fig, use_container_width=True)

# =============================================================
# SLIDE 6 — STRATEGIC IMPORTANCE
# =============================================================
with tabs[5]:
    walmart_header("Why This Matters: WSR Can Scale to $1B+ If Attribution Is Fixed")

    st.markdown("""
    ### WSR is structurally similar to Amazon Brand Referral Bonus
    - Sellers use Google Ads, Meta, TikTok  
    - They need transparent, multi-touch attribution  
    - Amazon invests heavily in measurement → **$10B+ channel**  

    ### WSR’s measurement layer is affiliate-legacy  
    - Short windows  
    - Last-touch only  
    - No cross-channel reconciliation  
    - No first-touch / multi-touch visibility  

    ### Fixing attribution = unlocking the flywheel
    - Better trust  
    - More seller spend  
    - More solution provider adoption  
    - More GMV  
    """)

# =============================================================
# SLIDE 7 — TEST PROGRAM
# =============================================================
with tabs[6]:
    walmart_header("FY27 Attribution Test Program (Proposed)")

    st.markdown("""
    ### Test 1 — First-Touch vs Last-Touch (Google + Meta)
    - Quantify conversion undercounting  
    - Validate new multi-touch model  
    - Build transparent rule set  

    ### Test 2 — WSR vs Amazon Brand Referral Bonus
    - Match creatives, budget, targeting  
    - Compare true incremental ROI  
    - Identify gaps in attribution design  

    ### Output  
    - Clear attribution model (windows, touch rules)  
    - Better reporting for sellers & partners  
    - Foundation for API-grade measurement  
    """)

# =============================================================
# SLIDE 8 — DECISION
# =============================================================
with tabs[7]:
    walmart_header("Leadership Decision Required")

    st.markdown("""
    ## Do we allocate FY27 budget to run the attribution modernization tests?

    ### What approval unlocks:
    - Run cross-channel tests (Google, Meta, Amazon baseline)
    - Build measurement sandbox + test accounts
    - Update attribution rules
    - Deliver FY27 roadmap for attribution + WSR API

    ### Potential FY27 GMV Unlock  
    **+$8–$12M incremental GMV** → pathway to **$1B+** over time.
    """)

    st.success("Awaiting leadership decision.")

