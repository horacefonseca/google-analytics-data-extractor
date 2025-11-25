"""
E-Commerce Analytics Module
Synthetic dataset generation and advanced analytics for e-commerce business intelligence

Features:
- Synthetic data generation (25k visits/month, 2 months)
- Data cleaning and wrangling pipeline
- Customer Lifetime Value (CLV) analysis
- RFM Analysis (Recency, Frequency, Monetary)
- Cart Abandonment Analysis
- Product Performance Analysis
- Customer Segmentation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import Tuple, Dict, List
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class EcommerceDataGenerator:
    """Generate realistic synthetic e-commerce data"""

    def __init__(self, seed=42):
        np.random.seed(seed)
        random.seed(seed)

        # Product catalog
        self.products = [
            {'id': 'P001', 'name': 'Wireless Headphones', 'category': 'Electronics', 'price': 79.99},
            {'id': 'P002', 'name': 'Smart Watch', 'category': 'Electronics', 'price': 199.99},
            {'id': 'P003', 'name': 'Laptop Stand', 'category': 'Accessories', 'price': 34.99},
            {'id': 'P004', 'name': 'USB-C Cable', 'category': 'Accessories', 'price': 12.99},
            {'id': 'P005', 'name': 'Mechanical Keyboard', 'category': 'Electronics', 'price': 129.99},
            {'id': 'P006', 'name': 'Ergonomic Mouse', 'category': 'Electronics', 'price': 49.99},
            {'id': 'P007', 'name': 'Phone Case', 'category': 'Accessories', 'price': 19.99},
            {'id': 'P008', 'name': 'Screen Protector', 'category': 'Accessories', 'price': 9.99},
            {'id': 'P009', 'name': 'Portable Charger', 'category': 'Electronics', 'price': 39.99},
            {'id': 'P010', 'name': 'Bluetooth Speaker', 'category': 'Electronics', 'price': 89.99},
            {'id': 'P011', 'name': 'Webcam HD', 'category': 'Electronics', 'price': 69.99},
            {'id': 'P012', 'name': 'Desk Lamp', 'category': 'Accessories', 'price': 29.99},
            {'id': 'P013', 'name': 'Monitor 27"', 'category': 'Electronics', 'price': 299.99},
            {'id': 'P014', 'name': 'Laptop Sleeve', 'category': 'Accessories', 'price': 24.99},
            {'id': 'P015', 'name': 'Cable Organizer', 'category': 'Accessories', 'price': 14.99},
        ]

        self.devices = ['Desktop', 'Mobile', 'Tablet']
        self.channels = ['Organic Search', 'Paid Search', 'Social Media', 'Direct', 'Email', 'Referral']
        self.countries = ['USA', 'Canada', 'UK', 'Germany', 'France', 'Australia', 'Spain']

    def generate_dataset(self, visits_per_month=25000, months=2) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Generate complete e-commerce dataset

        Returns:
            sessions_df: Session-level data
            events_df: Event-level data (page views, cart actions)
            transactions_df: Completed transactions
        """
        total_visits = visits_per_month * months

        # Generate sessions
        sessions_data = []
        events_data = []
        transactions_data = []

        # Create customer pool (30% are returning customers)
        total_customers = int(total_visits * 0.6)  # Not every visit is unique customer
        customer_ids = [f'C{i:06d}' for i in range(1, total_customers + 1)]

        # Some customers will visit multiple times
        returning_customer_pool = random.sample(customer_ids, int(total_customers * 0.3))

        session_id = 1
        transaction_id = 1

        start_date = datetime.now() - timedelta(days=60)

        for _ in range(total_visits):
            # Decide if returning customer
            if random.random() < 0.3 and len(returning_customer_pool) > 0:
                customer_id = random.choice(returning_customer_pool)
                is_returning = True
            else:
                customer_id = random.choice(customer_ids)
                is_returning = random.random() < 0.2

            # Session details
            session_date = start_date + timedelta(
                days=random.randint(0, 59),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )

            device = np.random.choice(self.devices, p=[0.45, 0.40, 0.15])
            channel = np.random.choice(self.channels, p=[0.30, 0.25, 0.20, 0.15, 0.05, 0.05])
            country = np.random.choice(self.countries, p=[0.40, 0.15, 0.12, 0.10, 0.08, 0.08, 0.07])

            # Session behavior
            pages_viewed = max(1, int(np.random.exponential(3)))
            time_on_site = max(10, int(np.random.exponential(180)))  # seconds

            # Conversion probability (influenced by device, channel, returning status)
            base_conversion_rate = 0.03
            if is_returning:
                base_conversion_rate *= 2.5
            if device == 'Desktop':
                base_conversion_rate *= 1.3
            if channel in ['Email', 'Direct']:
                base_conversion_rate *= 1.5

            converted = random.random() < base_conversion_rate

            # Cart abandonment (some users add to cart but don't purchase)
            added_to_cart = random.random() < 0.15  # 15% add to cart
            cart_abandoned = False

            if added_to_cart and not converted:
                cart_abandoned = random.random() < 0.70  # 70% of carts are abandoned

            session_data = {
                'session_id': f'S{session_id:08d}',
                'customer_id': customer_id,
                'session_date': session_date,
                'device': device,
                'channel': channel,
                'country': country,
                'is_returning': is_returning,
                'pages_viewed': pages_viewed,
                'time_on_site': time_on_site,
                'added_to_cart': added_to_cart,
                'cart_abandoned': cart_abandoned,
                'converted': converted
            }
            sessions_data.append(session_data)

            # Generate events for this session
            event_time = session_date

            # Landing page
            events_data.append({
                'event_id': len(events_data) + 1,
                'session_id': f'S{session_id:08d}',
                'event_type': 'landing',
                'event_time': event_time,
                'product_id': None,
                'product_name': None
            })

            # Product views
            products_viewed = random.sample(self.products, min(pages_viewed, len(self.products)))
            for i, product in enumerate(products_viewed):
                event_time += timedelta(seconds=random.randint(10, 60))
                events_data.append({
                    'event_id': len(events_data) + 1,
                    'session_id': f'S{session_id:08d}',
                    'event_type': 'product_view',
                    'event_time': event_time,
                    'product_id': product['id'],
                    'product_name': product['name']
                })

            # Add to cart events
            if added_to_cart:
                cart_products = random.sample(products_viewed, random.randint(1, min(3, len(products_viewed))))
                for product in cart_products:
                    event_time += timedelta(seconds=random.randint(5, 30))
                    events_data.append({
                        'event_id': len(events_data) + 1,
                        'session_id': f'S{session_id:08d}',
                        'event_type': 'add_to_cart',
                        'event_time': event_time,
                        'product_id': product['id'],
                        'product_name': product['name']
                    })

                if converted:
                    # Checkout initiated
                    event_time += timedelta(seconds=random.randint(10, 120))
                    events_data.append({
                        'event_id': len(events_data) + 1,
                        'session_id': f'S{session_id:08d}',
                        'event_type': 'checkout_start',
                        'event_time': event_time,
                        'product_id': None,
                        'product_name': None
                    })

                    # Purchase completed
                    event_time += timedelta(seconds=random.randint(60, 300))
                    events_data.append({
                        'event_id': len(events_data) + 1,
                        'session_id': f'S{session_id:08d}',
                        'event_type': 'purchase',
                        'event_time': event_time,
                        'product_id': None,
                        'product_name': None
                    })

                    # Create transaction
                    quantity_per_product = {p['id']: random.randint(1, 2) for p in cart_products}
                    total_amount = sum(p['price'] * quantity_per_product[p['id']] for p in cart_products)

                    for product in cart_products:
                        transactions_data.append({
                            'transaction_id': f'T{transaction_id:08d}',
                            'session_id': f'S{session_id:08d}',
                            'customer_id': customer_id,
                            'transaction_date': event_time,
                            'product_id': product['id'],
                            'product_name': product['name'],
                            'category': product['category'],
                            'quantity': quantity_per_product[product['id']],
                            'unit_price': product['price'],
                            'total_amount': product['price'] * quantity_per_product[product['id']],
                            'order_total': total_amount,
                            'device': device,
                            'channel': channel,
                            'country': country
                        })

                    transaction_id += 1

                elif cart_abandoned:
                    # Cart abandoned event
                    event_time += timedelta(seconds=random.randint(30, 180))
                    events_data.append({
                        'event_id': len(events_data) + 1,
                        'session_id': f'S{session_id:08d}',
                        'event_type': 'cart_abandoned',
                        'event_time': event_time,
                        'product_id': None,
                        'product_name': None
                    })

            session_id += 1

        sessions_df = pd.DataFrame(sessions_data)
        events_df = pd.DataFrame(events_data)
        transactions_df = pd.DataFrame(transactions_data)

        return sessions_df, events_df, transactions_df


