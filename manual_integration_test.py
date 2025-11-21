"""
Manual Integration Test - Simulates Full User Workflow
Tests all app functions without Streamlit runtime
"""

import sys
sys.path.insert(0, '.')

from app import generate_demo_data, perform_clustering, detect_trends, detect_anomalies
import pandas as pd
import traceback

print("="*70)
print("MANUAL INTEGRATION TEST - SIMULATING USER WORKFLOW")
print("="*70)

errors_found = []
warnings_found = []

# STEP 1: User clicks "Connect to Demo"
print("\nSTEP 1: User clicks 'Connect to Demo'")
print("-" * 70)
try:
    df = generate_demo_data(90)
    print(f"[SUCCESS] Generated {len(df)} days of demo data")
    print(f"          Columns: {list(df.columns)}")
    print(f"          Date range: {df['date'].min()} to {df['date'].max()}")
except Exception as e:
    print(f"[ERROR] Failed to generate demo data: {e}")
    errors_found.append({"step": "Demo Data Generation", "error": str(e), "traceback": traceback.format_exc()})
    sys.exit(1)

# STEP 2: User views Overview tab
print("\nSTEP 2: User views Overview tab")
print("-" * 70)
try:
    # Calculate metrics (as shown in app)
    total_sessions = df['sessions'].sum()
    total_users = df['totalUsers'].sum()
    total_conversions = df['conversions'].sum()
    total_revenue = df['revenue'].sum()

    print(f"[SUCCESS] Overview metrics calculated:")
    print(f"          Total Sessions: {total_sessions:,}")
    print(f"          Total Users: {total_users:,}")
    print(f"          Total Conversions: {total_conversions:,}")
    print(f"          Total Revenue: ${total_revenue:,.2f}")

    # Test CSV export
    csv_data = df.to_csv(index=False)
    print(f"[SUCCESS] CSV export prepared ({len(csv_data)} bytes)")

except Exception as e:
    print(f"[ERROR] Overview tab failed: {e}")
    errors_found.append({"step": "Overview Tab", "error": str(e), "traceback": traceback.format_exc()})

# STEP 3: User goes to Clustering tab and runs analysis
print("\nSTEP 3: User goes to Clustering tab, selects 3 clusters, clicks 'Run Clustering'")
print("-" * 70)
try:
    n_clusters = 3
    df_clustered, cluster_stats = perform_clustering(df.copy(), n_clusters)

    print(f"[SUCCESS] Clustering completed")
    print(f"          Clusters created: {df_clustered['cluster'].nunique()}")
    print(f"          Cluster names: {df_clustered['cluster_name'].unique().tolist()}")
    print(f"\n          Cluster Statistics:")
    print(f"          {cluster_stats.to_string()}")

    # Verify cluster assignments
    if 'cluster' not in df_clustered.columns:
        errors_found.append({"step": "Clustering", "error": "Missing cluster column", "traceback": ""})
        print("[ERROR] Missing 'cluster' column after clustering")
    elif 'cluster_name' not in df_clustered.columns:
        errors_found.append({"step": "Clustering", "error": "Missing cluster_name column", "traceback": ""})
        print("[ERROR] Missing 'cluster_name' column after clustering")
    else:
        print(f"[SUCCESS] Cluster columns verified")

except Exception as e:
    print(f"[ERROR] Clustering tab failed: {e}")
    errors_found.append({"step": "Clustering Tab", "error": str(e), "traceback": traceback.format_exc()})

# STEP 4: User goes to Trends tab
print("\nSTEP 4: User views Trends tab")
print("-" * 70)
try:
    trend_results = detect_trends(df)

    print(f"[SUCCESS] Trend detection completed")
    print(f"          Direction: {trend_results['direction']}")
    print(f"          Growth Rate: {trend_results['growth_rate']:.2f}%")
    print(f"          Daily Change: {trend_results['slope']:.2f} sessions/day")
    print(f"          Trend line points: {len(trend_results['trend_line'])}")

    # Verify all required fields present
    required_fields = ['direction', 'color', 'slope', 'growth_rate', 'trend_line']
    missing_fields = [f for f in required_fields if f not in trend_results]

    if missing_fields:
        print(f"[ERROR] Missing required fields: {missing_fields}")
        errors_found.append({"step": "Trends", "error": f"Missing fields: {missing_fields}", "traceback": ""})
    else:
        print(f"[SUCCESS] All trend fields present")

except Exception as e:
    print(f"[ERROR] Trends tab failed: {e}")
    errors_found.append({"step": "Trends Tab", "error": str(e), "traceback": traceback.format_exc()})

