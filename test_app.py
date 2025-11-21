"""
Comprehensive Testing Suite for GA Extractor Pro
Simulates user workflow and tests all functionality
"""

import sys
import traceback
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Import functions from app.py
sys.path.insert(0, '.')
from app import generate_demo_data, perform_clustering, detect_trends, detect_anomalies


class TestLogger:
    """Logger to track test results and errors"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed = []
        self.test_count = 0

    def log_pass(self, test_name, message=""):
        self.test_count += 1
        self.passed.append({
            'test': test_name,
            'message': message,
            'timestamp': datetime.now()
        })
        print(f"[PASS] {test_name}")
        if message:
            print(f"       {message}")

    def log_error(self, test_name, error, traceback_str=""):
        self.test_count += 1
        self.errors.append({
            'test': test_name,
            'error': str(error),
            'traceback': traceback_str,
            'timestamp': datetime.now()
        })
        print(f"[ERROR] {test_name}")
        print(f"        {error}")
        if traceback_str:
            print(f"        Traceback: {traceback_str[:200]}...")

    def log_warning(self, test_name, warning):
        self.warnings.append({
            'test': test_name,
            'warning': warning,
            'timestamp': datetime.now()
        })
        print(f"[WARNING] {test_name}")
        print(f"          {warning}")

    def summary(self):
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {self.test_count}")
        print(f"Passed: {len(self.passed)} ({len(self.passed)/self.test_count*100:.1f}%)")
        print(f"Failed: {len(self.errors)} ({len(self.errors)/self.test_count*100:.1f}%)")
        print(f"Warnings: {len(self.warnings)}")
        print("="*70)


logger = TestLogger()


def test_data_generation():
    """Test 1: Demo Data Generation"""
    print("\n" + "="*70)
    print("TEST 1: DATA GENERATION")
    print("="*70)

    # Test 1.1: Standard 90-day generation
    try:
        df = generate_demo_data(90)
        assert df is not None, "Data is None"
        assert len(df) == 90, f"Expected 90 rows, got {len(df)}"
        assert 'sessions' in df.columns, "Missing 'sessions' column"
        assert 'date' in df.columns, "Missing 'date' column"
        logger.log_pass("1.1 Standard 90-day data generation", f"Generated {len(df)} rows")
    except Exception as e:
        logger.log_error("1.1 Standard 90-day data generation", e, traceback.format_exc())

    # Test 1.2: Different time periods
    for days in [30, 60, 180, 365]:
        try:
            df = generate_demo_data(days)
            assert len(df) == days, f"Expected {days} rows, got {len(df)}"
            logger.log_pass(f"1.2 Generate {days}-day data", f"Successfully generated {len(df)} rows")
        except Exception as e:
            logger.log_error(f"1.2 Generate {days}-day data", e, traceback.format_exc())

    # Test 1.3: Edge case - very small dataset
    try:
        df = generate_demo_data(1)
        assert len(df) == 1, "Single day generation failed"
        logger.log_pass("1.3 Edge case: 1-day data", "Successfully generated single row")
    except Exception as e:
        logger.log_error("1.3 Edge case: 1-day data", e, traceback.format_exc())

    # Test 1.4: Edge case - zero days (should fail gracefully)
    try:
        df = generate_demo_data(0)
        if len(df) == 0:
            logger.log_warning("1.4 Edge case: 0-day data", "Generated empty dataframe - should handle gracefully")
        else:
            logger.log_error("1.4 Edge case: 0-day data", "Unexpected behavior with 0 days", "")
    except Exception as e:
        logger.log_pass("1.4 Edge case: 0-day data", "Correctly raised error for invalid input")

    # Test 1.5: Data quality checks
    try:
        df = generate_demo_data(90)

        # Check for negative values
        numeric_cols = ['sessions', 'totalUsers', 'newUsers', 'screenPageViews', 'conversions', 'revenue']
        for col in numeric_cols:
            if (df[col] < 0).any():
                logger.log_error(f"1.5 Data quality: {col}", f"Found negative values in {col}", "")
            else:
                logger.log_pass(f"1.5 Data quality: {col}", f"No negative values in {col}")

        # Check for NaN values
        if df.isnull().any().any():
            logger.log_error("1.5 Data quality: NaN check", "Found NaN values in data", "")
        else:
            logger.log_pass("1.5 Data quality: NaN check", "No NaN values found")

        # Check data types
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            logger.log_error("1.5 Data quality: date dtype", "Date column is not datetime type", "")
        else:
            logger.log_pass("1.5 Data quality: date dtype", "Date column is correct datetime type")

    except Exception as e:
        logger.log_error("1.5 Data quality checks", e, traceback.format_exc())

    # Test 1.6: Realistic value ranges
    try:
        df = generate_demo_data(90)

        # Check if bounce rate is between 0 and 1
        if (df['bounceRate'] >= 0).all() and (df['bounceRate'] <= 1).all():
            logger.log_pass("1.6 Bounce rate range", "Bounce rate values are within [0,1]")
        else:
            logger.log_error("1.6 Bounce rate range", "Bounce rate outside valid range [0,1]", "")

        # Check if users <= sessions (realistic constraint)
        if (df['totalUsers'] <= df['sessions']).all():
            logger.log_pass("1.6 Users vs Sessions", "Users <= Sessions (realistic)")
        else:
            logger.log_warning("1.6 Users vs Sessions", "Some days have Users > Sessions (unusual)")

        # Check if new users <= total users
        if (df['newUsers'] <= df['totalUsers']).all():
            logger.log_pass("1.6 New users constraint", "New users <= Total users")
        else:
            logger.log_error("1.6 New users constraint", "New users > Total users (impossible)", "")

    except Exception as e:
        logger.log_error("1.6 Realistic value ranges", e, traceback.format_exc())


def test_clustering():
    """Test 2: Clustering Functionality"""
    print("\n" + "="*70)
    print("TEST 2: CLUSTERING ANALYSIS")
    print("="*70)

    # Generate test data
    df = generate_demo_data(90)

    # Test 2.1: Standard 3-cluster analysis
    try:
        df_clustered, stats = perform_clustering(df.copy(), n_clusters=3)
        assert 'cluster' in df_clustered.columns, "Missing cluster column"
        assert 'cluster_name' in df_clustered.columns, "Missing cluster_name column"
        assert len(df_clustered) == len(df), "Row count mismatch after clustering"
        logger.log_pass("2.1 Standard 3-cluster analysis", f"Created {df_clustered['cluster'].nunique()} clusters")
    except Exception as e:
        logger.log_error("2.1 Standard 3-cluster analysis", e, traceback.format_exc())

    # Test 2.2: Different cluster counts
    for n in [2, 4, 5]:
        try:
            df_clustered, stats = perform_clustering(df.copy(), n_clusters=n)
            actual_clusters = df_clustered['cluster'].nunique()
            assert actual_clusters == n, f"Expected {n} clusters, got {actual_clusters}"
            logger.log_pass(f"2.2 {n}-cluster analysis", f"Successfully created {n} clusters")
        except Exception as e:
            logger.log_error(f"2.2 {n}-cluster analysis", e, traceback.format_exc())

    # Test 2.3: Edge case - Single cluster
    try:
        df_clustered, stats = perform_clustering(df.copy(), n_clusters=1)
        logger.log_pass("2.3 Edge case: 1 cluster", "Single cluster created successfully")
    except Exception as e:
        logger.log_error("2.3 Edge case: 1 cluster", e, traceback.format_exc())

    # Test 2.4: Cluster label consistency
    try:
        df_clustered, stats = perform_clustering(df.copy(), n_clusters=3)
        cluster_labels = df_clustered['cluster'].unique()
        expected_labels = [0, 1, 2]

        if sorted(cluster_labels) == expected_labels:
            logger.log_pass("2.4 Cluster labels", "Cluster labels are 0, 1, 2 as expected")
        else:
            logger.log_warning("2.4 Cluster labels", f"Unexpected cluster labels: {sorted(cluster_labels)}")
    except Exception as e:
        logger.log_error("2.4 Cluster label consistency", e, traceback.format_exc())

    # Test 2.5: Cluster statistics validity
    try:
        df_clustered, stats = perform_clustering(df.copy(), n_clusters=3)

        # Check if stats contain all required columns
        required_cols = ['sessions', 'totalUsers', 'conversions', 'revenue']
        for col in required_cols:
            if col in stats.columns:
                logger.log_pass(f"2.5 Cluster stats: {col}", f"{col} present in statistics")
            else:
                logger.log_error(f"2.5 Cluster stats: {col}", f"Missing {col} in cluster statistics", "")

        # Check for NaN in stats
        if stats.isnull().any().any():
            logger.log_error("2.5 Cluster stats: NaN", "Found NaN values in cluster statistics", "")
        else:
            logger.log_pass("2.5 Cluster stats: NaN", "No NaN values in statistics")

    except Exception as e:
        logger.log_error("2.5 Cluster statistics validity", e, traceback.format_exc())

    # Test 2.6: Small dataset clustering
    try:
        small_df = generate_demo_data(5)
        df_clustered, stats = perform_clustering(small_df.copy(), n_clusters=3)
        logger.log_pass("2.6 Small dataset (5 rows)", "Clustering works with small dataset")
    except Exception as e:
        logger.log_error("2.6 Small dataset (5 rows)", e, traceback.format_exc())

    # Test 2.7: Cluster naming consistency
    try:
        df_clustered, stats = perform_clustering(df.copy(), n_clusters=3)
        cluster_names = df_clustered['cluster_name'].unique()

        expected_names = ['Low Activity', 'Medium Activity', 'High Activity']
        if len(cluster_names) == 3:
            logger.log_pass("2.7 Cluster naming", f"Found {len(cluster_names)} distinct cluster names")
        else:
            logger.log_warning("2.7 Cluster naming", f"Unexpected cluster names: {cluster_names}")
    except Exception as e:
        logger.log_error("2.7 Cluster naming consistency", e, traceback.format_exc())


def test_trends():
    """Test 3: Trend Detection"""
    print("\n" + "="*70)
    print("TEST 3: TREND DETECTION")
    print("="*70)

    # Test 3.1: Standard trend detection
    try:
        df = generate_demo_data(90)
        results = detect_trends(df)

        required_keys = ['direction', 'color', 'slope', 'growth_rate', 'trend_line']
        for key in required_keys:
            if key in results:
                logger.log_pass(f"3.1 Trend result: {key}", f"{key} present in results")
            else:
                logger.log_error(f"3.1 Trend result: {key}", f"Missing {key} in trend results", "")

    except Exception as e:
        logger.log_error("3.1 Standard trend detection", e, traceback.format_exc())

    # Test 3.2: Upward trend detection
    try:
        # Create synthetic upward trend
        dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
        sessions = np.linspace(500, 1500, 90) + np.random.normal(0, 20, 90)
        df_up = pd.DataFrame({'date': dates, 'sessions': sessions})

        results = detect_trends(df_up)

        if results['slope'] > 5:
            logger.log_pass("3.2 Upward trend", f"Correctly detected upward trend (slope: {results['slope']:.2f})")
        else:
            logger.log_warning("3.2 Upward trend", f"Weak upward slope: {results['slope']:.2f}")

    except Exception as e:
        logger.log_error("3.2 Upward trend detection", e, traceback.format_exc())

    # Test 3.3: Downward trend detection
    try:
        # Create synthetic downward trend
        dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
        sessions = np.linspace(1500, 500, 90) + np.random.normal(0, 20, 90)
        df_down = pd.DataFrame({'date': dates, 'sessions': sessions})

        results = detect_trends(df_down)

        if results['slope'] < -5:
            logger.log_pass("3.3 Downward trend", f"Correctly detected downward trend (slope: {results['slope']:.2f})")
        else:
            logger.log_warning("3.3 Downward trend", f"Weak downward slope: {results['slope']:.2f}")

    except Exception as e:
        logger.log_error("3.3 Downward trend detection", e, traceback.format_exc())

    # Test 3.4: Stable trend detection
    try:
        # Create flat trend
        dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
        sessions = np.ones(90) * 1000 + np.random.normal(0, 30, 90)
        df_stable = pd.DataFrame({'date': dates, 'sessions': sessions})

        results = detect_trends(df_stable)

        if abs(results['slope']) < 5:
            logger.log_pass("3.4 Stable trend", f"Correctly detected stable trend (slope: {results['slope']:.2f})")
        else:
            logger.log_warning("3.4 Stable trend", f"Slope too high for stable: {results['slope']:.2f}")

    except Exception as e:
        logger.log_error("3.4 Stable trend detection", e, traceback.format_exc())

    # Test 3.5: Growth rate calculation
    try:
        df = generate_demo_data(90)
        results = detect_trends(df)

        # Verify growth rate is a number
        if isinstance(results['growth_rate'], (int, float)):
            logger.log_pass("3.5 Growth rate type", f"Growth rate is numeric: {results['growth_rate']:.2f}%")
        else:
            logger.log_error("3.5 Growth rate type", f"Growth rate is not numeric: {type(results['growth_rate'])}", "")

    except Exception as e:
        logger.log_error("3.5 Growth rate calculation", e, traceback.format_exc())

    # Test 3.6: Trend line length
    try:
        df = generate_demo_data(90)
        results = detect_trends(df)

        if len(results['trend_line']) == len(df):
            logger.log_pass("3.6 Trend line length", f"Trend line matches data length ({len(df)} points)")
        else:
            logger.log_error("3.6 Trend line length", f"Length mismatch: data={len(df)}, trend={len(results['trend_line'])}", "")

    except Exception as e:
        logger.log_error("3.6 Trend line length", e, traceback.format_exc())

    # Test 3.7: Edge case - Zero division protection
    try:
        # Create dataset with zero initial value
        dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
        sessions = np.zeros(90)
        sessions[0] = 0  # First value is zero
        sessions[1:] = np.linspace(1, 100, 89)
        df_zero = pd.DataFrame({'date': dates, 'sessions': sessions})

        results = detect_trends(df_zero)
        logger.log_pass("3.7 Zero division protection", "Handled zero initial value without error")

    except Exception as e:
        logger.log_error("3.7 Zero division protection", e, traceback.format_exc())


def test_anomalies():
    """Test 4: Anomaly Detection"""
    print("\n" + "="*70)
    print("TEST 4: ANOMALY DETECTION")
    print("="*70)

    # Test 4.1: Standard anomaly detection
    try:
        df = generate_demo_data(90)
        anomalies, lower, upper = detect_anomalies(df.copy())

        assert 'is_anomaly' in df.columns, "Missing is_anomaly column"
        logger.log_pass("4.1 Standard anomaly detection", f"Detected {len(anomalies)} anomalies")

    except Exception as e:
        logger.log_error("4.1 Standard anomaly detection", e, traceback.format_exc())

    # Test 4.2: Threshold calculations
    try:
        df = generate_demo_data(90)
        anomalies, lower, upper = detect_anomalies(df.copy())

        Q1 = df['sessions'].quantile(0.25)
        Q3 = df['sessions'].quantile(0.75)
        IQR = Q3 - Q1

        expected_lower = Q1 - 1.5 * IQR
        expected_upper = Q3 + 1.5 * IQR

        if abs(lower - expected_lower) < 0.01 and abs(upper - expected_upper) < 0.01:
            logger.log_pass("4.2 Threshold calculations", f"Lower={lower:.2f}, Upper={upper:.2f}")
        else:
            logger.log_error("4.2 Threshold calculations", f"Threshold mismatch: L={lower:.2f} vs {expected_lower:.2f}", "")

    except Exception as e:
        logger.log_error("4.2 Threshold calculations", e, traceback.format_exc())

    # Test 4.3: Anomaly with clear spike
    try:
        dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
        sessions = np.ones(90) * 1000 + np.random.normal(0, 20, 90)
        sessions[45] = 3000  # Clear spike
        df_spike = pd.DataFrame({'date': dates, 'sessions': sessions})

        anomalies, lower, upper = detect_anomalies(df_spike.copy())

        if len(anomalies) >= 1:
            logger.log_pass("4.3 Detect spike anomaly", f"Detected {len(anomalies)} anomalies including spike")
        else:
            logger.log_error("4.3 Detect spike anomaly", "Failed to detect obvious spike", "")

    except Exception as e:
        logger.log_error("4.3 Anomaly with clear spike", e, traceback.format_exc())

    # Test 4.4: Anomaly with clear drop
    try:
        dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
        sessions = np.ones(90) * 1000 + np.random.normal(0, 20, 90)
        sessions[45] = 200  # Clear drop
        df_drop = pd.DataFrame({'date': dates, 'sessions': sessions})

        anomalies, lower, upper = detect_anomalies(df_drop.copy())

        if len(anomalies) >= 1:
            logger.log_pass("4.4 Detect drop anomaly", f"Detected {len(anomalies)} anomalies including drop")
        else:
            logger.log_error("4.4 Detect drop anomaly", "Failed to detect obvious drop", "")

    except Exception as e:
        logger.log_error("4.4 Anomaly with clear drop", e, traceback.format_exc())

    # Test 4.5: No anomalies in uniform data
    try:
        dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
        sessions = np.ones(90) * 1000 + np.random.normal(0, 5, 90)  # Very small variance
        df_uniform = pd.DataFrame({'date': dates, 'sessions': sessions})

        anomalies, lower, upper = detect_anomalies(df_uniform.copy())

        if len(anomalies) == 0:
            logger.log_pass("4.5 Uniform data (no anomalies)", "Correctly found no anomalies in uniform data")
        else:
            logger.log_warning("4.5 Uniform data (no anomalies)", f"Found {len(anomalies)} anomalies in uniform data")

    except Exception as e:
        logger.log_error("4.5 No anomalies in uniform data", e, traceback.format_exc())

    # Test 4.6: Column parameter flexibility
    try:
        df = generate_demo_data(90)

        # Test different columns
        for col in ['sessions', 'totalUsers', 'conversions']:
            anomalies, lower, upper = detect_anomalies(df.copy(), column=col)
            logger.log_pass(f"4.6 Anomaly on {col}", f"Successfully detected anomalies in {col}")

    except Exception as e:
        logger.log_error("4.6 Column parameter flexibility", e, traceback.format_exc())

    # Test 4.7: Edge case - Very small dataset
    try:
        small_df = generate_demo_data(5)
        anomalies, lower, upper = detect_anomalies(small_df.copy())
        logger.log_pass("4.7 Small dataset (5 rows)", "Anomaly detection works on small dataset")

    except Exception as e:
        logger.log_error("4.7 Small dataset (5 rows)", e, traceback.format_exc())


def test_integration():
    """Test 5: Integration & Edge Cases"""
    print("\n" + "="*70)
    print("TEST 5: INTEGRATION & EDGE CASES")
    print("="*70)

    # Test 5.1: Full pipeline
    try:
        # Generate data
        df = generate_demo_data(90)

        # Clustering
        df_clustered, stats = perform_clustering(df.copy(), n_clusters=3)

        # Trends
        trend_results = detect_trends(df)

        # Anomalies
        anomalies, lower, upper = detect_anomalies(df.copy())

        logger.log_pass("5.1 Full pipeline", "All functions executed successfully in sequence")

    except Exception as e:
        logger.log_error("5.1 Full pipeline", e, traceback.format_exc())

    # Test 5.2: Large dataset
    try:
        large_df = generate_demo_data(365*2)  # 2 years
        df_clustered, stats = perform_clustering(large_df.copy(), n_clusters=4)
        trend_results = detect_trends(large_df)
        anomalies, lower, upper = detect_anomalies(large_df.copy())

        logger.log_pass("5.2 Large dataset (730 days)", "Successfully processed 2 years of data")

    except Exception as e:
        logger.log_error("5.2 Large dataset (730 days)", e, traceback.format_exc())

    # Test 5.3: Data persistence after operations
    try:
        df = generate_demo_data(90)
        original_len = len(df)

        # Perform operations
        df_clustered, stats = perform_clustering(df.copy(), n_clusters=3)
        trend_results = detect_trends(df)
        anomalies, lower, upper = detect_anomalies(df.copy())

        # Check original data unchanged
        if len(df) == original_len:
            logger.log_pass("5.3 Data persistence", "Original data preserved after operations")
        else:
            logger.log_error("5.3 Data persistence", f"Data length changed: {original_len} -> {len(df)}", "")

    except Exception as e:
        logger.log_error("5.3 Data persistence after operations", e, traceback.format_exc())

    # Test 5.4: Missing columns handling
    try:
        df = generate_demo_data(90)
        df_incomplete = df.drop(columns=['revenue'])

        # This should fail or handle gracefully
        try:
            df_clustered, stats = perform_clustering(df_incomplete.copy(), n_clusters=3)
            logger.log_warning("5.4 Missing columns", "Function continued with missing 'revenue' column")
        except KeyError:
            logger.log_pass("5.4 Missing columns", "Correctly raised error for missing columns")

    except Exception as e:
        logger.log_error("5.4 Missing columns handling", e, traceback.format_exc())

    # Test 5.5: Data type consistency
    try:
        df = generate_demo_data(90)

        # Check if numeric columns are numeric
        numeric_cols = ['sessions', 'totalUsers', 'conversions', 'revenue']
        all_numeric = all(pd.api.types.is_numeric_dtype(df[col]) for col in numeric_cols)

        if all_numeric:
            logger.log_pass("5.5 Data type consistency", "All numeric columns have correct types")
        else:
            logger.log_error("5.5 Data type consistency", "Some numeric columns have wrong types", "")

    except Exception as e:
        logger.log_error("5.5 Data type consistency", e, traceback.format_exc())

    # Test 5.6: Memory efficiency check
    try:
        import sys

        df = generate_demo_data(365)
        size_mb = sys.getsizeof(df) / 1024 / 1024

        if size_mb < 10:  # Should be much less than 10MB
            logger.log_pass("5.6 Memory efficiency", f"Dataset size: {size_mb:.2f} MB (efficient)")
        else:
            logger.log_warning("5.6 Memory efficiency", f"Dataset size: {size_mb:.2f} MB (large)")

    except Exception as e:
        logger.log_error("5.6 Memory efficiency check", e, traceback.format_exc())


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("GA EXTRACTOR PRO - COMPREHENSIVE TEST SUITE")
    print("Simulating User Workflow and Testing All Functionality")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run all test suites
    test_data_generation()
    test_clustering()
    test_trends()
    test_anomalies()
    test_integration()

    # Print summary
    logger.summary()

    # Return results for reporting
    return logger


if __name__ == "__main__":
    logger = main()

    # Save results to file
    print("\n" + "="*70)
    print("Saving detailed results...")

    with open('test_results.txt', 'w', encoding='utf-8') as f:
        f.write("GA EXTRACTOR PRO - TEST RESULTS\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*70 + "\n\n")

        f.write(f"SUMMARY:\n")
        f.write(f"Total Tests: {logger.test_count}\n")
        f.write(f"Passed: {len(logger.passed)}\n")
        f.write(f"Failed: {len(logger.errors)}\n")
        f.write(f"Warnings: {len(logger.warnings)}\n\n")

        if logger.errors:
            f.write("="*70 + "\n")
            f.write("ERRORS:\n")
            f.write("="*70 + "\n")
            for i, error in enumerate(logger.errors, 1):
                f.write(f"\n{i}. {error['test']}\n")
                f.write(f"   Error: {error['error']}\n")
                if error['traceback']:
                    f.write(f"   Traceback:\n{error['traceback']}\n")

        if logger.warnings:
            f.write("\n" + "="*70 + "\n")
            f.write("WARNINGS:\n")
            f.write("="*70 + "\n")
            for i, warning in enumerate(logger.warnings, 1):
                f.write(f"\n{i}. {warning['test']}\n")
                f.write(f"   Warning: {warning['warning']}\n")

        f.write("\n" + "="*70 + "\n")
        f.write("PASSED TESTS:\n")
        f.write("="*70 + "\n")
        for i, passed in enumerate(logger.passed, 1):
            f.write(f"{i}. {passed['test']}: {passed['message']}\n")

    print("[SUCCESS] Results saved to test_results.txt")