class EcommerceDataCleaner:
    """Data cleaning and wrangling pipeline"""

    @staticmethod
    def clean_sessions(sessions_df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare session data"""
        df = sessions_df.copy()

        # Convert dates
        df['session_date'] = pd.to_datetime(df['session_date'])

        # Remove duplicates
        df = df.drop_duplicates(subset=['session_id'])

        # Handle missing values (in real data)
        df['device'] = df['device'].fillna('Unknown')
        df['channel'] = df['channel'].fillna('Unknown')

        # Add derived fields
        df['session_hour'] = df['session_date'].dt.hour
        df['session_day_of_week'] = df['session_date'].dt.dayofweek
        df['session_week'] = df['session_date'].dt.isocalendar().week

        # Categorize time on site
        df['engagement_level'] = pd.cut(
            df['time_on_site'],
            bins=[0, 30, 120, 300, float('inf')],
            labels=['Very Low', 'Low', 'Medium', 'High']
        )

        return df

    @staticmethod
    def clean_transactions(transactions_df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare transaction data"""
        df = transactions_df.copy()

        # Convert dates
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])

        # Remove invalid transactions
        df = df[df['total_amount'] > 0]
        df = df[df['quantity'] > 0]

        # Add derived fields
        df['transaction_month'] = df['transaction_date'].dt.to_period('M')
        df['transaction_week'] = df['transaction_date'].dt.isocalendar().week

        return df

    @staticmethod
    def create_customer_summary(sessions_df: pd.DataFrame, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """Create customer-level summary for analysis"""

        # Session metrics by customer
        session_metrics = sessions_df.groupby('customer_id').agg({
            'session_id': 'count',
            'session_date': ['min', 'max'],
            'converted': 'sum',
            'time_on_site': 'mean',
            'pages_viewed': 'mean',
            'cart_abandoned': 'sum'
        }).reset_index()

        session_metrics.columns = ['customer_id', 'total_sessions', 'first_session', 'last_session',
                                   'total_conversions', 'avg_time_on_site', 'avg_pages_viewed', 'total_cart_abandonments']

        # Transaction metrics by customer
        if len(transactions_df) > 0:
            transaction_metrics = transactions_df.groupby('customer_id').agg({
                'transaction_id': 'nunique',
                'total_amount': 'sum',
                'transaction_date': ['min', 'max']
            }).reset_index()

            transaction_metrics.columns = ['customer_id', 'total_orders', 'total_revenue',
                                           'first_purchase', 'last_purchase']

            # Merge
            customer_df = session_metrics.merge(transaction_metrics, on='customer_id', how='left')
            customer_df['total_orders'] = customer_df['total_orders'].fillna(0)
            customer_df['total_revenue'] = customer_df['total_revenue'].fillna(0)
        else:
            customer_df = session_metrics
            customer_df['total_orders'] = 0
            customer_df['total_revenue'] = 0

        # Calculate additional metrics
        customer_df['conversion_rate'] = customer_df['total_conversions'] / customer_df['total_sessions']
        customer_df['avg_order_value'] = customer_df.apply(
            lambda x: x['total_revenue'] / x['total_orders'] if x['total_orders'] > 0 else 0,
            axis=1
        )

        # Recency (days since last session)
        current_date = sessions_df['session_date'].max()
        customer_df['recency_days'] = (current_date - customer_df['last_session']).dt.days

        return customer_df


class EcommerceAnalytics:
    """Advanced analytics for e-commerce data"""

    @staticmethod
    def calculate_clv(customer_df: pd.DataFrame, projection_months=12) -> pd.DataFrame:
        """
        Calculate Customer Lifetime Value

        CLV = (Average Order Value × Purchase Frequency) × Customer Lifespan
        """
        df = customer_df.copy()

        # Historical CLV (actual revenue)
        df['historical_clv'] = df['total_revenue']

        # Calculate average purchase frequency (orders per month)
        df['customer_age_days'] = (df['last_session'] - df['first_session']).dt.days
        df['customer_age_months'] = df['customer_age_days'] / 30
        df['customer_age_months'] = df['customer_age_months'].replace(0, 1)  # Avoid division by zero

        df['purchase_frequency_monthly'] = df['total_orders'] / df['customer_age_months']

        # Predicted CLV (simple projection)
        df['predicted_clv'] = df['avg_order_value'] * df['purchase_frequency_monthly'] * projection_months

        # Total CLV
        df['total_clv'] = df['historical_clv'] + df['predicted_clv']

        # CLV segments - only segment customers with CLV > 0
        df['clv_segment'] = 'No Purchase'

        customers_with_clv = df[df['total_clv'] > 0].copy()
        if len(customers_with_clv) > 0:
            try:
                # Try with 4 segments
                customers_with_clv['clv_segment'] = pd.qcut(
                    customers_with_clv['total_clv'],
                    q=4,
                    labels=['Low Value', 'Medium Value', 'High Value', 'VIP'],
                    duplicates='drop'
                )
            except (ValueError, TypeError):
                # Fallback: use simple percentile-based segmentation
                percentile_75 = customers_with_clv['total_clv'].quantile(0.75)
                percentile_50 = customers_with_clv['total_clv'].quantile(0.50)
                percentile_25 = customers_with_clv['total_clv'].quantile(0.25)

                def assign_segment(clv):
                    if clv >= percentile_75:
                        return 'High Value'
                    elif clv >= percentile_50:
                        return 'Medium Value'
                    else:
                        return 'Low Value'

                customers_with_clv['clv_segment'] = customers_with_clv['total_clv'].apply(assign_segment)

            # Merge back
            df.loc[customers_with_clv.index, 'clv_segment'] = customers_with_clv['clv_segment']

        return df

    @staticmethod
    def rfm_analysis(customer_df: pd.DataFrame) -> pd.DataFrame:
        """
        RFM Analysis: Recency, Frequency, Monetary

        Segments customers based on:
        - Recency: How recently did they purchase?
        - Frequency: How often do they purchase?
        - Monetary: How much do they spend?
        """
        df = customer_df.copy()

        # Only analyze customers with at least one purchase
        df = df[df['total_orders'] > 0].copy()

        if len(df) == 0:
            return pd.DataFrame()

        # Calculate RFM scores (1-5, where 5 is best)
        # Use rank-based scoring as fallback if qcut fails
        try:
            df['R_score'] = pd.qcut(df['recency_days'], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop').astype(int)
        except (ValueError, TypeError):
            df['R_score'] = pd.cut(df['recency_days'], bins=5, labels=[5, 4, 3, 2, 1]).astype(int)

        try:
            df['F_score'] = pd.qcut(df['total_orders'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop').astype(int)
        except (ValueError, TypeError):
            # Rank-based scoring
            df['F_score'] = pd.cut(df['total_orders'].rank(method='first'), bins=5, labels=[1, 2, 3, 4, 5]).astype(int)

        try:
            df['M_score'] = pd.qcut(df['total_revenue'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop').astype(int)
        except (ValueError, TypeError):
            df['M_score'] = pd.cut(df['total_revenue'].rank(method='first'), bins=5, labels=[1, 2, 3, 4, 5]).astype(int)

        # Calculate RFM score
        df['RFM_score'] = df['R_score'] + df['F_score'] + df['M_score']

        # Create segments
        def segment_rfm(row):
            r, f, m = row['R_score'], row['F_score'], row['M_score']

            if r >= 4 and f >= 4 and m >= 4:
                return 'Champions'
            elif r >= 3 and f >= 3 and m >= 3:
                return 'Loyal Customers'
            elif r >= 4 and f <= 2:
                return 'New Customers'
            elif r <= 2 and f >= 3 and m >= 3:
                return 'At Risk'
            elif r <= 2 and f <= 2:
                return 'Lost'
            elif m >= 4:
                return 'Big Spenders'
            else:
                return 'Promising'

        df['rfm_segment'] = df.apply(segment_rfm, axis=1)

        return df

    @staticmethod
    def cart_abandonment_analysis(sessions_df: pd.DataFrame) -> Dict:
        """Analyze cart abandonment patterns"""

        # Filter sessions with cart activity
        cart_sessions = sessions_df[sessions_df['added_to_cart'] == True].copy()

        if len(cart_sessions) == 0:
            return {
                'total_carts': 0,
                'abandoned_carts': 0,
                'abandonment_rate': 0,
                'by_device': pd.DataFrame(),
                'by_channel': pd.DataFrame(),
                'by_hour': pd.DataFrame()
            }

        total_carts = len(cart_sessions)
        abandoned_carts = cart_sessions['cart_abandoned'].sum()
        abandonment_rate = abandoned_carts / total_carts

        # Abandonment by device
        by_device = cart_sessions.groupby('device').agg({
            'cart_abandoned': ['sum', 'count']
        }).reset_index()
        by_device.columns = ['device', 'abandoned', 'total']
        by_device['abandonment_rate'] = by_device['abandoned'] / by_device['total']

        # Abandonment by channel
        by_channel = cart_sessions.groupby('channel').agg({
            'cart_abandoned': ['sum', 'count']
        }).reset_index()
        by_channel.columns = ['channel', 'abandoned', 'total']
        by_channel['abandonment_rate'] = by_channel['abandoned'] / by_channel['total']

        # Abandonment by hour
        by_hour = cart_sessions.groupby('session_hour').agg({
            'cart_abandoned': ['sum', 'count']
        }).reset_index()
        by_hour.columns = ['hour', 'abandoned', 'total']
        by_hour['abandonment_rate'] = by_hour['abandoned'] / by_hour['total']

        return {
            'total_carts': total_carts,
            'abandoned_carts': int(abandoned_carts),
            'abandonment_rate': abandonment_rate,
            'by_device': by_device,
            'by_channel': by_channel,
            'by_hour': by_hour
        }

    @staticmethod
    def product_performance_analysis(transactions_df: pd.DataFrame) -> pd.DataFrame:
        """Analyze product performance metrics"""

        if len(transactions_df) == 0:
            return pd.DataFrame()

        product_metrics = transactions_df.groupby(['product_id', 'product_name', 'category']).agg({
            'quantity': 'sum',
            'total_amount': 'sum',
            'transaction_id': 'nunique',
            'unit_price': 'first'
        }).reset_index()

        product_metrics.columns = ['product_id', 'product_name', 'category',
                                   'units_sold', 'revenue', 'num_orders', 'unit_price']

        # Calculate additional metrics
        total_revenue = product_metrics['revenue'].sum()
        product_metrics['revenue_share'] = product_metrics['revenue'] / total_revenue
        product_metrics['avg_quantity_per_order'] = product_metrics['units_sold'] / product_metrics['num_orders']

        # Sort by revenue
        product_metrics = product_metrics.sort_values('revenue', ascending=False)

        return product_metrics

    @staticmethod
    def customer_segmentation(customer_df: pd.DataFrame, n_clusters=4) -> Tuple[pd.DataFrame, Dict]:
        """
        K-Means clustering for customer segmentation
        """
        df = customer_df.copy()

        # Select features for clustering
        features = ['total_sessions', 'total_revenue', 'avg_order_value',
                   'conversion_rate', 'recency_days', 'avg_time_on_site']

        # Filter customers with purchases
        df_cluster = df[df['total_orders'] > 0].copy()

        if len(df_cluster) < n_clusters:
            return df, {}

        # Prepare data
        X = df_cluster[features].fillna(0)

        # Standardize
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # K-Means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        df_cluster['segment'] = kmeans.fit_predict(X_scaled)

        # Merge back
        df = df.merge(df_cluster[['customer_id', 'segment']], on='customer_id', how='left')
        df['segment'] = df['segment'].fillna(-1).astype(int)

        # Analyze segments
        segment_analysis = df_cluster.groupby('segment').agg({
            'customer_id': 'count',
            'total_revenue': 'mean',
            'avg_order_value': 'mean',
            'total_sessions': 'mean',
            'conversion_rate': 'mean',
            'recency_days': 'mean'
        }).round(2)

        segment_analysis.columns = ['customer_count', 'avg_revenue', 'avg_order_value',
                                   'avg_sessions', 'avg_conversion_rate', 'avg_recency_days']

        # Label segments
        segment_labels = {
            0: 'High Value Frequent',
            1: 'Occasional Buyers',
            2: 'New Potential',
            3: 'Dormant/At Risk'
        }

        # Sort by revenue and reassign labels
        segment_analysis = segment_analysis.sort_values('avg_revenue', ascending=False)
        segment_mapping = {old: new for new, old in enumerate(segment_analysis.index)}
        df['segment'] = df['segment'].map(segment_mapping).fillna(-1).astype(int)
        df['segment_name'] = df['segment'].map(segment_labels).fillna('No Purchase')

        return df, segment_analysis.to_dict()


class EcommerceVisualizer:
    """Create visualizations for e-commerce analytics"""

    @staticmethod
    def plot_clv_distribution(customer_df: pd.DataFrame) -> go.Figure:
        """Plot CLV distribution and segments"""

        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('CLV Distribution', 'CLV Segments'),
            specs=[[{'type': 'histogram'}, {'type': 'bar'}]]
        )

        # Histogram
        fig.add_trace(
            go.Histogram(x=customer_df['total_clv'], nbinsx=50, name='CLV Distribution',
                        marker_color='lightblue'),
            row=1, col=1
        )

        # Segments
        segment_counts = customer_df['clv_segment'].value_counts()
        fig.add_trace(
            go.Bar(x=segment_counts.index, y=segment_counts.values,
                  marker_color=['#ff6b6b', '#ffd93d', '#6bcf7f', '#4d96ff'],
                  name='Customer Count'),
            row=1, col=2
        )

        fig.update_layout(
            title_text='Customer Lifetime Value Analysis',
            showlegend=False,
            height=400
        )

        return fig

    @staticmethod
    def plot_rfm_segments(rfm_df: pd.DataFrame) -> go.Figure:
        """Plot RFM segment distribution"""

        segment_summary = rfm_df.groupby('rfm_segment').agg({
            'customer_id': 'count',
            'total_revenue': 'sum'
        }).reset_index()
        segment_summary.columns = ['segment', 'customer_count', 'total_revenue']
        segment_summary = segment_summary.sort_values('total_revenue', ascending=False)

        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Customers by Segment', 'Revenue by Segment'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}]]
        )

        # Customer count
        fig.add_trace(
            go.Bar(x=segment_summary['segment'], y=segment_summary['customer_count'],
                  marker_color='lightcoral', name='Customers'),
            row=1, col=1
        )

        # Revenue
        fig.add_trace(
            go.Bar(x=segment_summary['segment'], y=segment_summary['total_revenue'],
                  marker_color='lightseagreen', name='Revenue'),
            row=1, col=2
        )

        fig.update_layout(
            title_text='RFM Segment Analysis',
            showlegend=False,
            height=400
        )

        return fig

    @staticmethod
    def plot_cart_abandonment(abandonment_data: Dict) -> go.Figure:
        """Plot cart abandonment analysis"""

        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Abandonment by Device', 'Abandonment by Hour'),
            specs=[[{'type': 'bar'}, {'type': 'scatter'}]]
        )

        # By device
        by_device = abandonment_data['by_device']
        fig.add_trace(
            go.Bar(x=by_device['device'], y=by_device['abandonment_rate'] * 100,
                  marker_color='orange', name='Abandonment Rate'),
            row=1, col=1
        )

        # By hour
        by_hour = abandonment_data['by_hour']
        fig.add_trace(
            go.Scatter(x=by_hour['hour'], y=by_hour['abandonment_rate'] * 100,
                      mode='lines+markers', marker_color='red', name='Abandonment Rate'),
            row=1, col=2
        )

        fig.update_yaxes(title_text='Abandonment Rate (%)', row=1, col=1)
        fig.update_yaxes(title_text='Abandonment Rate (%)', row=1, col=2)
        fig.update_xaxes(title_text='Hour of Day', row=1, col=2)

        fig.update_layout(
            title_text=f'Cart Abandonment Analysis (Overall Rate: {abandonment_data["abandonment_rate"]*100:.1f}%)',
            showlegend=False,
            height=400
        )

        return fig

    @staticmethod
    def plot_product_performance(product_df: pd.DataFrame) -> go.Figure:
        """Plot product performance metrics"""

        top_products = product_df.head(10)

        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Top 10 Products by Revenue', 'Revenue Share by Category'),
            specs=[[{'type': 'bar'}, {'type': 'pie'}]]
        )

        # Top products
        fig.add_trace(
            go.Bar(x=top_products['product_name'], y=top_products['revenue'],
                  marker_color='mediumseagreen', name='Revenue'),
            row=1, col=1
        )

        # Category breakdown
        category_revenue = product_df.groupby('category')['revenue'].sum()
        fig.add_trace(
            go.Pie(labels=category_revenue.index, values=category_revenue.values,
                  name='Category Revenue'),
            row=1, col=2
        )

        fig.update_xaxes(tickangle=-45, row=1, col=1)
        fig.update_layout(
            title_text='Product Performance Analysis',
            showlegend=False,
            height=400
        )

        return fig

    @staticmethod
    def plot_customer_segments(customer_df: pd.DataFrame) -> go.Figure:
        """Plot customer segmentation results"""

        segment_data = customer_df[customer_df['segment'] >= 0]

        fig = px.scatter(
            segment_data,
            x='total_sessions',
            y='total_revenue',
            color='segment_name',
            size='avg_order_value',
            hover_data=['customer_id', 'conversion_rate', 'recency_days'],
            title='Customer Segmentation (K-Means Clustering)',
            labels={
                'total_sessions': 'Total Sessions',
                'total_revenue': 'Total Revenue ($)',
                'segment_name': 'Segment'
            }
        )

        fig.update_layout(height=500)

        return fig


# Convenience function for complete analysis
def run_complete_analysis():
    """
    Run complete e-commerce analysis pipeline
    Returns all datasets and analysis results
    """
    print("Generating synthetic e-commerce data...")
    generator = EcommerceDataGenerator(seed=42)
    sessions_df, events_df, transactions_df = generator.generate_dataset(
        visits_per_month=25000,
        months=2
    )

    print("Cleaning and wrangling data...")
    cleaner = EcommerceDataCleaner()
    sessions_clean = cleaner.clean_sessions(sessions_df)
    transactions_clean = cleaner.clean_transactions(transactions_df)
    customer_df = cleaner.create_customer_summary(sessions_clean, transactions_clean)

    print("Running analytics...")
    analytics = EcommerceAnalytics()

    # 1. CLV Analysis
    customer_clv = analytics.calculate_clv(customer_df)

    # 2. RFM Analysis
    customer_rfm = analytics.rfm_analysis(customer_df)

    # 3. Cart Abandonment
    abandonment_data = analytics.cart_abandonment_analysis(sessions_clean)

    # 4. Product Performance
    product_performance = analytics.product_performance_analysis(transactions_clean)

    # 5. Customer Segmentation
    customer_segments, segment_analysis = analytics.customer_segmentation(customer_df)

    print("Analysis complete!")

    return {
        'sessions': sessions_clean,
        'events': events_df,
        'transactions': transactions_clean,
        'customers': customer_df,
        'customer_clv': customer_clv,
        'customer_rfm': customer_rfm,
        'abandonment': abandonment_data,
        'products': product_performance,
        'segments': customer_segments,
        'segment_analysis': segment_analysis
    }


if __name__ == '__main__':
    # Test the module
    results = run_complete_analysis()
    print("\nSummary Statistics:")
    print(f"Total Sessions: {len(results['sessions']):,}")
    print(f"Total Transactions: {len(results['transactions']):,}")
    print(f"Total Customers: {len(results['customers']):,}")
    print(f"Total Revenue: ${results['transactions']['total_amount'].sum():,.2f}")
    print(f"Conversion Rate: {(results['sessions']['converted'].sum() / len(results['sessions']) * 100):.2f}%")
    print(f"Cart Abandonment Rate: {results['abandonment']['abandonment_rate']*100:.1f}%")