# STEP 5: User goes to Anomalies tab (THE CRITICAL BUG TEST)
print("\nSTEP 5: User views Anomalies tab")
print("-" * 70)
try:
    # This is where the bug was - we need to keep reference to modified df
    df_anomaly = df.copy()
    anomalies, lower, upper = detect_anomalies(df_anomaly)

    print(f"[SUCCESS] Anomaly detection completed")
    print(f"          Anomalies detected: {len(anomalies)}")
    print(f"          Lower threshold: {lower:.2f}")
    print(f"          Upper threshold: {upper:.2f}")

    # Critical test: Check if is_anomaly column exists
    if 'is_anomaly' not in df_anomaly.columns:
        print(f"[ERROR] Missing 'is_anomaly' column - BUG STILL EXISTS!")
        errors_found.append({"step": "Anomalies", "error": "Missing is_anomaly column", "traceback": ""})
    else:
        print(f"[SUCCESS] 'is_anomaly' column exists in dataframe")

        # Test visualization data preparation (as in app.py)
        normal_data = df_anomaly[~df_anomaly['is_anomaly']]
        anomaly_data = df_anomaly[df_anomaly['is_anomaly']]

        print(f"          Normal data points: {len(normal_data)}")
        print(f"          Anomaly data points: {len(anomaly_data)}")

        if len(anomalies) > 0:
            print(f"\n          Sample anomalies:")
            for _, row in anomalies.head(3).iterrows():
                print(f"          - {row['date'].strftime('%Y-%m-%d')}: {row['sessions']:.0f} sessions")

        print(f"[SUCCESS] Anomaly visualization data prepared without errors")

except Exception as e:
    print(f"[ERROR] Anomalies tab failed: {e}")
    errors_found.append({"step": "Anomalies Tab", "error": str(e), "traceback": traceback.format_exc()})
    print(f"          Traceback: {traceback.format_exc()}")

# STEP 6: Test with different cluster counts
print("\nSTEP 6: User tries different cluster counts (2, 4, 5)")
print("-" * 70)
for n in [2, 4, 5]:
    try:
        df_test, stats = perform_clustering(df.copy(), n_clusters=n)
        actual_clusters = df_test['cluster'].nunique()

        if actual_clusters == n:
            print(f"[SUCCESS] {n}-cluster analysis: Created {actual_clusters} clusters")
        else:
            print(f"[WARNING] {n}-cluster requested but got {actual_clusters} clusters")
            warnings_found.append({"step": f"{n}-cluster analysis", "warning": f"Mismatch: requested {n}, got {actual_clusters}"})

    except Exception as e:
        print(f"[ERROR] {n}-cluster analysis failed: {e}")
        errors_found.append({"step": f"{n}-cluster analysis", "error": str(e), "traceback": traceback.format_exc()})

# STEP 7: Test edge cases
print("\nSTEP 7: Testing edge cases")
print("-" * 70)

# Test with very small dataset
try:
    small_df = generate_demo_data(7)
    df_small_clust, _ = perform_clustering(small_df.copy(), n_clusters=2)
    trend_small = detect_trends(small_df)
    anomalies_small, _, _ = detect_anomalies(small_df.copy())
    print(f"[SUCCESS] Small dataset (7 days) processed successfully")
except Exception as e:
    print(f"[ERROR] Small dataset failed: {e}")
    errors_found.append({"step": "Small dataset", "error": str(e), "traceback": traceback.format_exc()})

# Test with large dataset
try:
    large_df = generate_demo_data(365)
    df_large_clust, _ = perform_clustering(large_df.copy(), n_clusters=4)
    trend_large = detect_trends(large_df)
    anomalies_large, _, _ = detect_anomalies(large_df.copy())
    print(f"[SUCCESS] Large dataset (365 days) processed successfully")
except Exception as e:
    print(f"[ERROR] Large dataset failed: {e}")
    errors_found.append({"step": "Large dataset", "error": str(e), "traceback": traceback.format_exc()})

# FINAL REPORT
print("\n" + "="*70)
print("INTEGRATION TEST SUMMARY")
print("="*70)

print(f"\nTotal Errors: {len(errors_found)}")
print(f"Total Warnings: {len(warnings_found)}")

if errors_found:
    print("\n" + "="*70)
    print("ERRORS DETAIL:")
    print("="*70)
    for i, error in enumerate(errors_found, 1):
        print(f"\n{i}. {error['step']}")
        print(f"   Error: {error['error']}")
        if error['traceback']:
            print(f"   Traceback:\n{error['traceback']}")

if warnings_found:
    print("\n" + "="*70)
    print("WARNINGS DETAIL:")
    print("="*70)
    for i, warning in enumerate(warnings_found, 1):
        print(f"\n{i}. {warning['step']}")
        print(f"   Warning: {warning['warning']}")

if not errors_found and not warnings_found:
    print("\n[SUCCESS] ALL TESTS PASSED - Application is working correctly!")
    print("          User can successfully navigate all tabs and perform all operations.")
    sys.exit(0)
elif not errors_found:
    print("\n[SUCCESS] All critical tests passed (warnings present)")
    sys.exit(0)
else:
    print("\n[FAILURE] Critical errors found - see details above")
    sys.exit(1)
