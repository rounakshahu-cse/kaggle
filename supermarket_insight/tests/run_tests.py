"""
Test Suite for Supermarket Sales & Stock Insight Tool.
Implements the PRD Section 13 Test Plan using plain assert statements.
Executable directly with `python run_tests.py` or via `pytest`.
"""

import os
import sys
import numpy as np
import pandas as pd

# Add package root to sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PACKAGE_DIR)

import config
import store
import analytics
import alerts
import search
import report


def test_duplicate_invoices_removed():
    """PRD Test: Duplicate invoices after cleaning -> None remain."""
    raw_fixture = store.load_data(config.FIXTURE_DATA_FILE)
    assert len(raw_fixture) == 12, f"Expected 12 raw fixture rows, got {len(raw_fixture)}"

    clean_fixture, health = store.clean_data(raw_fixture)
    # The fixture contains duplicate invoice '101-11-1001' on lines 2 and 8
    assert health["duplicates_removed"] == 1, (
        f"Expected exactly 1 duplicate removed, got {health['duplicates_removed']}"
    )
    assert len(clean_fixture) == 11, f"Expected 11 cleaned rows, got {len(clean_fixture)}"

    # Check that each invoice ID in cleaned dataset is unique
    unique_invoices = set(clean_fixture["Invoice ID"])
    assert len(unique_invoices) == len(clean_fixture), "Duplicate invoice remains in cleaned data!"
    print("  [PASS] test_duplicate_invoices_removed")


def test_missing_rating_handled_safely():
    """PRD Test: Missing rating -> Does not crash program and stays blank (NaN)."""
    clean_fixture, health = store.clean_data(store.load_data(config.FIXTURE_DATA_FILE))

    # Rating column should contain exactly 1 missing value in the test fixture
    assert health["missing_values"]["Rating"] == 1, (
        f"Expected 1 missing rating, found {health['missing_values']['Rating']}"
    )

    # Ensure rating averages calculate without throwing errors or skewing
    avg_ratings = analytics.get_rating_averages(clean_fixture)
    assert avg_ratings["overall_avg"] > 0, "Overall rating average calculation failed"
    assert isinstance(avg_ratings["by_branch"], dict), "Branch rating must be a dictionary"
    assert isinstance(avg_ratings["by_product"], dict), "Product rating must be a dictionary"

    # Verify that bill statistics and revenue calculations work seamlessly
    stats = analytics.get_bill_statistics(clean_fixture)
    assert stats["count"] == 11, f"Expected 11 count in stats, got {stats['count']}"
    print("  [PASS] test_missing_rating_handled_safely")


def test_string_cleaning_and_casing():
    """PRD Test: Whitespace stripped and title-cased."""
    clean_fixture, _ = store.clean_data(store.load_data(config.FIXTURE_DATA_FILE))

    product_lines = list(clean_fixture["Product line"].unique())
    # The fixture has '  health and BEAUTY  ' and 'electronic ACCESSORIES  '
    assert "Health And Beauty" in product_lines, "Whitespace and title-casing failed on Health And Beauty"
    assert "Electronic Accessories" in product_lines, "Whitespace and title-casing failed on Electronic Accessories"

    # Ensure no leading/trailing spaces exist in any text column
    for col in config.TEXT_COLUMNS:
        for val in clean_fixture[col].dropna():
            assert str(val) == str(val).strip(), f"Untrimmed whitespace found in column {col}: '{val}'"
    print("  [PASS] test_string_cleaning_and_casing")


def test_total_revenue_greater_than_zero():
    """PRD Test: Total revenue -> Greater than 0."""
    clean_fixture, _ = store.clean_data(store.load_data(config.FIXTURE_DATA_FILE))
    fixture_rev = analytics.get_total_revenue(clean_fixture)
    assert fixture_rev > 0, f"Expected positive revenue for fixture, got {fixture_rev}"

    clean_prod, _ = store.clean_data(store.load_data(config.DEFAULT_DATA_FILE))
    prod_rev = analytics.get_total_revenue(clean_prod)
    assert prod_rev > 0, f"Expected positive revenue for production data, got {prod_rev}"
    assert np.isclose(prod_rev, 322966.749, atol=1.0), f"Production revenue mismatch: {prod_rev}"
    print("  [PASS] test_total_revenue_greater_than_zero")


def test_low_sales_alert_dynamic_limit():
    """PRD Test: Raising the low-sales limit -> The alert fires."""
    clean_fixture, _ = store.clean_data(store.load_data(config.FIXTURE_DATA_FILE))

    # At limit = 1.0, all products should be healthy (no alert)
    low_alert = alerts.get_low_sales_alerts(clean_fixture, limit=1.0)
    assert low_alert["alert_count"] == 0, f"Expected 0 alerts at limit 1.0, got {low_alert['alert_count']}"

    # At limit = 50000.0, all fixture products should trigger an alert
    high_alert = alerts.get_low_sales_alerts(clean_fixture, limit=50000.0)
    assert high_alert["alert_count"] > 0, "Alert did not fire when raising the low-sales limit!"
    assert len(high_alert["alerts"]) == high_alert["total_products_checked"]

    # Verify deficit calculation
    first_flagged = high_alert["alerts"][0]
    assert first_flagged["deficit"] > 0, "Deficit must be greater than 0"
    assert np.isclose(first_flagged["threshold"] - first_flagged["revenue"], first_flagged["deficit"])
    print("  [PASS] test_low_sales_alert_dynamic_limit")


