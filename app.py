"""
GA Extractor Pro - MVP
Standalone Google Analytics 4 Data Extraction with ML Insights

A simple, powerful tool for extracting and analyzing GA4 data without coding.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Import e-commerce analytics module
try:
    from ecommerce_analytics import (
        EcommerceDataGenerator,
        EcommerceDataCleaner,
        EcommerceAnalytics,
        EcommerceVisualizer
    )
    ECOMMERCE_AVAILABLE = True
except ImportError:
    ECOMMERCE_AVAILABLE = False

# Page config
st.set_page_config(
    page_title="GA Extractor Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("📊 GA Extractor Pro - MVP")
st.markdown("**Extract Google Analytics 4 data and get instant ML-powered insights**")

# Initialize session state
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'data' not in st.session_state:
    st.session_state.data = None
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = False
if 'dataset_type' not in st.session_state:
    st.session_state.dataset_type = 'Google Analytics'
if 'ecommerce_data' not in st.session_state:
    st.session_state.ecommerce_data = None


@st.cache_data
def generate_demo_data(days=90):
    """Generate realistic demo GA4 data for demonstration"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')

    # Generate realistic patterns
    base_sessions = 1000
    trend = np.linspace(0, 200, days)  # Upward trend
    seasonality = 150 * np.sin(np.arange(days) * 2 * np.pi / 7)  # Weekly pattern
    noise = np.random.normal(0, 50, days)

    sessions = base_sessions + trend + seasonality + noise
    sessions = np.maximum(sessions, 100).astype(int)

    # Correlated metrics
    users = (sessions * np.random.uniform(0.6, 0.8, days)).astype(int)
    new_users = (users * np.random.uniform(0.3, 0.5, days)).astype(int)
    pageviews = (sessions * np.random.uniform(2.5, 4.0, days)).astype(int)
    bounce_rate = np.random.uniform(0.35, 0.65, days)
    avg_session_duration = np.random.uniform(120, 300, days)
    conversions = (sessions * np.random.uniform(0.01, 0.05, days)).astype(int)
    revenue = conversions * np.random.uniform(50, 200, days)

    df = pd.DataFrame({
        'date': dates,
        'sessions': sessions,
        'totalUsers': users,
        'newUsers': new_users,
        'screenPageViews': pageviews,
        'bounceRate': bounce_rate,
        'averageSessionDuration': avg_session_duration,
        'conversions': conversions,
        'revenue': revenue
    })

    return df


@st.cache_data
def perform_clustering(df, n_clusters=3):
    """Perform K-means clustering on data"""
    # Select numeric columns
    numeric_cols = ['sessions', 'totalUsers', 'conversions', 'revenue']
    X = df[numeric_cols].values

    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Cluster
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df['cluster'] = kmeans.fit_predict(X_scaled)

    # Label clusters
    cluster_names = {0: 'Low Activity', 1: 'Medium Activity', 2: 'High Activity'}
    cluster_means = df.groupby('cluster')[numeric_cols].mean()
    sorted_clusters = cluster_means['sessions'].sort_values().index

    cluster_mapping = {old: new for new, old in enumerate(sorted_clusters)}
    df['cluster'] = df['cluster'].map(cluster_mapping)
    df['cluster_name'] = df['cluster'].map(cluster_names)

    return df, cluster_means


@st.cache_data
def detect_trends(df):
    """Detect trends using linear regression"""
    X = np.arange(len(df)).reshape(-1, 1)
    y = df['sessions'].values

    # Simple linear fit
    coeffs = np.polyfit(X.flatten(), y, 1)
    trend_line = np.poly1d(coeffs)

    slope = coeffs[0]
    if slope > 5:
        direction = "Upward"
        color = "green"
    elif slope < -5:
        direction = "Downward"
        color = "red"
    else:
        direction = "Stable"
        color = "gray"

    growth_rate = ((y[-1] - y[0]) / y[0]) * 100 if y[0] != 0 else 0

    return {
        'direction': direction,
        'color': color,
        'slope': slope,
        'growth_rate': growth_rate,
        'trend_line': trend_line(X.flatten())
    }


