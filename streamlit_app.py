import streamlit as st
import pandas as pd
import altair as alt

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Walmart Sales Rewards – Attribution Test Program",
    layout="wide"
)

# ---------------------------------------------------
# CORE DATA (STATIC, FROM YOUR ANALYSIS)
# ---------------------------------------------------

# High-level WSR metrics
WSR_YTD_GMV = 6_500_000
WSR_YTD_BUYERS = 200_000
WSR_YTD_ROI = 18  # x
WSR_NOV_GMV = 920_000
WSR_NOV_PAYOUT = 50_000

# Attrition summary
ATTRITION_TOTAL_LOST_GMV = 2_450_000
ATTRITION_SELLERS_FEB_NOV = 295
ATTRITION_SELLERS_OCT_NOV = 149
ATTRITION_SELLERS_LOST = 145

# GMV delta among active sellers
GMV_DELTA_ACTIVE = -1_650_000
TOTAL_GMV_DRAG = ATTRITION_TOTAL_LOST_GMV + GMV_DELTA_ACTIVE  # ≈ -4.1M

# Example lost sellers (from your files)
attrition_examples = pd.DataFrame(
    [
        ["XIUXIAN TRADE CO LTD", 1_850_000, 0, 1_850_000],
        ["shenzhenshixinmiaodianzi…", 467_000, 0, 467_000],
        ["pcplanet", 41_000, 0, 41_000],
    ],
    columns=["Seller", "GMV Feb–Nov", "GMV Oct–Nov", "GMV Lost"]
)

# Efficiency anomalies – Pattern A: high clicks, low GMV/click
efficiency_high_clicks = pd.DataFrame(
    [
        ["Bernie’s Best, Inc", 16_247, 36_132, 36_132 / 16_247],
        ["SOFT INC.", 15_239, 25_639, 25_639 / 15_239],
        ["Organixx (Epigenetic Labs)", 22_718, 284, 284 / 22_718],
    ],
    columns=["Seller", "Clicks", "GMV", "GMV per Click"]
)

# Efficiency anomalies – Pattern B: low clicks, very high GMV/click
efficiency_low_clicks = pd.DataFrame(
    [
        ["shenzhenshixinmiaodianziyouxiangongsi", 2_712, 466_928, 466_928 / 2_712],
        ["zhangzhoushijingqumaoyiyouxiangongsi", 2_615, 386_173, 386_173 / 2_615],
        ["Hangzhou Longhui Trading Co. Ltd", 2_038, 329_113, 329_113 / 2_038],
    ],
    columns=["Seller", "Clicks", "GMV", "GMV per Click"]
)

# GMV Delta examples among active sellers
gmv_delta_examples = pd.DataFrame(
    [
        ["Electronics Seller A", 300_000, 80_000, 80_000 - 300_000],
        ["Cosmetics Seller B", 180_000, 62_000, 62_000 - 180_000],
        ["Home Fitness Pro", 220_000, 136_000, 136_000 - 220_000],
    ],
    columns=["Seller", "GMV Feb–Nov", "GMV Oct–Nov", "Δ GMV"]
)
gmv_delta_examples["Δ %"] = (
    gmv_delta_examples["Δ GMV"] / gmv_delta_examples["GMV Feb–Nov"] * 100
).round(1)

# Combined GMV drag summary
gmv_drag_summary = pd.DataFrame(
    [
        ["Lost sellers (churn)", -ATTRITION_TOTAL_LOST_GMV],
        ["Declining active sellers", GMV_DELTA_ACTIVE],
    ],
    columns=["Component", "GMV Impact"]
)


# ---------------------------------------------------
# HELPER: SIMPLE WALMART-LIKE METRIC CARD ROW
# ---------------------------------------------------
def metric_row():
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("YTD WSR GMV", f"${WSR_YTD_GMV:,.0f}")
    col2.metric("YTD Incremental Buyers", f"{WSR_YTD_BUYERS:,.0f}")
    col3.metric("YTD ROI (GMV / Payout)", f"{WSR_YTD_ROI}×")
    col4.metric("Nov GMV / Payout", f"${WSR_NOV_GMV:,.0f} / ${WSR_NOV_PAYOUT:,.0f}")


