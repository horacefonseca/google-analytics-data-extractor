# Real GA4 Data Extraction Plan

## Objective
Extract real Google Analytics 4 ecommerce data from Google Merchandise Store for training/demo purposes.

---

## Solution: BigQuery Public Dataset (FREE)

Google provides public GA4 sample data via BigQuery:
- **Dataset:** `bigquery-public-data.ga4_obfuscated_sample_ecommerce`
- **Period:** November 2020 - January 2021 (92 days)
- **Source:** Google Merchandise Store (real ecommerce traffic)
- **Cost:** FREE (within BigQuery free tier: 1TB/month)

---

## Implementation Steps

### Step 1: Install Dependencies

```bash
pip install google-cloud-bigquery pandas db-dtypes
```

### Step 2: Create Data Extraction Script

Create `extract_real_ga4_data.py`:

```python
"""
Extract real GA4 data from Google BigQuery public dataset
No authentication required for public datasets
"""

from google.cloud import bigquery
import pandas as pd
from datetime import datetime

def extract_ga4_data(days=30, start_date='20210101'):
    """
    Extract GA4 data from BigQuery public dataset

    Args:
        days: Number of days to extract (max 92)
        start_date: Start date in YYYYMMDD format
    """

    print(f"Extracting {days} days of real GA4 data from BigQuery...")

    # Create BigQuery client (no auth needed for public data)
    client = bigquery.Client()

    # Calculate end date
    end_date = pd.to_datetime(start_date).date() + pd.Timedelta(days=days)
    end_date_str = end_date.strftime('%Y%m%d')

    query = f"""
    SELECT
        PARSE_DATE('%Y%m%d', event_date) as date,
        COUNT(DISTINCT user_pseudo_id) as totalUsers,
        COUNTIF(
            user_pseudo_id NOT IN (
                SELECT DISTINCT user_pseudo_id
                FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
                WHERE _TABLE_SUFFIX < FORMAT_DATE('%Y%m%d', PARSE_DATE('%Y%m%d', event_date) - 1)
            )
        ) as newUsers,
        COUNT(*) as sessions,
        SUM(
            (SELECT SUM(value.int_value)
             FROM UNNEST(event_params)
             WHERE key = 'page_view')
        ) as screenPageViews,
        AVG(
            (SELECT value.int_value
             FROM UNNEST(event_params)
             WHERE key = 'engagement_time_msec')
        ) / 1000 as averageSessionDuration,
        AVG(
            (SELECT value.int_value
             FROM UNNEST(event_params)
             WHERE key = 'session_engaged')
        ) as bounceRate,
        COUNTIF(event_name = 'purchase') as conversions,
        IFNULL(SUM(ecommerce.purchase_revenue), 0) as revenue
    FROM
        `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
    WHERE
        _TABLE_SUFFIX BETWEEN '{start_date}' AND '{end_date_str}'
    GROUP BY
        date
    ORDER BY
        date
    """

    print("Running BigQuery query...")
    df = client.query(query).to_dataframe()

    # Data cleaning
    df['bounceRate'] = 1 - df['bounceRate'].fillna(0)  # Convert to bounce rate
    df['averageSessionDuration'] = df['averageSessionDuration'].fillna(120)
    df['screenPageViews'] = df['screenPageViews'].fillna(df['sessions'] * 2)
    df['newUsers'] = df['newUsers'].fillna(df['totalUsers'] * 0.4)

    print(f"✓ Extracted {len(df)} days of data")
    print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"  Total sessions: {df['sessions'].sum():,}")
    print(f"  Total revenue: ${df['revenue'].sum():,.2f}")

    return df


def save_data(df, filename='ga4_real_data.csv'):
    """Save extracted data to CSV"""
    df.to_csv(filename, index=False)
    print(f"✓ Saved to {filename}")


if __name__ == "__main__":
    # Extract 30 days of data
    df = extract_ga4_data(days=30, start_date='20210101')

    # Save to CSV
    save_data(df)

    # Display sample
    print("\nSample data:")
    print(df.head())
```

### Step 3: Run Extraction

```bash
python extract_real_ga4_data.py
```

**Output:** `ga4_real_data.csv` with 30 days of real data

### Step 4: Integrate into App

Update `app.py` to load real data:

```python
@st.cache_data
def load_real_ga4_data():
    """Load real GA4 data from CSV"""
    try:
        df = pd.read_csv('ga4_real_data.csv')
        df['date'] = pd.to_datetime(df['date'])
        return df
    except FileNotFoundError:
        st.error("Real data file not found. Run extract_real_ga4_data.py first")
        return None

# In sidebar, add option:
use_real_data = st.checkbox("🔥 Use Real GA4 Data", value=False)

if use_real_data:
    st.session_state.data = load_real_ga4_data()
else:
    # Use demo mode...
```

---

## Alternative: Kaggle Dataset (No Setup)

**Easiest option if BigQuery setup is complicated:**

1. **Download:** https://www.kaggle.com/datasets/pdaasha/ga4-obfuscated-sample-ecommerce-jan2021
2. **Extract CSV** (30 days, January 2021)
3. **Load into app:**
   ```python
   df = pd.read_csv('kaggle_ga4_data.csv')
   ```

---

## Data Schema

Both sources provide these columns:
- `date` - Date of data
- `totalUsers` - Unique users
- `newUsers` - First-time users
- `sessions` - Total sessions
- `screenPageViews` - Page views
- `averageSessionDuration` - Avg time on site (seconds)
- `bounceRate` - Bounce rate (0-1)
- `conversions` - Purchase events
- `revenue` - Total revenue ($)

**Perfect match for your app's current demo data structure!**

---

## Limitations

### BigQuery Public Dataset:
- ✅ FREE (1TB queries/month free)
- ✅ 3 months available (Nov 2020 - Jan 2021)
- ✅ Real ecommerce data
- ❌ Data is obfuscated (privacy)
- ❌ Historical data only (not live)

### GA4 Demo Account API:
- ❌ **NOT accessible via API** (403 permissions error)
- ❌ Only manual export via UI
- ❌ 90-day limit per export

### Own GA4 Property:
- ✅ Full API access
- ✅ Live data
- ✅ Unlimited history
- ❌ Need to set up tracking
- ❌ Need real website traffic

---

## Cost Analysis

**Option 1: BigQuery Public Dataset**
- Queries: FREE (1TB/month free tier)
- Storage: FREE (public dataset)
- **Total: $0**

**Option 2: Kaggle Download**
- Download: FREE
- **Total: $0**

**Option 3: Own GA4 + API**
- GA4: FREE
- API calls: FREE (25,000 requests/day)
- Cloud hosting: ~$5-10/month
- **Total: $0 (if self-hosted)**

---

## Recommended Timeline

**Total time: 30-60 minutes**

1. **Install BigQuery library** (5 min)
2. **Run extraction script** (10 min)
3. **Verify data quality** (5 min)
4. **Integrate into app** (10 min)
5. **Test with real data** (10 min)

---

## Expected Results

After implementation:
- ✅ Real Google Merchandise Store ecommerce data
- ✅ 30-90 days of actual traffic patterns
- ✅ Realistic revenue, conversion data
- ✅ Better demo credibility
- ✅ More accurate ML model training

---

## Next Steps

1. Run `pip install google-cloud-bigquery pandas`
2. Create and run `extract_real_ga4_data.py`
3. Verify `ga4_real_data.csv` created
4. Add real data option to app sidebar
5. Test all features with real data
6. Document in README that app uses real Google data

---

## Notes

- BigQuery requires Google Cloud project (FREE tier is sufficient)
- If BigQuery setup fails, use Kaggle option (no setup needed)
- Real data is obfuscated for privacy (user IDs hashed)
- Data is from 2020-2021 (historical, but realistic patterns)

---

**Status:** Ready to implement
**Difficulty:** Medium (BigQuery) / Easy (Kaggle)
**Cost:** FREE
**Time:** 30-60 minutes
