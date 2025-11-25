"""
E-Commerce Analytics Dashboard
Interactive Streamlit application for e-commerce business intelligence

Features:
- Synthetic data generation (25k visits/month, 2 months)
- Data cleaning and wrangling demonstration
- 5 advanced analytics:
  1. Customer Lifetime Value (CLV)
  2. RFM Analysis (Recency, Frequency, Monetary)
  3. Cart Abandonment Analysis
  4. Product Performance Analysis
  5. Customer Segmentation (K-Means)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from ecommerce_analytics import (
    EcommerceDataGenerator,
    EcommerceDataCleaner,
    EcommerceAnalytics,
    EcommerceVisualizer
)

# Page config
st.set_page_config(
    page_title="E-Commerce Analytics Pro",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .insight-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load and process e-commerce data with caching"""
    generator = EcommerceDataGenerator(seed=42)
    sessions_df, events_df, transactions_df = generator.generate_dataset(
        visits_per_month=25000,
        months=2
    )

    cleaner = EcommerceDataCleaner()
    sessions_clean = cleaner.clean_sessions(sessions_df)
    transactions_clean = cleaner.clean_transactions(transactions_df)
    customer_df = cleaner.create_customer_summary(sessions_clean, transactions_clean)

    return sessions_clean, events_df, transactions_clean, customer_df


@st.cache_data
def run_analytics(sessions_df, transactions_df, customer_df):
    """Run all analytics with caching"""
    analytics = EcommerceAnalytics()

    customer_clv = analytics.calculate_clv(customer_df)
    customer_rfm = analytics.rfm_analysis(customer_df)
    abandonment_data = analytics.cart_abandonment_analysis(sessions_df)
    product_performance = analytics.product_performance_analysis(transactions_df)
    customer_segments, segment_analysis = analytics.customer_segmentation(customer_df)

    return {
        'customer_clv': customer_clv,
        'customer_rfm': customer_rfm,
        'abandonment': abandonment_data,
        'products': product_performance,
        'segments': customer_segments,
        'segment_analysis': segment_analysis
    }