# ---------------------------------------------------
# TABS = SLIDES
# ---------------------------------------------------
tabs = st.tabs([
    "Slide 1 – Title",
    "Slide 2 – TL;DR",
    "Slide 3 – Attrition",
    "Slide 4 – Efficiency",
    "Slide 5 – GMV Delta",
    "Slide 6 – Strategic Why",
    "Slide 7 – Test Program",
    "Slide 8 – Decision"
])

# ---------------------------------------------------
# SLIDE 1 — TITLE
# ---------------------------------------------------
with tabs[0]:
    st.title("Walmart Sales Rewards (WSR): FY27 Attribution Test Program")
    st.subheader("Aligning on measurement to unlock a +$1B GMV opportunity")

    metric_row()

    st.markdown(
        """
        **Objective**

        Align leadership on investing in a **cross-provider attribution test program** to:

        - Restore seller and solution-provider confidence  
        - Recover GMV currently lost to attribution noise  
        - Build the measurement foundation for WSR to scale to **$1B+ GMV**
        """
    )

# ---------------------------------------------------
# SLIDE 2 — TL;DR / WHY NOW
# ---------------------------------------------------
with tabs[1]:
    st.header("TL;DR — WSR is Working Too Well for Us to Be This Blind")

    metric_row()

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown(
            f"""
            - **YTD GMV:** ~${WSR_YTD_GMV:,.0f}  
            - **Incremental buyers:** ~{WSR_YTD_BUYERS:,.0f}  
            - **Program ROI:** ~{WSR_YTD_ROI}×  
            - **Example:** In **November**, WSR generated **${WSR_NOV_GMV:,.0f} GMV** on **${WSR_NOV_PAYOUT:,.0f} payouts** (~18× ROI).  

            WSR traffic is:
            - High-intent (Google Ads, Meta campaigns, etc.)  
            - Incremental vs broader affiliate (closer to **Amazon Brand Referral Bonus** than to coupon sites)  

            **But attribution quality is now the #1 barrier to scaling WSR.**
            """
        )

    with col_right:
        summary = pd.DataFrame(
            {
                "Metric": ["Lost GMV from churn", "GMV delta (active)", "Total GMV drag (sample)"],
                "Value": [
                    -ATTRITION_TOTAL_LOST_GMV,
                    GMV_DELTA_ACTIVE,
                    TOTAL_GMV_DRAG
                ],
            }
        )
        summary_chart = alt.Chart(summary).mark_bar().encode(
            x=alt.X("Metric:N", sort=None),
            y=alt.Y("Value:Q", title="GMV Impact ($)"),
            color=alt.value("#0071CE")
        )
        st.altair_chart(summary_chart, use_container_width=True)
        st.caption("GMV drag from seller churn + performance declines in the analyzed top-seller cohort (~$4.1M).")

    st.markdown(
        """
        **Leadership need:**  
        Fund a focused **FY27 attribution test program** to validate and modernize WSR measurement.
        """
    )

# ---------------------------------------------------
# SLIDE 3 — ATTRITION
# ---------------------------------------------------
with tabs[2]:
    st.header("Seller Attrition — $2.45M GMV at Risk")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sellers Feb–Nov", f"{ATTRITION_SELLERS_FEB_NOV}")
    col2.metric("Active Oct–Nov", f"{ATTRITION_SELLERS_OCT_NOV}")
    col3.metric("Churned Sellers", f"{ATTRITION_SELLERS_LOST}")
    col4.metric("GMV Lost from Churn", f"-${ATTRITION_TOTAL_LOST_GMV:,.0f}")

    st.subheader("Example Churned Sellers (from dataset)")
    st.dataframe(attrition_examples.style.format({"GMV Feb–Nov": "${:,.0f}", "GMV Oct–Nov": "${:,.0f}", "GMV Lost": "${:,.0f}"}))

    attrition_chart = alt.Chart(attrition_examples).mark_bar().encode(
        x=alt.X("Seller:N", sort="-y"),
        y=alt.Y("GMV Lost:Q", title="GMV Lost ($)"),
        color=alt.value("#0071CE")
    )
    st.altair_chart(attrition_chart, use_container_width=True)

    st.markdown(
        """
        **Key Takeaways**

        - ~145 sellers churned (GMV → 0) between Feb–Nov and Oct–Nov.  
        - These sellers represent **~$2.45M GMV** that disappeared in Oct–Nov.  
        - Seller feedback is consistent:  
          > “Attribution is undercounting conversions.”  
          > “We can’t reconcile Walmart-reported conversions with our analytics.”  
        """
    )

