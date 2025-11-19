import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Walmart Sales Rewards - FY27 Attribution Test Program",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Walmart branding
st.markdown("""
    <style>
    .main {
        background-color: #ffffff;
    }
    h1, h2, h3 {
        color: #0071CE;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 4px 4px 0 0;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0071CE;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📊 Title", 
    "🎯 TL;DR", 
    "⚠️ Seller Attrition", 
    "📉 Efficiency Signals",
    "📊 GMV Decline",
    "🎯 Strategic Importance",
    "🔬 Test Program",
    "✅ Decision Required"
])

# ============================================================================
# TAB 1 - TITLE SLIDE
# ============================================================================
with tab1:
    st.title("Walmart Sales Rewards (WSR): FY27 Attribution Test Program")
    
    st.markdown("### Objective")
    st.markdown("""
    - **Align leadership** on investing in a cross-provider attribution test program
    - **Restore seller confidence** in WSR measurement
    - **Unlock stalled GMV** and scale toward a $1B+ GMV program
    """)
    
    st.markdown("---")
    st.markdown("### Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("YTD WSR GMV", "$6.5M")
    with col2:
        st.metric("Incremental Buyers", "200K")
    with col3:
        st.metric("ROI", "~18x")
    with col4:
        st.metric("November GMV vs Payouts", "$920K vs $50K")

# ============================================================================
# TAB 2 - TL;DR / WHY NOW
# ============================================================================
with tab2:
    st.header("TL;DR — WSR is High-ROI but Held Back by Attribution")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Key Highlights")
        st.markdown("""
        - **YTD WSR GMV:** ~$6.5M
        - **Incremental buyers:** 200K
        - **ROI:** ~18x (example: $920K GMV in November vs $50K payouts)
        - Traffic is **high-intent**, often from Google Ads / Meta, similar to Amazon Brand Referral Bonus (~$10B+)
        - **BUT:** Attribution quality is now the **#1 barrier** to scaling WSR
        """)
        
        st.markdown("---")
        st.info("**Leadership need:** Fund attribution tests to validate and modernize WSR measurement.")
    
    with col2:
        st.markdown("### GMV Drag Components")
        
        drag_data = pd.DataFrame({
            'Component': ['Lost GMV from Churn', 'GMV Decline (Active Sellers)', 'Total GMV Drag'],
            'GMV Impact ($M)': [-2.45, -1.65, -4.1]
        })
        
        fig = px.bar(drag_data, x='Component', y='GMV Impact ($M)', 
                     color='GMV Impact ($M)',
                     color_continuous_scale=['#DC143C', '#FF6347', '#FFA07A'])
        fig.update_layout(showlegend=False, height=400)
        fig.update_traces(marker_line_color='#0071CE', marker_line_width=2)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 3 - SELLER ATTRITION
# ============================================================================
with tab3:
    st.header("Problem: Attribution Is Creating GMV Drag")
    st.subheader("Seller Attrition → –$2.45M GMV Lost")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Sellers Feb–Nov", "295")
    with col2:
        st.metric("Sellers Active Oct–Nov", "149")
    with col3:
        st.metric("Churned Sellers", "145", delta="-49%", delta_color="inverse")
    with col4:
        st.metric("GMV Lost from Churn", "–$2.45M", delta_color="inverse")
    
    st.markdown("---")
    st.markdown("### Sample Lost Sellers")
    
    lost_sellers_data = pd.DataFrame({
        'Seller': ['XIUXIAN TRADE CO LTD', 'shenzhenshixinmiaodianzi...', 'pcplanet'],
        'GMV Feb–Nov': [1850000, 467000, 41000],
        'GMV Oct–Nov': [0, 0, 0],
        'GMV Lost': [1850000, 467000, 41000]
    })
    
    # Format as currency
    styled_df = lost_sellers_data.copy()
    for col in ['GMV Feb–Nov', 'GMV Oct–Nov', 'GMV Lost']:
        styled_df[col] = styled_df[col].apply(lambda x: f"${x:,.0f}")
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    # Bar chart
    fig = px.bar(lost_sellers_data, x='Seller', y='GMV Lost',
                 color='GMV Lost', color_continuous_scale='Reds')
    fig.update_layout(showlegend=False, height=400, title="GMV Lost by Churned Sellers")
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### Key Findings")
    st.markdown("""
    - **~145 sellers** dropped to zero GMV between Feb–Nov and Oct–Nov
    - These "lost" sellers represent **$2.45M in GMV** disappearing in Oct–Nov
    - **Qualitative feedback** from sellers:
        - *"Attribution is undercounting conversions"*
        - *"We can't reconcile Walmart-reported conversions with our own analytics"*
    """)

# ============================================================================
# TAB 4 - EFFICIENCY SIGNALS
# ============================================================================
with tab4:
    st.header("Problem: Efficiency Signals Show Attribution Misalignment")
    
    st.subheader("Pattern A — High Clicks, Low GMV per Click (Undercounting Conversions)")
    
    pattern_a_data = pd.DataFrame({
        'Seller': ["Bernie's Best, Inc", 'SOFT INC.', 'Organixx'],
        'Clicks': [16247, 15239, 22718],
        'GMV': [36132, 25639, 284],
        'GMV per Click': [2.22, 1.68, 0.01]
    })
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        styled_a = pattern_a_data.copy()
        styled_a['Clicks'] = styled_a['Clicks'].apply(lambda x: f"{x:,}")
        styled_a['GMV'] = styled_a['GMV'].apply(lambda x: f"${x:,.0f}")
        styled_a['GMV per Click'] = styled_a['GMV per Click'].apply(lambda x: f"${x:.2f}")
        st.dataframe(styled_a, use_container_width=True, hide_index=True)
    
    with col2:
        fig = px.bar(pattern_a_data, x='Seller', y='GMV per Click',
                     color='GMV per Click', color_continuous_scale='Blues')
        fig.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    st.warning("**GMV per click ($0.01–$2.22)** is far below expected ranges (~$18–$26), suggesting conversions are happening but not being attributed.")
    
    st.markdown("---")
    st.subheader("Pattern B — Low Clicks, High GMV per Click (Undercounting Clicks)")
    
    pattern_b_data = pd.DataFrame({
        'Seller': ['shenzhenshixinmiaodianzi...', 'zhangzhoushijingqumaoyi...', 'Hangzhou Longhui'],
        'Clicks': [2712, 2615, 2038],
        'GMV': [466928, 386173, 329113],
        'GMV per Click': [172, 148, 161]
    })
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        styled_b = pattern_b_data.copy()
        styled_b['Clicks'] = styled_b['Clicks'].apply(lambda x: f"{x:,}")
        styled_b['GMV'] = styled_b['GMV'].apply(lambda x: f"${x:,.0f}")
        styled_b['GMV per Click'] = styled_b['GMV per Click'].apply(lambda x: f"${x:.0f}")
        st.dataframe(styled_b, use_container_width=True, hide_index=True)
    
    with col2:
        fig = px.bar(pattern_b_data, x='Seller', y='GMV per Click',
                     color='GMV per Click', color_continuous_scale='Oranges')
        fig.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    st.warning("**GMV per click values ($148–$172)** are unrealistically high, pointing to missing clicks or mis-grouped conversions.")
    
    st.markdown("---")
    st.error("""
    **Conclusion:** Neither pattern matches normal affiliate performance. Both are consistent with attribution plumbing issues 
    (lost events, mis-tagged clicks, last-touch quirks), not actual shopper behavior.
    """)

# ============================================================================
# TAB 5 - GMV DECLINE AMONG ACTIVE SELLERS
# ============================================================================
with tab5:
    st.header("Problem: GMV Delta Among Active Sellers")
    st.subheader("GMV Decline Among Active Sellers — –$1.65M")
    
    col1, col2, col3 = st.columns(3)
    with col2:
        st.metric("GMV Change (Active Sellers)", "–$1.65M", delta_color="inverse")
    
    st.markdown("---")
    st.markdown("### Sample Active Sellers with Declining GMV")
    
    declining_data = pd.DataFrame({
        'Seller': ['Electronics Seller', 'Home Category Seller'],
        'GMV Feb–Nov': [300000, 220000],
        'GMV Oct–Nov': [80000, 136000],
        'Δ GMV': [-220000, -84000],
        'Δ %': [-73, -38]
    })
    
    styled_declining = declining_data.copy()
    styled_declining['GMV Feb–Nov'] = styled_declining['GMV Feb–Nov'].apply(lambda x: f"${x:,.0f}")
    styled_declining['GMV Oct–Nov'] = styled_declining['GMV Oct–Nov'].apply(lambda x: f"${x:,.0f}")
    styled_declining['Δ GMV'] = styled_declining['Δ GMV'].apply(lambda x: f"${x:,.0f}")
    styled_declining['Δ %'] = styled_declining['Δ %'].apply(lambda x: f"{x}%")
    
    st.dataframe(styled_declining, use_container_width=True, hide_index=True)
    
    # Bar chart of decline
    fig = px.bar(declining_data, x='Seller', y='Δ GMV',
                 color='Δ GMV', color_continuous_scale='Reds')
    fig.update_layout(showlegend=False, height=350, title="GMV Change by Seller")
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### Total GMV Drag Summary")
    
    drag_summary = pd.DataFrame({
        'Component': ['Lost Sellers (Churn)', 'Declining Active Sellers', 'Total GMV Drag'],
        'Impact': ['–$2.45M', '–$1.65M', '–$4.1M']
    })
    
    st.dataframe(drag_summary, use_container_width=True, hide_index=True)
    
    st.error("""
    **Combined**, churn + active-seller declines represent **~$4.1M GMV drag** in this sample, 
    much of it correlated with tracking and reconciliation concerns.
    """)

# ============================================================================
# TAB 6 - STRATEGIC IMPORTANCE
# ============================================================================
with tab6:
    st.header("Why Attribution Is Now Strategic for WSR")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Current State")
        st.markdown("""
        - WSR is already a **high-ROI performance program** with **$1B+ GMV potential**
        - WSR behaves more like **Amazon Attribution / Brand Referral Bonus (~$10B+)** than a classic coupon affiliate program
        - Sellers drive traffic from **Google Ads, Meta, TikTok, solution providers**, and expect transparent, reliable reporting
        """)
    
    with col2:
        st.markdown("### The Opportunity")
        st.markdown("""
        - **Amazon scaled Brand Referral** once measurement became API-grade and trustworthy
        - Today, WSR still relies on **affiliate-legacy rules:**
            - Short windows
            - Last-touch-only attribution
            - No systematized multi-touch testing
        """)
    
    st.markdown("---")
    st.markdown("### The WSR Flywheel")
    
    st.info("""
    **Fixing attribution unlocks the WSR flywheel:**
    
    1. **Better measurement** → Higher seller confidence & spend
    2. **More solution-provider integrations** → Richer performance data
    3. **Better optimization** → Higher ROI → More spend
    4. **GMV scales non-linearly** toward $1B+ target
    """)
    
    # Visual flywheel representation
    flywheel_metrics = pd.DataFrame({
        'Stage': ['Better Measurement', 'Provider Integrations', 'Optimization', 'Scale'],
        'Impact': [25, 50, 75, 100]
    })
    
    fig = go.Figure(data=[go.Bar(
        x=flywheel_metrics['Stage'],
        y=flywheel_metrics['Impact'],
        marker_color=['#0071CE', '#FFC220', '#0071CE', '#FFC220']
    )])
    fig.update_layout(
        title="WSR Growth Potential Through Attribution",
        yaxis_title="Relative Impact",
        height=300,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 7 - TEST PROGRAM
# ============================================================================
with tab7:
    st.header("FY27 Attribution Test Program — What We Need to Run")
    
    st.markdown("### Goal")
    st.success("**Establish trustworthy measurement** for WSR across channels and providers")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 1️⃣ First-Touch vs Last-Touch Test")
        st.markdown("**Channels:** Google + Meta")
        st.markdown("""
        **Approach:**
        - Compare current last-touch model against first-touch / multi-touch on matched campaigns
        - Quantify conversion undercounting in current setup
        
        **Output:**
        - Transparent, improved attribution rule set (window, touch model, event handling)
        """)
    
    with col2:
        st.markdown("### 2️⃣ WSR vs Amazon Brand Referral Bonus Test")
        st.markdown("**Benchmark:** Amazon BRB")
        st.markdown("""
        **Approach:**
        - Run matched campaigns with:
            - Balanced budget
            - Matched creatives
            - Similar targeting
        
        **Output:**
        - True incremental ROI of WSR
        - Where our measurement must evolve to meet/beat Amazon
        """)
    
    st.markdown("---")
    st.markdown("### Test Program Summary")
    
    test_summary = pd.DataFrame({
        'Test': ['First-Touch vs Last-Touch', 'WSR vs Amazon BRB'],
        'Channel': ['Google & Meta', 'WSR vs Amazon'],
        'Objective': ['Quantify under-attribution', 'Benchmark ROI'],
        'Key Output': ['New attribution rule set', 'Positioning & roadmap']
    })
    
    st.dataframe(test_summary, use_container_width=True, hide_index=True)

# ============================================================================
# TAB 8 - DECISION REQUIRED
# ============================================================================
with tab8:
    st.header("Decision Required — Fund WSR Attribution Testing in FY27")
    
    st.markdown("---")
    st.markdown("### Key Question")
    st.info("""
    ## Do you agree that Walmart should assign FY27 budget to run the attribution test program described above?
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### If YES → Actions Required")
        st.markdown("""
        1. **Execute cross-channel tests** (Google, Meta, with Amazon as benchmark)
        2. **Build a measurement sandbox** + test accounts
        3. **Update attribution rules** based on test results
        4. **Deliver an FY27 roadmap** for:
            - WSR measurement
            - API-grade reporting
            - Seller/solution-provider transparency
        """)
    
    with col2:
        st.markdown("### Expected Impact")
        st.success("""
        ### Unlock Potential:
        
        **+$8–$12M** incremental GMV in FY27 from improved attribution alone
        
        Clear path toward **$1B+ WSR GMV** at scale
        """)
    
    st.markdown("---")
    
    # Impact visualization
    impact_data = pd.DataFrame({
        'Scenario': ['Current State (YTD)', 'FY27 with Attribution Fix', 'Scale Potential'],
        'GMV ($M)': [6.5, 18.5, 1000]
    })
    
    fig = px.bar(impact_data, x='Scenario', y='GMV ($M)',
                 color='GMV ($M)', 
                 color_continuous_scale=[[0, '#DC143C'], [0.5, '#FFC220'], [1, '#0071CE']])
    fig.update_layout(
        title="WSR GMV Growth Trajectory",
        height=400,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.balloons()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <small>Walmart Sales Rewards (WSR) — FY27 Attribution Test Program | Confidential</small>
</div>
""", unsafe_allow_html=True)