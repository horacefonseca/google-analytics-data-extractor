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

    return anomalies, lower_bound, upper_bound


# Sidebar
with st.sidebar:
    st.header("🔌 Connection")

    # Demo mode toggle
    use_demo = st.checkbox("🎭 Use Demo Data (for testing)", value=True)

    if use_demo:
        if st.button("Connect to Demo", type="primary"):
            with st.spinner("Generating demo data..."):
                st.session_state.data = generate_demo_data(90)
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
    # Data loaded - show analysis
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

        df_anomaly = df.copy()
        anomalies, lower, upper = detect_anomalies(df_anomaly)

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