# ---------------------------------------------------
# SLIDE 4 — EFFICIENCY
# ---------------------------------------------------
with tabs[3]:
    st.header("Efficiency Anomalies — Attribution Misalignment Signals")

    st.subheader("Pattern A — High Clicks, Low GMV per Click (Missing Conversions)")
    st.dataframe(efficiency_high_clicks.style.format({"Clicks": "{:,.0f}", "GMV": "${:,.0f}", "GMV per Click": "${:,.2f}"}))

    chart_a = alt.Chart(efficiency_high_clicks).mark_circle(size=120).encode(
        x=alt.X("Clicks:Q"),
        y=alt.Y("GMV per Click:Q", title="GMV per Click ($)"),
        tooltip=["Seller", "Clicks", "GMV", "GMV per Click"],
        color=alt.value("#0071CE")
    )
    st.altair_chart(chart_a, use_container_width=True)

    st.markdown(
        """
        These GMV-per-click values ($0.01–$2.22) are **far below** expected category ranges (~$18–$26),  
        suggesting conversions are happening but **not being attributed correctly.**
        """
    )

    st.subheader("Pattern B — Low Clicks, Very High GMV per Click (Missing Clicks)")
    st.dataframe(efficiency_low_clicks.style.format({"Clicks": "{:,.0f}", "GMV": "${:,.0f}", "GMV per Click": "${:,.2f}"}))

    chart_b = alt.Chart(efficiency_low_clicks).mark_circle(size=120).encode(
        x=alt.X("Clicks:Q"),
        y=alt.Y("GMV per Click:Q", title="GMV per Click ($)"),
        tooltip=["Seller", "Clicks", "GMV", "GMV per Click"],
        color=alt.value("#FFC220")  # Walmart yellow-ish
    )
    st.altair_chart(chart_b, use_container_width=True)

    st.markdown(
        """
        GMV-per-click values of $148–$172 are **not realistic** for normal affiliate behavior.  
        They point to **lost click IDs** or conversions grouped incorrectly under too few clicks.

        Taken together, Pattern A + Pattern B indicate **attribution plumbing issues**,  
        not actual shopper behavior.
        """
    )

# ---------------------------------------------------
# SLIDE 5 — GMV DELTA
# ---------------------------------------------------
with tabs[4]:
    st.header("GMV Delta Among Active Sellers — –$1.65M")

    st.metric("GMV Change (Active Sellers)", f"-${abs(GMV_DELTA_ACTIVE):,.0f}")

    st.subheader("Examples from Active Sellers")
    st.dataframe(
        gmv_delta_examples.style.format(
            {
                "GMV Feb–Nov": "${:,.0f}",
                "GMV Oct–Nov": "${:,.0f}",
                "Δ GMV": "${:,.0f}",
                "Δ %": "{:,.1f}%"
            }
        )
    )

    delta_chart = alt.Chart(gmv_delta_examples).mark_bar().encode(
        x=alt.X("Seller:N", sort="-y"),
        y=alt.Y("Δ GMV:Q", title="Change in GMV ($)"),
        color=alt.condition(
            alt.datum["Δ GMV"] < 0,
            alt.value("#D0342C"),  # red for decline
            alt.value("#0071CE")
        ),
        tooltip=["Seller", "GMV Feb–Nov", "GMV Oct–Nov", "Δ GMV", "Δ %"]
    )
    st.altair_chart(delta_chart, use_container_width=True)

    st.subheader("Combined GMV Drag in the Analyzed Cohort")
    st.dataframe(gmv_drag_summary.style.format({"GMV Impact": "${:,.0f}"}))

    drag_chart = alt.Chart(gmv_drag_summary).mark_bar().encode(
        x=alt.X("Component:N", sort=None),
        y=alt.Y("GMV Impact:Q", title="GMV Impact ($)"),
        color=alt.value("#0071CE")
    )
    st.altair_chart(drag_chart, use_container_width=True)

    st.markdown(
        f"""
        - GMV decline among active sellers: **-${abs(GMV_DELTA_ACTIVE):,.0f}**  
        - Combined with churn, this sample shows **~${abs(TOTAL_GMV_DRAG):,.0f} GMV drag**.  
        - Many of the steepest declines are among solution-provider–managed sellers,  
          who have explicitly cited **tracking and reconciliation issues** as the reason for pulling back spend.
        """
    )