@st.cache_data
def detect_anomalies(df, column='sessions'):
    """Detect anomalies using IQR method"""
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    df['is_anomaly'] = (df[column] < lower_bound) | (df[column] > upper_bound)
    anomalies = df[df['is_anomaly']]

    return df, anomalies, lower_bound, upper_bound


# Sidebar
with st.sidebar:
    st.header("🔌 Connection")

    # Dataset type selector
    dataset_options = ['Google Analytics']
    if ECOMMERCE_AVAILABLE:
        dataset_options.append('E-Commerce')

    dataset_type = st.selectbox(
        "📊 Select Dataset Type",
        dataset_options,
        index=dataset_options.index(st.session_state.dataset_type) if st.session_state.dataset_type in dataset_options else 0
    )

    if dataset_type != st.session_state.dataset_type:
        st.session_state.dataset_type = dataset_type
        st.session_state.connected = False
        st.session_state.data = None
        st.rerun()

    st.divider()

    # Demo mode toggle
    use_demo = st.checkbox("🎭 Use Demo Data (for testing)", value=True)

    if use_demo:
        if st.button("Connect to Demo", type="primary"):
            with st.spinner("Generating demo data..."):
                if st.session_state.dataset_type == 'E-Commerce' and ECOMMERCE_AVAILABLE:
                    # Generate e-commerce data
                    generator = EcommerceDataGenerator(seed=42)
                    sessions_df, events_df, transactions_df = generator.generate_dataset(
                        visits_per_month=25000,
                        months=2
                    )
                    cleaner = EcommerceDataCleaner()
                    sessions_clean = cleaner.clean_sessions(sessions_df)
                    transactions_clean = cleaner.clean_transactions(transactions_df)
                    customer_df = cleaner.create_customer_summary(sessions_clean, transactions_clean)

                    st.session_state.ecommerce_data = {
                        'sessions': sessions_clean,
                        'events': events_df,
                        'transactions': transactions_clean,
                        'customers': customer_df
                    }
                    st.session_state.data = sessions_clean  # For compatibility
                else:
                    # Generate Google Analytics data
                    st.session_state.data = generate_demo_data(90)
                    st.session_state.ecommerce_data = None

                st.session_state.connected = True
                st.session_state.demo_mode = True
            st.success("✅ Connected to demo data!")
            st.rerun()
    else:
        st.markdown("**Real GA4 Connection**")
        st.info("⚠️ Real GA4 connection requires service account JSON. For this MVP, use Demo Mode.")

        uploaded_file = st.file_uploader("Upload Service Account JSON", type=['json'])
        property_id = st.text_input("GA4 Property ID", placeholder="123456789")

        if st.button("Connect to GA4", type="primary", disabled=True):
            st.warning("Real GA4 connection coming in full version!")

    st.divider()

    if st.session_state.connected:
        st.success("🟢 Connected")
        if st.button("Disconnect"):
            st.session_state.connected = False
            st.session_state.data = None
            st.rerun()

    st.divider()
    st.caption("GA Extractor Pro v1.0 MVP")
    st.caption("© 2025 - Demo Version")


# Main content
if not st.session_state.connected:
    # Landing page
    st.info("👈 **Get Started**: Click 'Connect to Demo' in the sidebar to see the tool in action!")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### ⚡ Fast")
        st.markdown("Extract years of data in seconds, not hours")

    with col2:
        st.markdown("### 🤖 Smart")
        st.markdown("Built-in ML finds patterns automatically")

    with col3:
        st.markdown("### 💰 Affordable")
        st.markdown("$29/month vs $2,400/year in manual work")

    st.divider()

    st.markdown("### 🎯 Features")

    features = {
        "📊 Data Extraction": "One-click export of unlimited GA4 historical data",
        "🔍 Clustering Analysis": "Automatically group similar traffic patterns",
        "📈 Trend Detection": "Identify upward, downward, or stable trends",
        "⚠️ Anomaly Detection": "Spot unusual spikes or drops instantly",
        "📉 Visualization": "Interactive charts powered by Plotly",
        "💾 Export": "Download as CSV for further analysis"
    }

    for feature, description in features.items():
        st.markdown(f"**{feature}**: {description}")