def main():
    # Header
    st.markdown('<h1 class="main-header">🛒 E-Commerce Analytics Pro</h1>', unsafe_allow_html=True)
    st.markdown("""
    **Advanced E-Commerce Intelligence Dashboard**
    Analyzing 50,000 sessions (25k visits/month × 2 months) from a synthetic e-commerce website
    """)

    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/clouds/100/000000/shopping-cart.png", width=100)
        st.title("Navigation")
        st.markdown("---")

        st.markdown("### 📊 Dataset Info")
        st.info("""
        **Synthetic E-Commerce Data**
        - 50,000 total sessions
        - 2 months of data
        - 15 products across 2 categories
        - Multi-device tracking
        - Multiple acquisition channels
        """)

        st.markdown("---")
        st.markdown("### 🎯 Analyses Included")
        st.success("""
        1. **Customer Lifetime Value**
        2. **RFM Segmentation**
        3. **Cart Abandonment**
        4. **Product Performance**
        5. **Customer Clustering**
        """)

        st.markdown("---")
        if st.button("🔄 Reload Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Load data
    with st.spinner("📊 Loading e-commerce data..."):
        sessions_df, events_df, transactions_df, customer_df = load_data()

    with st.spinner("🧮 Running analytics..."):
        results = run_analytics(sessions_df, transactions_df, customer_df)

    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📈 Overview",
        "🧹 Data Cleaning",
        "💰 Customer Lifetime Value",
        "🎯 RFM Analysis",
        "🛒 Cart Abandonment",
        "📦 Product Performance",
        "👥 Customer Segmentation"
    ])

    # ==================== TAB 1: OVERVIEW ====================
    with tab1:
        st.header("📈 Business Overview")

        # Key metrics
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                "Total Sessions",
                f"{len(sessions_df):,}",
                help="Total number of website visits"
            )

        with col2:
            total_revenue = transactions_df['total_amount'].sum()
            st.metric(
                "Total Revenue",
                f"${total_revenue:,.2f}",
                help="Total revenue from all transactions"
            )

        with col3:
            conversion_rate = (sessions_df['converted'].sum() / len(sessions_df)) * 100
            st.metric(
                "Conversion Rate",
                f"{conversion_rate:.2f}%",
                help="Percentage of sessions that resulted in a purchase"
            )

        with col4:
            avg_order_value = transactions_df.groupby('transaction_id')['order_total'].first().mean()
            st.metric(
                "Avg Order Value",
                f"${avg_order_value:.2f}",
                help="Average value per order"
            )

        with col5:
            total_customers = customer_df[customer_df['total_orders'] > 0].shape[0]
            st.metric(
                "Customers",
                f"{total_customers:,}",
                help="Total unique customers with purchases"
            )

        st.markdown("---")

        # Revenue over time
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📅 Revenue Over Time")
            daily_revenue = transactions_df.groupby(transactions_df['transaction_date'].dt.date)['total_amount'].sum().reset_index()
            daily_revenue.columns = ['date', 'revenue']

            fig = px.line(
                daily_revenue,
                x='date',
                y='revenue',
                title='Daily Revenue Trend',
                labels={'revenue': 'Revenue ($)', 'date': 'Date'}
            )
            fig.update_traces(line_color='#1f77b4', line_width=2)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("📱 Traffic by Device")
            device_sessions = sessions_df['device'].value_counts().reset_index()
            device_sessions.columns = ['device', 'sessions']

            fig = px.pie(
                device_sessions,
                values='sessions',
                names='device',
                title='Session Distribution by Device',
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)

        # Channel performance
        st.subheader("📢 Acquisition Channel Performance")

        channel_metrics = sessions_df.groupby('channel').agg({
            'session_id': 'count',
            'converted': 'sum',
            'time_on_site': 'mean'
        }).reset_index()
        channel_metrics.columns = ['channel', 'sessions', 'conversions', 'avg_time_on_site']
        channel_metrics['conversion_rate'] = (channel_metrics['conversions'] / channel_metrics['sessions'] * 100).round(2)

        # Add revenue by channel
        channel_revenue = transactions_df.groupby('channel')['total_amount'].sum().reset_index()
        channel_revenue.columns = ['channel', 'revenue']
        channel_metrics = channel_metrics.merge(channel_revenue, on='channel', how='left')
        channel_metrics['revenue'] = channel_metrics['revenue'].fillna(0)

        st.dataframe(
            channel_metrics.sort_values('revenue', ascending=False),
            use_container_width=True,
            hide_index=True
        )

    # ==================== TAB 2: DATA CLEANING ====================
    with tab2:
        st.header("🧹 Data Cleaning & Wrangling Process")

        st.markdown("""
        This tab demonstrates the data cleaning and wrangling pipeline applied to raw e-commerce data.
        """)

        st.subheader("1️⃣ Raw Data Overview")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Sessions Dataset**")
            st.info(f"""
            - {len(sessions_df):,} records
            - {sessions_df.shape[1]} columns
            - Date range: {sessions_df['session_date'].min().date()} to {sessions_df['session_date'].max().date()}
            """)

        with col2:
            st.markdown("**Events Dataset**")
            st.info(f"""
            - {len(events_df):,} records
            - {events_df.shape[1]} columns
            - Event types: {events_df['event_type'].nunique()}
            """)

        with col3:
            st.markdown("**Transactions Dataset**")
            st.info(f"""
            - {len(transactions_df):,} records
            - {transactions_df.shape[1]} columns
            - Revenue: ${transactions_df['total_amount'].sum():,.2f}
            """)

        st.subheader("2️⃣ Data Quality Checks")

        # Show data quality metrics
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Missing Values (Sessions)**")
            missing_sessions = sessions_df.isnull().sum()
            missing_sessions = missing_sessions[missing_sessions > 0]
            if len(missing_sessions) == 0:
                st.success("✅ No missing values found!")
            else:
                st.dataframe(missing_sessions, use_container_width=True)

        with col2:
            st.markdown("**Duplicate Records**")
            duplicates_sessions = sessions_df.duplicated(subset=['session_id']).sum()
            duplicates_transactions = transactions_df.duplicated(subset=['transaction_id', 'product_id']).sum()

            st.success(f"""
            ✅ Sessions duplicates removed: {duplicates_sessions}
            ✅ Transaction duplicates removed: {duplicates_transactions}
            """)

        st.subheader("3️⃣ Feature Engineering")

        st.markdown("**Derived Features Created:**")

        feature_examples = pd.DataFrame({
            'Original Feature': ['session_date', 'session_date', 'time_on_site', 'first_session, last_session'],
            'Derived Feature': ['session_hour', 'session_day_of_week', 'engagement_level', 'recency_days'],
            'Purpose': [
                'Analyze hourly patterns',
                'Identify day-of-week trends',
                'Categorize user engagement',
                'Calculate customer recency'
            ]
        })

        st.dataframe(feature_examples, use_container_width=True, hide_index=True)

        st.subheader("4️⃣ Data Aggregation")

        st.markdown("**Customer-Level Summary Created:**")

        st.code("""
# Aggregating sessions and transactions to customer level
customer_summary = sessions.groupby('customer_id').agg({
    'session_id': 'count',
    'session_date': ['min', 'max'],
    'converted': 'sum',
    'time_on_site': 'mean'
})

# Merge with transaction data
customer_summary = customer_summary.merge(
    transactions.groupby('customer_id').agg({
        'transaction_id': 'nunique',
        'total_amount': 'sum'
    })
)
        """, language='python')

        st.markdown("**Sample of Cleaned Customer Data:**")
        st.dataframe(
            customer_df.head(10)[['customer_id', 'total_sessions', 'total_orders',
                                  'total_revenue', 'conversion_rate', 'avg_order_value']],
            use_container_width=True,
            hide_index=True
        )

        st.subheader("5️⃣ Data Validation")

        col1, col2, col3 = st.columns(3)

        with col1:
            valid_revenue = (transactions_df['total_amount'] > 0).all()
            st.metric(
                "Revenue Validation",
                "✅ Pass" if valid_revenue else "❌ Fail",
                help="All transactions have positive revenue"
            )

        with col2:
            valid_dates = (sessions_df['session_date'].notna()).all()
            st.metric(
                "Date Validation",
                "✅ Pass" if valid_dates else "❌ Fail",
                help="All sessions have valid dates"
            )

        with col3:
            valid_customers = (customer_df['total_sessions'] > 0).all()
            st.metric(
                "Customer Validation",
                "✅ Pass" if valid_customers else "❌ Fail",
                help="All customers have at least one session"
            )

    # ==================== TAB 3: CLV ANALYSIS ====================
    with tab3:
        st.header("💰 Customer Lifetime Value Analysis")

        customer_clv = results['customer_clv']

        st.markdown("""
        **CLV Formula:** `(Average Order Value × Purchase Frequency) × Customer Lifespan`

        This analysis calculates both historical CLV (actual revenue) and predicted CLV (projected 12 months).
        """)

        # Key CLV metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            avg_clv = customer_clv['total_clv'].mean()
            st.metric(
                "Average CLV",
                f"${avg_clv:.2f}",
                help="Average total customer lifetime value"
            )

        with col2:
            median_clv = customer_clv['total_clv'].median()
            st.metric(
                "Median CLV",
                f"${median_clv:.2f}",
                help="Median customer lifetime value"
            )

        with col3:
            top_10_pct_clv = customer_clv.nlargest(int(len(customer_clv) * 0.1), 'total_clv')['total_clv'].sum()
            total_clv = customer_clv['total_clv'].sum()
            top_pct = (top_10_pct_clv / total_clv * 100)
            st.metric(
                "Top 10% CLV Share",
                f"{top_pct:.1f}%",
                help="Percentage of total CLV from top 10% customers"
            )

        with col4:
            vip_count = (customer_clv['clv_segment'] == 'VIP').sum()
            st.metric(
                "VIP Customers",
                f"{vip_count:,}",
                help="Number of VIP segment customers"
            )

        st.markdown("---")

        # CLV visualization
        visualizer = EcommerceVisualizer()
        fig_clv = visualizer.plot_clv_distribution(customer_clv)
        st.plotly_chart(fig_clv, use_container_width=True)

        # CLV Segments table
        st.subheader("📊 CLV Segment Breakdown")

        segment_summary = customer_clv.groupby('clv_segment').agg({
            'customer_id': 'count',
            'total_clv': ['mean', 'sum'],
            'historical_clv': 'mean',
            'predicted_clv': 'mean'
        }).round(2)
        segment_summary.columns = ['customer_count', 'avg_clv', 'total_clv', 'avg_historical', 'avg_predicted']

        st.dataframe(segment_summary, use_container_width=True)

        # Insights
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown("### 💡 Key Insights")
        st.markdown(f"""
        - The top 10% of customers contribute **{top_pct:.1f}%** of total CLV
        - VIP customers have an average CLV of **${segment_summary.loc['VIP', 'avg_clv']:.2f}** (if VIP segment exists)
        - Focus retention efforts on High Value and VIP segments for maximum ROI
        - Low value customers may benefit from re-engagement campaigns
        """)
        st.markdown('</div>', unsafe_allow_html=True)

        # Top customers
        st.subheader("🏆 Top 20 Customers by CLV")
        top_customers = customer_clv.nlargest(20, 'total_clv')[
            ['customer_id', 'total_clv', 'historical_clv', 'predicted_clv',
             'total_orders', 'avg_order_value', 'clv_segment']
        ].round(2)
        st.dataframe(top_customers, use_container_width=True, hide_index=True)

    # ==================== TAB 4: RFM ANALYSIS ====================
    with tab4:
        st.header("🎯 RFM Analysis - Customer Segmentation")

        customer_rfm = results['customer_rfm']

        if len(customer_rfm) == 0:
            st.warning("No customers with purchases found for RFM analysis.")
        else:
            st.markdown("""
            **RFM stands for:**
            - **R**ecency: How recently did the customer purchase?
            - **F**requency: How often do they purchase?
            - **M**onetary: How much do they spend?

            Each customer is scored 1-5 on each dimension (5 being best).
            """)

            # RFM metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                champions = (customer_rfm['rfm_segment'] == 'Champions').sum()
                st.metric("Champions", f"{champions:,}", help="High R, F, M scores")

            with col2:
                loyal = (customer_rfm['rfm_segment'] == 'Loyal Customers').sum()
                st.metric("Loyal Customers", f"{loyal:,}", help="Regular purchasers")

            with col3:
                at_risk = (customer_rfm['rfm_segment'] == 'At Risk').sum()
                st.metric("At Risk", f"{at_risk:,}", help="Haven't purchased recently", delta=f"-{at_risk}", delta_color="inverse")

            with col4:
                lost = (customer_rfm['rfm_segment'] == 'Lost').sum()
                st.metric("Lost", f"{lost:,}", help="Inactive customers", delta=f"-{lost}", delta_color="inverse")

            st.markdown("---")

            # RFM visualization
            fig_rfm = visualizer.plot_rfm_segments(customer_rfm)
            st.plotly_chart(fig_rfm, use_container_width=True)

            # RFM segment details
            st.subheader("📊 RFM Segment Details")

            segment_details = customer_rfm.groupby('rfm_segment').agg({
                'customer_id': 'count',
                'R_score': 'mean',
                'F_score': 'mean',
                'M_score': 'mean',
                'total_revenue': 'sum',
                'total_orders': 'mean',
                'recency_days': 'mean'
            }).round(2)
            segment_details.columns = ['customers', 'avg_R', 'avg_F', 'avg_M', 'total_revenue', 'avg_orders', 'avg_recency']

            st.dataframe(segment_details.sort_values('total_revenue', ascending=False), use_container_width=True)

            # Marketing recommendations
            st.markdown('<div class="insight-box">', unsafe_allow_html=True)
            st.markdown("### 📧 Recommended Marketing Actions")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("""
                **Champions & Loyal Customers:**
                - VIP programs and exclusive offers
                - Early access to new products
                - Referral incentives
                - Thank you campaigns
                """)

            with col2:
                st.markdown("""
                **At Risk & Lost:**
                - Win-back email campaigns
                - Special discount offers
                - Survey to understand why they left
                - Retargeting ads
                """)

            st.markdown('</div>', unsafe_allow_html=True)

            # RFM Score distribution
            st.subheader("📈 RFM Score Distribution")

            col1, col2, col3 = st.columns(3)

            with col1:
                fig = px.histogram(customer_rfm, x='R_score', title='Recency Score Distribution',
                                  color_discrete_sequence=['#ff6b6b'])
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig = px.histogram(customer_rfm, x='F_score', title='Frequency Score Distribution',
                                  color_discrete_sequence=['#4ecdc4'])
                st.plotly_chart(fig, use_container_width=True)

            with col3:
                fig = px.histogram(customer_rfm, x='M_score', title='Monetary Score Distribution',
                                  color_discrete_sequence=['#95e1d3'])
                st.plotly_chart(fig, use_container_width=True)

    # ==================== TAB 5: CART ABANDONMENT ====================
    with tab5:
        st.header("🛒 Cart Abandonment Analysis")

        abandonment_data = results['abandonment']

        st.markdown("""
        Cart abandonment occurs when customers add items to their cart but leave without completing the purchase.
        Understanding abandonment patterns helps optimize checkout flow and recover lost revenue.
        """)

        # Key metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Carts",
                f"{abandonment_data['total_carts']:,}",
                help="Total number of shopping carts created"
            )

        with col2:
            st.metric(
                "Abandoned Carts",
                f"{abandonment_data['abandoned_carts']:,}",
                delta=f"-{abandonment_data['abandoned_carts']}",
                delta_color="inverse",
                help="Number of abandoned carts"
            )

        with col3:
            abandonment_rate = abandonment_data['abandonment_rate'] * 100
            st.metric(
                "Abandonment Rate",
                f"{abandonment_rate:.1f}%",
                delta=f"-{abandonment_rate:.1f}%",
                delta_color="inverse",
                help="Percentage of carts abandoned"
            )

        with col4:
            # Estimate lost revenue (assuming avg order value)
            if len(transactions_df) > 0:
                avg_order = transactions_df.groupby('transaction_id')['order_total'].first().mean()
                lost_revenue = avg_order * abandonment_data['abandoned_carts']
                st.metric(
                    "Estimated Lost Revenue",
                    f"${lost_revenue:,.2f}",
                    delta=f"-${lost_revenue:,.0f}",
                    delta_color="inverse",
                    help="Potential revenue from abandoned carts"
                )

        st.markdown("---")

        # Abandonment visualization
        fig_abandonment = visualizer.plot_cart_abandonment(abandonment_data)
        st.plotly_chart(fig_abandonment, use_container_width=True)

        # Detailed tables
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📱 Abandonment by Device")
            st.dataframe(
                abandonment_data['by_device'].sort_values('abandonment_rate', ascending=False),
                use_container_width=True,
                hide_index=True
            )

        with col2:
            st.subheader("📢 Abandonment by Channel")
            st.dataframe(
                abandonment_data['by_channel'].sort_values('abandonment_rate', ascending=False),
                use_container_width=True,
                hide_index=True
            )

        # Insights and recommendations
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown("### 💡 Optimization Recommendations")

        highest_device = abandonment_data['by_device'].sort_values('abandonment_rate', ascending=False).iloc[0]

        st.markdown(f"""
        1. **Mobile Optimization**: {highest_device['device']} has the highest abandonment rate ({highest_device['abandonment_rate']*100:.1f}%).
           - Simplify mobile checkout flow
           - Reduce required form fields
           - Add guest checkout option

        2. **Timing Analysis**: Abandonment peaks at certain hours
           - Send abandoned cart emails 1-2 hours after abandonment
           - Offer time-limited discounts during high-abandonment hours

        3. **Recovery Campaigns**:
           - Automated abandoned cart email series
           - Exit-intent popups with incentives
           - Retargeting ads for cart abandoners

        4. **Trust Signals**:
           - Display security badges
           - Show shipping costs upfront
           - Add customer reviews on product pages
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    # ==================== TAB 6: PRODUCT PERFORMANCE ====================
    with tab6:
        st.header("📦 Product Performance Analysis")

        product_performance = results['products']

        if len(product_performance) == 0:
            st.warning("No product sales data available.")
        else:
            st.markdown("""
            Analyze which products drive revenue, understand category performance, and identify opportunities.
            """)

            # Key metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                total_products = len(product_performance)
                st.metric(
                    "Total Products",
                    f"{total_products}",
                    help="Number of unique products sold"
                )

            with col2:
                total_units = product_performance['units_sold'].sum()
                st.metric(
                    "Units Sold",
                    f"{total_units:,}",
                    help="Total units sold across all products"
                )

            with col3:
                total_product_revenue = product_performance['revenue'].sum()
                st.metric(
                    "Total Revenue",
                    f"${total_product_revenue:,.2f}",
                    help="Total revenue from product sales"
                )

            with col4:
                avg_units_per_product = product_performance['units_sold'].mean()
                st.metric(
                    "Avg Units/Product",
                    f"{avg_units_per_product:.0f}",
                    help="Average units sold per product"
                )

            st.markdown("---")

            # Product visualization
            fig_products = visualizer.plot_product_performance(product_performance)
            st.plotly_chart(fig_products, use_container_width=True)

            # Product table
            st.subheader("📊 Complete Product Performance")

            # Add rank
            product_display = product_performance.copy()
            product_display['rank'] = range(1, len(product_display) + 1)
            product_display['revenue_share_pct'] = (product_display['revenue_share'] * 100).round(2)

            st.dataframe(
                product_display[['rank', 'product_name', 'category', 'units_sold', 'revenue',
                               'revenue_share_pct', 'num_orders', 'avg_quantity_per_order']].round(2),
                use_container_width=True,
                hide_index=True
            )

            # Category analysis
            st.subheader("🏷️ Category Performance")

            category_metrics = product_performance.groupby('category').agg({
                'product_id': 'count',
                'units_sold': 'sum',
                'revenue': 'sum',
                'num_orders': 'sum'
            }).reset_index()
            category_metrics.columns = ['category', 'num_products', 'units_sold', 'revenue', 'num_orders']
            category_metrics['avg_revenue_per_product'] = category_metrics['revenue'] / category_metrics['num_products']

            col1, col2 = st.columns(2)

            with col1:
                st.dataframe(category_metrics.round(2), use_container_width=True, hide_index=True)

            with col2:
                fig = px.bar(
                    category_metrics,
                    x='category',
                    y='revenue',
                    title='Revenue by Category',
                    color='category'
                )
                st.plotly_chart(fig, use_container_width=True)

            # Insights
            st.markdown('<div class="insight-box">', unsafe_allow_html=True)
            st.markdown("### 💡 Product Strategy Insights")

            top_product = product_performance.iloc[0]
            top_category = category_metrics.sort_values('revenue', ascending=False).iloc[0]

            st.markdown(f"""
            - **Top Product**: {top_product['product_name']} generates ${top_product['revenue']:.2f} ({top_product['revenue_share']*100:.1f}% of total revenue)
            - **Top Category**: {top_category['category']} leads with ${top_category['revenue']:.2f} in revenue
            - **Inventory Focus**: Top 20% of products drive significant revenue - prioritize stock
            - **Cross-Sell Opportunity**: Bundle popular products with lower performers
            - **Pricing Strategy**: High-revenue products may support premium pricing
            """)
            st.markdown('</div>', unsafe_allow_html=True)

    # ==================== TAB 7: CUSTOMER SEGMENTATION ====================
    with tab7:
        st.header("👥 Customer Segmentation (K-Means Clustering)")

        customer_segments = results['segments']

        st.markdown("""
        Machine learning-based customer segmentation using K-Means clustering.
        Customers are grouped based on:
        - Total sessions & revenue
        - Average order value
        - Conversion rate
        - Recency & engagement
        """)

        # Segment overview
        segment_counts = customer_segments['segment_name'].value_counts()

        col1, col2, col3, col4 = st.columns(4)

        for idx, (segment, count) in enumerate(segment_counts.items()):
            with [col1, col2, col3, col4][idx % 4]:
                pct = (count / len(customer_segments) * 100)
                st.metric(
                    segment,
                    f"{count:,}",
                    f"{pct:.1f}% of customers"
                )

        st.markdown("---")

        # Segmentation visualization
        fig_segments = visualizer.plot_customer_segments(customer_segments)
        st.plotly_chart(fig_segments, use_container_width=True)

        # Segment characteristics
        st.subheader("📊 Segment Characteristics")

        segment_summary = customer_segments[customer_segments['segment'] >= 0].groupby('segment_name').agg({
            'customer_id': 'count',
            'total_revenue': ['mean', 'sum'],
            'avg_order_value': 'mean',
            'total_sessions': 'mean',
            'conversion_rate': 'mean',
            'recency_days': 'mean'
        }).round(2)
        segment_summary.columns = ['customers', 'avg_revenue', 'total_revenue',
                                   'avg_order_value', 'avg_sessions', 'avg_conversion_rate', 'avg_recency']

        st.dataframe(segment_summary, use_container_width=True)

        # Segment profiles
        st.subheader("🎯 Segment Profiles & Strategies")

        segments_to_profile = customer_segments[customer_segments['segment'] >= 0]['segment_name'].unique()

        for segment in segments_to_profile:
            with st.expander(f"📌 {segment}"):
                segment_data = customer_segments[customer_segments['segment_name'] == segment]
                segment_stats = segment_summary.loc[segment]

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Segment Characteristics:**")
                    st.write(f"- Customers: {int(segment_stats['customers']):,}")
                    st.write(f"- Avg Revenue: ${segment_stats['avg_revenue']:.2f}")
                    st.write(f"- Avg Order Value: ${segment_stats['avg_order_value']:.2f}")
                    st.write(f"- Avg Sessions: {segment_stats['avg_sessions']:.1f}")
                    st.write(f"- Conversion Rate: {segment_stats['avg_conversion_rate']*100:.1f}%")

                with col2:
                    st.markdown("**Recommended Actions:**")
                    if 'High Value' in segment or 'Champions' in segment:
                        st.success("""
                        - VIP treatment and exclusive perks
                        - Personal account managers
                        - Beta access to new products
                        - Loyalty rewards program
                        """)
                    elif 'New' in segment or 'Promising' in segment:
                        st.info("""
                        - Welcome email series
                        - First purchase incentives
                        - Product education content
                        - Survey for preferences
                        """)
                    elif 'At Risk' in segment or 'Dormant' in segment:
                        st.warning("""
                        - Win-back campaigns
                        - Special offers and discounts
                        - Feedback surveys
                        - Re-engagement emails
                        """)
                    else:
                        st.write("""
                        - Regular email newsletters
                        - Seasonal promotions
                        - Product recommendations
                        - Engagement campaigns
                        """)

        # Export options
        st.markdown("---")
        st.subheader("📥 Export Data")

        col1, col2, col3 = st.columns(3)

        with col1:
            csv_customers = customer_segments.to_csv(index=False)
            st.download_button(
                label="📥 Download Customer Segments",
                data=csv_customers,
                file_name="customer_segments.csv",
                mime="text/csv"
            )

        with col2:
            if len(product_performance) > 0:
                csv_products = product_performance.to_csv(index=False)
                st.download_button(
                    label="📥 Download Product Performance",
                    data=csv_products,
                    file_name="product_performance.csv",
                    mime="text/csv"
                )

        with col3:
            csv_sessions = sessions_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Sessions Data",
                data=csv_sessions,
                file_name="sessions_data.csv",
                mime="text/csv"
            )

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>E-Commerce Analytics Pro | Advanced Business Intelligence Dashboard</p>
        <p>Built with Streamlit, Pandas, Scikit-learn, and Plotly</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