# ---------------------------------------------------
# SLIDE 6 — STRATEGIC WHY
# ---------------------------------------------------
with tabs[5]:
    st.header("Why This Matters Strategically")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            **WSR today**

            - High-ROI program (~18×) with **$1B+ GMV potential**  
            - Sends **high-intent, incremental traffic** (paid media, influencers, solution providers)  
            - Functionally resembles **Amazon Attribution / Brand Referral Bonus**, not coupon-style affiliates  

            **Amazon’s path**

            - Separated attribution from Amazon Associates  
            - Built **API-grade measurement** for Brand Referral  
            - Turned it into a **$10B+ performance channel**  
            """
        )

    with col2:
        st.markdown(
            """
            **WSR’s current measurement stack**

            - Affiliate-legacy rules (short windows, last-touch only)  
            - No systematic first-touch vs last-touch testing across Google/Meta  
            - Event capture & tagging not aligned with modern performance marketing  

            **Implication**

            - Attribution is now **the gating factor**, not demand or ROI.  
            - Fixing attribution is how we:
                - Unlock higher seller and provider spend  
                - Justify WSR vs Amazon in seller boardrooms  
                - Scale WSR into Walmart’s flagship performance-marketing rail
            """
        )

# ---------------------------------------------------
# SLIDE 7 — TEST PROGRAM
# ---------------------------------------------------
with tabs[6]:
    st.header("FY27 Attribution Test Program — What We Need to Run")

    st.subheader("Goal")
    st.markdown(
        """
        Establish **trustworthy, cross-channel measurement** for WSR so sellers and solution providers  
        can confidently scale spend.
        """
    )

    st.subheader("Proposed FY27 Tests")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            ### 1️⃣ First-Touch vs Last-Touch (Google + Meta)

            - Run **side-by-side measurement** on a set of WSR campaigns  
            - Compare:
                - Current **last-touch** logic  
                - Alternate **first-touch / multi-touch** models  
            - Quantify:
                - Degree of **conversion undercounting**  
                - Impact on ROI perception and spend levels  

            **Outcome:**  
            - A transparent, seller-readable attribution rule set that reflects real performance.
            """
        )

    with col2:
        st.markdown(
            """
            ### 2️⃣ WSR vs Amazon Brand Referral Benchmark

            - Select overlapping sellers running:
                - **WSR campaigns → Walmart.com**  
                - **Brand Referral Bonus campaigns → Amazon**  
            - Hold budgets, creatives, and targeting as constant as possible  
            - Compare:
                - GMV  
                - ROI  
                - Measured conversions under harmonized rules  

            **Outcome:**  
            - Clarity on:
                - True **incremental ROI** of WSR  
                - Where our attribution needs to evolve to meet or beat Amazon’s bar
            """
        )

    st.subheader("Expected Impact")
    st.markdown(
        """
        - Recover a meaningful share of the **~$4.1M GMV drag** identified in the sample  
        - Build the measurement foundation for:
            - WSR **API scale** (campaign + product reporting)  
            - Deeper integration with solution providers  
        - Unlock an estimated **+$8–$12M incremental GMV in FY27**,  
          and set the trajectory toward **$1B+ GMV** at scale.
        """
    )

# ---------------------------------------------------
# SLIDE 8 — DECISION
# ---------------------------------------------------
with tabs[7]:
    st.header("Decision Required from Leadership")

    st.markdown(
        """
        ### Ask

        Do you agree that Walmart should **assign dedicated FY27 budget**  
        to run the attribution test program described here?

        If **Yes**, we will:

        1. Stand up an attribution **test sandbox** and accounts across providers (Google, Meta, Amazon baseline)  
        2. Execute:
            - **First-touch vs Last-touch tests**  
            - **WSR vs Amazon Brand Referral** comparison  
        3. Update WSR attribution rules based on observed performance  
        4. Deliver an FY27 roadmap for:
            - WSR **measurement**  
            - WSR **API-grade reporting**  
            - Seller- and provider-facing transparency  
        """
    )

    st.subheader("What Success Looks Like")
    st.markdown(
        """
        - Sellers and solution providers report **confidence** in WSR reporting  
        - GMV drag from attrition and mis-measurement is **materially reduced**  
        - WSR becomes Walmart’s **flagship performance rail** for offsite traffic,  
          positioned credibly against Amazon’s Brand Referral program.
        """
    )

    st.success("Once leadership aligns, this app can be reused as a live narrative tracker for test design, execution, and results.")