def test_search_case_and_space_tolerance():
    """PRD Test: Search for 'health and beauty' -> Found in any case or spacing."""
    clean_fixture, _ = store.clean_data(store.load_data(config.FIXTURE_DATA_FILE))

    # Search with messy casing and multi-spaces
    queries = [
        "health and beauty",
        "  health   and   BEAUTY  ",
        "HEALTH AND BEAUTY",
        "health",
        "BEAUTY",
    ]

    for q in queries:
        results = search.search_records(clean_fixture, q)
        assert len(results) >= 2, f"Query '{q}' failed to match expected records. Found {len(results)}"

    # Specific invoice search
    inv_match = search.get_transaction_by_invoice(clean_fixture, "  101-11-1002  ")
    assert inv_match.get("Invoice ID") == "101-11-1002", "Invoice lookup with padding spaces failed"
    print("  [PASS] test_search_case_and_space_tolerance")


def test_branch_product_gap_sets():
    """PRD Test: Branch product gap -> Set difference and intersection across branches."""
    clean_prod, _ = store.clean_data(store.load_data(config.DEFAULT_DATA_FILE))
    gap = alerts.get_branch_product_gap(clean_prod)

    assert isinstance(gap["common_all_branches"], set), "Common products must be a set"
    assert isinstance(gap["all_catalog_products"], set), "Catalog must be a set"
    assert len(gap["common_all_branches"]) > 0, "Expected common products across branches"

    # In standard supermarket dataset, all 6 product lines are sold in branches A, B, and C
    assert len(gap["common_all_branches"]) == 6, (
        f"Expected 6 common product lines, got {len(gap['common_all_branches'])}"
    )
    print("  [PASS] test_branch_product_gap_sets")


def test_numpy_bill_statistics():
    """PRD Test: Bill statistics -> Mean, median, std dev, 90th percentile (NumPy)."""
    clean_prod, _ = store.clean_data(store.load_data(config.DEFAULT_DATA_FILE))
    stats = analytics.get_bill_statistics(clean_prod)

    raw_totals = np.array(clean_prod["Total"].dropna(), dtype=float)
    assert np.isclose(stats["mean"], float(np.mean(raw_totals)))
    assert np.isclose(stats["median"], float(np.median(raw_totals)))
    assert np.isclose(stats["std_dev"], float(np.std(raw_totals)))
    assert np.isclose(stats["percentile_90"], float(np.percentile(raw_totals, 90)))
    assert stats["min"] <= stats["median"] <= stats["max"]
    print("  [PASS] test_numpy_bill_statistics")


def test_text_bar_chart_generation():
    """PRD Test: Text bar charts -> Pure string construction, no plotting library."""
    bar = report.build_text_bar(50.0, 100.0, width=20, char="#")
    assert bar.startswith("[##########"), f"Bar rendering incorrect: {bar}"
    assert len(bar) == 22, f"Bar total length including brackets should be 22, got {len(bar)}"

    chart_str = report.render_bar_chart("Test Chart", [("Item A", 100), ("Item B", 50)])
    assert "Test Chart" in chart_str
    assert "Item A" in chart_str
    assert "Item B" in chart_str
    print("  [PASS] test_text_bar_chart_generation")


def test_exported_csv_and_text_reports():
    """PRD Test: Exported CSV and report.txt match data and row counts."""
    clean_prod, _ = store.clean_data(store.load_data(config.DEFAULT_DATA_FILE))

    test_csv = os.path.join(config.OUTPUT_DIR, "test_monthly.csv")
    test_txt = os.path.join(config.OUTPUT_DIR, "test_report.txt")

    csv_ok, txt_ok = report.export_all_reports(
        clean_prod,
        low_sales_limit=5000.0,
        csv_path=test_csv,
        txt_path=test_txt,
    )

    assert csv_ok and os.path.exists(test_csv), "Exported CSV file was not created"
    assert txt_ok and os.path.exists(test_txt), "Exported TXT report was not created"

    # Verify CSV structure
    exported_df = pd.read_csv(test_csv)
    expected_df = report.prepare_monthly_report_df(clean_prod)
    assert len(exported_df) == len(expected_df), (
        f"Exported CSV row count ({len(exported_df)}) does not match expected ({len(expected_df)})"
    )

    # Verify text report content
    with open(test_txt, "r", encoding="utf-8") as f:
        txt_content = f.read()
    assert "SUPERMARKET SALES & STOCK INSIGHT REPORT" in txt_content
    assert "$322,966.75" in txt_content
    assert "NUMPY BILL STATISTICS" in txt_content

    # Clean up test output artifacts
    if os.path.exists(test_csv):
        os.remove(test_csv)
    if os.path.exists(test_txt):
        os.remove(test_txt)

    print("  [PASS] test_exported_csv_and_text_reports")


def run_all_tests():
    """Run all verification tests sequentially and report results."""
    print("=" * 68)
    print("  RUNNING SUPERMARKET INSIGHT TEST SUITE (PLAIN ASSERT)")
    print("=" * 68)

    tests = [
        test_duplicate_invoices_removed,
        test_missing_rating_handled_safely,
        test_string_cleaning_and_casing,
        test_total_revenue_greater_than_zero,
        test_low_sales_alert_dynamic_limit,
        test_search_case_and_space_tolerance,
        test_branch_product_gap_sets,
        test_numpy_bill_statistics,
        test_text_bar_chart_generation,
        test_exported_csv_and_text_reports,
    ]

    passed = 0
    failed = 0

    for test_fn in tests:
        try:
            test_fn()
            passed += 1
        except AssertionError as e:
            print(f"  [FAIL] {test_fn.__name__}: {e}")
            failed += 1
        except Exception as err:
            print(f"  [ERROR] {test_fn.__name__}: Unexpected error: {err}")
            failed += 1

    print("=" * 68)
    if failed == 0:
        print(f"  ALL {passed} TESTS PASSED SUCCESSFULLY! (0 Failures)")
    else:
        print(f"  TESTS COMPLETED: {passed} Passed, {failed} Failed.")
    print("=" * 68)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