else:
    # Data loaded - show analysis based on dataset type
    if st.session_state.dataset_type == 'E-Commerce' and st.session_state.ecommerce_data:
        # E-COMMERCE ANALYTICS VIEW
        st.markdown("## 🛒 E-Commerce Analytics Dashboard")
        st.markdown("**Comprehensive business intelligence for online retail**")

        ecom_data = st.session_state.ecommerce_data
        sessions_df = ecom_data['sessions']
        transactions_df = ecom_data['transactions']
        customer_df = ecom_data['customers']

        # Run analytics
        analytics = EcommerceAnalytics()
        visualizer = EcommerceVisualizer()

        # Overview metrics
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Total Sessions", f"{len(sessions_df):,}")
        with col2:
            total_revenue = transactions_df['total_amount'].sum()
            st.metric("Total Revenue", f"${total_revenue:,.2f}")
        with col3:
            conversion_rate = (sessions_df['converted'].sum() / len(sessions_df)) * 100
            st.metric("Conversion Rate", f"{conversion_rate:.2f}%")
        with col4:
            if len(transactions_df) > 0:
                avg_order_value = transactions_df.groupby('transaction_id')['order_total'].first().mean()
                st.metric("Avg Order Value", f"${avg_order_value:.2f}")
            else:
                st.metric("Avg Order Value", "$0.00")
        with col5:
            total_customers = customer_df[customer_df['total_orders'] > 0].shape[0]
            st.metric("Customers", f"{total_customers:,}")

        st.divider()

        # Tabs for e-commerce analytics
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "💰 Customer Lifetime Value",
            "🎯 RFM Analysis",
            "🛒 Cart Abandonment",
            "📦 Product Performance",
            "👥 Customer Segmentation",
            "📊 Raw Data"
        ])

        # Tab 1: CLV
        with tab1:
            st.header("💰 Customer Lifetime Value Analysis")

            customer_clv = analytics.calculate_clv(customer_df)

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                avg_clv = customer_clv['total_clv'].mean()
                st.metric("Average CLV", f"${avg_clv:.2f}")
            with col2:
                median_clv = customer_clv['total_clv'].median()
                st.metric("Median CLV", f"${median_clv:.2f}")
            with col3:
                top_10_pct_clv = customer_clv.nlargest(int(len(customer_clv) * 0.1), 'total_clv')['total_clv'].sum()
                total_clv = customer_clv['total_clv'].sum()
                top_pct = (top_10_pct_clv / total_clv * 100) if total_clv > 0 else 0
                st.metric("Top 10% CLV Share", f"{top_pct:.1f}%")
            with col4:
                vip_count = (customer_clv['clv_segment'] == 'VIP').sum()
                st.metric("VIP Customers", f"{vip_count:,}")

            fig_clv = visualizer.plot_clv_distribution(customer_clv)
            st.plotly_chart(fig_clv, use_container_width=True)

            st.subheader("Top 20 Customers by CLV")
            top_customers = customer_clv.nlargest(20, 'total_clv')[
                ['customer_id', 'total_clv', 'historical_clv', 'predicted_clv',
                 'total_orders', 'avg_order_value', 'clv_segment']
            ].round(2)
            st.dataframe(top_customers, use_container_width=True, hide_index=True)

        # Tab 2: RFM
        with tab2:
            st.header("🎯 RFM Analysis")

            customer_rfm = analytics.rfm_analysis(customer_df)

            if len(customer_rfm) > 0:
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    champions = (customer_rfm['rfm_segment'] == 'Champions').sum()
                    st.metric("Champions", f"{champions:,}")
                with col2:
                    loyal = (customer_rfm['rfm_segment'] == 'Loyal Customers').sum()
                    st.metric("Loyal Customers", f"{loyal:,}")
                with col3:
                    at_risk = (customer_rfm['rfm_segment'] == 'At Risk').sum()
                    st.metric("At Risk", f"{at_risk:,}")
                with col4:
                    lost = (customer_rfm['rfm_segment'] == 'Lost').sum()
                    st.metric("Lost", f"{lost:,}")

                fig_rfm = visualizer.plot_rfm_segments(customer_rfm)
                st.plotly_chart(fig_rfm, use_container_width=True)

                st.subheader("RFM Segment Details")
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
            else:
                st.warning("No customers with purchases for RFM analysis")

        # Tab 3: Cart Abandonment
        with tab3:
            st.header("🛒 Cart Abandonment Analysis")

            abandonment_data = analytics.cart_abandonment_analysis(sessions_df)

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Carts", f"{abandonment_data['total_carts']:,}")
            with col2:
                st.metric("Abandoned Carts", f"{abandonment_data['abandoned_carts']:,}")
            with col3:
                abandonment_rate = abandonment_data['abandonment_rate'] * 100
                st.metric("Abandonment Rate", f"{abandonment_rate:.1f}%")
            with col4:
                if len(transactions_df) > 0:
                    avg_order = transactions_df.groupby('transaction_id')['order_total'].first().mean()
                    lost_revenue = avg_order * abandonment_data['abandoned_carts']
                    st.metric("Estimated Lost Revenue", f"${lost_revenue:,.2f}")

            fig_abandonment = visualizer.plot_cart_abandonment(abandonment_data)
            st.plotly_chart(fig_abandonment, use_container_width=True)

        # Tab 4: Product Performance
        with tab4:
            st.header("📦 Product Performance")

            product_performance = analytics.product_performance_analysis(transactions_df)

            if len(product_performance) > 0:
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Products", f"{len(product_performance)}")
                with col2:
                    total_units = product_performance['units_sold'].sum()
                    st.metric("Units Sold", f"{total_units:,}")
                with col3:
                    total_product_revenue = product_performance['revenue'].sum()
                    st.metric("Total Revenue", f"${total_product_revenue:,.2f}")
                with col4:
                    avg_units_per_product = product_performance['units_sold'].mean()
                    st.metric("Avg Units/Product", f"{avg_units_per_product:.0f}")

                fig_products = visualizer.plot_product_performance(product_performance)
                st.plotly_chart(fig_products, use_container_width=True)

                st.subheader("Complete Product Performance")
                product_display = product_performance.copy()
                product_display['rank'] = range(1, len(product_display) + 1)
                product_display['revenue_share_pct'] = (product_display['revenue_share'] * 100).round(2)
                st.dataframe(
                    product_display[['rank', 'product_name', 'category', 'units_sold', 'revenue',
                                   'revenue_share_pct', 'num_orders']].round(2),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.warning("No product sales data available")

        # Tab 5: Customer Segmentation
        with tab5:
            st.header("👥 Customer Segmentation (K-Means)")

            customer_segments, segment_analysis = analytics.customer_segmentation(customer_df)

            segment_counts = customer_segments['segment_name'].value_counts()

            cols = st.columns(min(4, len(segment_counts)))
            for idx, (segment, count) in enumerate(segment_counts.items()):
                with cols[idx % len(cols)]:
                    pct = (count / len(customer_segments) * 100)
                    st.metric(segment, f"{count:,}", f"{pct:.1f}%")

            fig_segments = visualizer.plot_customer_segments(customer_segments)
            st.plotly_chart(fig_segments, use_container_width=True)

            st.subheader("Segment Characteristics")
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

        # Tab 6: Raw Data
        with tab6:
            st.header("📊 Raw Data")

            data_selector = st.selectbox("Select Dataset", ["Sessions", "Transactions", "Customers"])

            if data_selector == "Sessions":
                st.dataframe(sessions_df, use_container_width=True)
                csv = sessions_df.to_csv(index=False).encode('utf-8')
                st.download_button("Download Sessions CSV", csv, "sessions.csv", "text/csv")
            elif data_selector == "Transactions":
                st.dataframe(transactions_df, use_container_width=True)
                csv = transactions_df.to_csv(index=False).encode('utf-8')
                st.download_button("Download Transactions CSV", csv, "transactions.csv", "text/csv")
            else:
                st.dataframe(customer_df, use_container_width=True)
                csv = customer_df.to_csv(index=False).encode('utf-8')
                st.download_button("Download Customers CSV", csv, "customers.csv", "text/csv")

    else:
        # GOOGLE ANALYTICS VIEW (existing code)
        df = st.session_state.data

        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🔍 Clustering", "📈 Trends", "⚠️ Anomalies"])

        # Tab 1: Overview
        with tab1:
            st.header("📊 Data Overview")

            # Metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Sessions", f"{df['sessions'].sum():,}")
            with col2:
                st.metric("Total Users", f"{df['totalUsers'].sum():,}")
            with col3:
                st.metric("Total Conversions", f"{df['conversions'].sum():,}")
            with col4:
                st.metric("Total Revenue", f"${df['revenue'].sum():,.2f}")

            st.divider()

            # Main chart
            st.subheader("📈 Sessions Over Time")

            fig = px.line(df, x='date', y='sessions', title='Daily Sessions')
            fig.update_layout(hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)

            # Data table
            st.subheader("📋 Raw Data")
            st.dataframe(df, use_container_width=True)

            # Download
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name=f"ga_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

        # Tab 2: Clustering
        with tab2:
            st.header("🔍 Clustering Analysis")
            st.markdown("**Automatically group days with similar traffic patterns**")

            n_clusters = st.slider("Number of Clusters", 2, 5, 3)

            if st.button("🎯 Run Clustering", type="primary"):
                with st.spinner("Clustering data..."):
                    df_clustered, cluster_stats = perform_clustering(df.copy(), n_clusters)
                    st.session_state.data_clustered = df_clustered
                    st.session_state.cluster_stats = cluster_stats

            if 'data_clustered' in st.session_state:
                df_c = st.session_state.data_clustered
                stats = st.session_state.cluster_stats

                st.success("✅ Clustering complete!")

                # Cluster statistics
                st.subheader("📊 Cluster Statistics")
                st.dataframe(stats.round(2), use_container_width=True)

                # Visualization
                st.subheader("📈 Clusters Visualization")

                fig = px.scatter(
                    df_c,
                    x='date',
                    y='sessions',
                    color='cluster_name',
                    title='Sessions by Cluster',
                    hover_data=['totalUsers', 'conversions']
                )
                st.plotly_chart(fig, use_container_width=True)

                # Insights
                st.subheader("💡 Insights")

                for cluster_id in sorted(df_c['cluster'].unique()):
                    cluster_data = df_c[df_c['cluster'] == cluster_id]
                    cluster_name = cluster_data['cluster_name'].iloc[0]
                    count = len(cluster_data)
                    avg_sessions = cluster_data['sessions'].mean()
                    avg_conversions = cluster_data['conversions'].mean()

                    st.markdown(f"""
                    **{cluster_name}** ({count} days):
                    - Average sessions: {avg_sessions:.0f}
                    - Average conversions: {avg_conversions:.1f}
                    - Conversion rate: {(avg_conversions/avg_sessions*100):.2f}%
                    """)

    # Tab 3: Trends
    with tab3:
        st.header("📈 Trend Analysis")
        st.markdown("**Detect growth patterns and predict future values**")

        trend_results = detect_trends(df)

        # Trend metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Trend Direction", trend_results['direction'])
        with col2:
            st.metric("Growth Rate", f"{trend_results['growth_rate']:.1f}%")
        with col3:
            st.metric("Daily Change", f"{trend_results['slope']:.1f} sessions/day")

        # Visualization
        st.subheader("📊 Trend Visualization")

        fig = go.Figure()

        # Actual data
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['sessions'],
            mode='lines',
            name='Actual Sessions',
            line=dict(color='blue')
        ))

        # Trend line
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=trend_results['trend_line'],
            mode='lines',
            name='Trend Line',
            line=dict(color='red', dash='dash')
        ))

        fig.update_layout(
            title='Sessions with Trend Line',
            xaxis_title='Date',
            yaxis_title='Sessions',
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True)

        # Insights
        st.subheader("💡 Insights")

        if trend_results['growth_rate'] > 10:
            st.success(f"🎉 **Strong Growth**: Traffic is growing at {trend_results['growth_rate']:.1f}% over the period")
        elif trend_results['growth_rate'] > 0:
            st.info(f"📈 **Positive Growth**: Traffic is growing at {trend_results['growth_rate']:.1f}%")
        elif trend_results['growth_rate'] > -10:
            st.warning(f"➡️ **Slight Decline**: Traffic decreased by {abs(trend_results['growth_rate']):.1f}%")
        else:
            st.error(f"📉 **Significant Decline**: Traffic dropped by {abs(trend_results['growth_rate']):.1f}%")

    # Tab 4: Anomalies
    with tab4:
        st.header("⚠️ Anomaly Detection")
        st.markdown("**Identify unusual spikes or drops in traffic**")

        df_anomaly, anomalies, lower, upper = detect_anomalies(df.copy())

        # Anomaly metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Anomalies Detected", len(anomalies))
        with col2:
            st.metric("Lower Threshold", f"{lower:.0f}")
        with col3:
            st.metric("Upper Threshold", f"{upper:.0f}")

        # Visualization
        st.subheader("📊 Anomaly Visualization")

        fig = go.Figure()

        # Normal data
        normal_data = df_anomaly[~df_anomaly['is_anomaly']]
        fig.add_trace(go.Scatter(
            x=normal_data['date'],
            y=normal_data['sessions'],
            mode='markers',
            name='Normal',
            marker=dict(color='blue', size=6)
        ))

        # Anomalies
        fig.add_trace(go.Scatter(
            x=anomalies['date'],
            y=anomalies['sessions'],
            mode='markers',
            name='Anomalies',
            marker=dict(color='red', size=10, symbol='x')
        ))

        # Thresholds
        fig.add_hline(y=upper, line_dash="dash", line_color="orange", annotation_text="Upper Threshold")
        fig.add_hline(y=lower, line_dash="dash", line_color="orange", annotation_text="Lower Threshold")

        fig.update_layout(
            title='Sessions with Anomaly Detection',
            xaxis_title='Date',
            yaxis_title='Sessions',
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True)

        # Anomaly details
        if len(anomalies) > 0:
            st.subheader("📋 Anomaly Details")
            st.dataframe(
                anomalies[['date', 'sessions', 'totalUsers', 'conversions']].sort_values('date', ascending=False),
                use_container_width=True
            )

            st.subheader("💡 Insights")

            for _, row in anomalies.iterrows():
                if row['sessions'] > upper:
                    st.success(f"📈 **Spike on {row['date'].strftime('%Y-%m-%d')}**: {row['sessions']:.0f} sessions (avg: {df['sessions'].mean():.0f})")
                else:
                    st.warning(f"📉 **Drop on {row['date'].strftime('%Y-%m-%d')}**: {row['sessions']:.0f} sessions (avg: {df['sessions'].mean():.0f})")
        else:
            st.info("✅ No anomalies detected. Traffic patterns are stable.")

# Footer
st.divider()
st.caption("💡 **Tip**: This is a demo version. Upgrade to Pro for real GA4 connection, unlimited data, and advanced ML models.")
st.caption("📧 Contact: demo@ga-extractor.com | 🌐 Website: ga-extractor.com")
