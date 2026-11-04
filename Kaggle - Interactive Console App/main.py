"""
Main Application Module for Supermarket Sales & Stock Insight Tool.
Menu loop and CLI routing.
Syllabus topics used: dictionaries, functions, lists, strings, variables, operators.
Layer rule: Calls report.py and store.py. Contains NO analytical business logic.
Only report.py and main.py perform print and input operations.
"""

import sys
import os

try:
    from config import (
        DEFAULT_DATA_FILE,
        FIXTURE_DATA_FILE,
        DEFAULT_LOW_SALES_LIMIT,
        MONTHLY_REPORT_CSV,
        REPORT_TXT,
    )
    import store
    import report
    import search
except ImportError:
    from supermarket_insight.config import (
        DEFAULT_DATA_FILE,
        FIXTURE_DATA_FILE,
        DEFAULT_LOW_SALES_LIMIT,
        MONTHLY_REPORT_CSV,
        REPORT_TXT,
    )
    import supermarket_insight.store as store
    import supermarket_insight.report as report
    import supermarket_insight.search as search


def print_banner():
    """Display startup application banner."""
    print("=" * 68)
    print("   SUPERMARKET SALES & STOCK INSIGHT TOOL (CONSOLE SYSTEM)")
    print("   Fast, Syllabus-Compliant Retail Decision Analytics Engine")
    print("=" * 68)


def print_menu(current_limit: float, record_count: int):
    """
    Print the numbered interactive console menu (PRD F12).
    Uses lists and string formatting.
    """
    menu_items = [
        "1.  Data Health Check (Duplicates & Missing Values)",
        "2.  Revenue Views (By Branch, Product Line, Month, Hour)",
        "3.  Best & Slowest Products (By Revenue & Units)",
        "4.  Payment Method Share (Volume & Percentage)",
        f"5.  Low-Sales Velocity Alerts (Threshold: ${current_limit:,.2f})",
        "6.  Branch Product Gap Analysis (Set Theory Intersection & Diffs)",
        "7.  Bill Statistics (NumPy Mean, Median, StdDev, 90th Pct)",
        "8.  Search Transactions (Case & Space Tolerant Lookup)",
        "9.  Visual Text Bar Charts (Pure String Rendering)",
        "10. Export Reports (monthly_report.csv & report.txt)",
        "11. Adjust Low-Sales Target Threshold",
        "12. Switch Dataset (Production Dataset vs Test Fixtures)",
        "0.  Exit System",
    ]

    print("\n" + "-" * 68)
    print(f"  MAIN MENU  [Active Dataset: {record_count:,} records | Alert Target: ${current_limit:,.2f}]")
    print("-" * 68)
    for item in menu_items:
        print(f"  {item}")
    print("-" * 68)


# --- Menu Action Handlers (Functions mapped via Dictionary) ---

def handle_health_check(state: dict):
    """Action 1: Display dataset health and integrity stats."""
    report.display_health_check(state["health_stats"])


def handle_revenue_views(state: dict):
    """Action 2: Display multidimensional revenue aggregations."""
    report.display_revenue_views(state["df"])


def handle_product_rankings(state: dict):
    """Action 3: Display top and bottom performing product lines."""
    report.display_product_rankings(state["df"])


def handle_payment_share(state: dict):
    """Action 4: Display payment method breakdown."""
    report.display_payment_share(state["df"])


def handle_low_sales_alerts(state: dict):
    """Action 5: Check and display low-sales velocity alerts."""
    report.display_low_sales_alerts(state["df"], state["low_sales_limit"])


def handle_branch_gap(state: dict):
    """Action 6: Perform and display set difference and intersection."""
    report.display_branch_gap(state["df"])


def handle_bill_statistics(state: dict):
    """Action 7: Display NumPy invoice statistics."""
    report.display_bill_statistics(state["df"])


def handle_search(state: dict):
    """Action 8: Search transactions with case and space tolerance."""
    report.display_header("Search Transactions", "Case & Space Tolerant Keyword Query")
    query = input("  Enter keyword to search (product, branch, invoice, date, city): ").strip()
    if not query:
        print("  [Notice] Search query was empty. Returning to menu.")
        return

    results = search.search_records(state["df"], query)
    report.display_search_results(results, query)


def handle_bar_charts(state: dict):
    """Action 9: Render ASCII visual text bar charts."""
    report.display_bar_charts(state["df"])


def handle_exports(state: dict):
    """Action 10: Export monthly_report.csv and report.txt."""
    report.display_header("Export Reports", "Saving Deliverables to data/output/")
    csv_ok, txt_ok = report.export_all_reports(
        state["df"],
        state["low_sales_limit"],
        MONTHLY_REPORT_CSV,
        REPORT_TXT,
    )

    if csv_ok and txt_ok:
        print(f"  [SUCCESS] Monthly Report exported to : {MONTHLY_REPORT_CSV}")
        print(f"  [SUCCESS] Executive Text Report saved: {REPORT_TXT}")
    else:
        print("  [ERROR] An error occurred while writing export files.")


def handle_adjust_threshold(state: dict):
    """Action 11: Modify the low-sales limit at runtime (PRD F6)."""
    report.display_header("Configure Alert Threshold", f"Current Target: ${state['low_sales_limit']:,.2f}")
    new_val_str = input("  Enter new low-sales threshold limit in dollars: ").strip()

    try:
        new_val = float(new_val_str)
        if new_val < 0:
            print("  [Error] Threshold cannot be negative.")
        else:
            state["low_sales_limit"] = new_val
            print(f"  [Updated] New low-sales alert threshold set to: ${new_val:,.2f}")
    except ValueError:
        print("  [Error] Invalid number. Target threshold remained unchanged.")


def handle_switch_dataset(state: dict):
    """Action 12: Toggle between full dataset and test fixture data."""
    report.display_header("Dataset Switcher", "Load Alternate Sales CSV File")
    print(f"  Current File: {state['active_file']}")
    print(f"  1. Main Production Dataset ({DEFAULT_DATA_FILE})")
    print(f"  2. Test Fixtures Dataset   ({FIXTURE_DATA_FILE})")
    print("  3. Custom file path")

    choice = input("  Select dataset (1, 2, or 3): ").strip()
    new_path = ""
    if choice == "1":
        new_path = DEFAULT_DATA_FILE
    elif choice == "2":
        new_path = FIXTURE_DATA_FILE
    elif choice == "3":
        new_path = input("  Enter full path to CSV file: ").strip()

    if new_path:
        try:
            raw_df = store.load_data(new_path)
            clean_df, health = store.clean_data(raw_df)
            state["df"] = clean_df
            state["health_stats"] = health
            state["active_file"] = new_path
            print(f"  [Success] Loaded {len(clean_df):,} records from {new_path}")
        except Exception as e:
            print(f"  [Error] Failed to load dataset: {e}")


def init_app_state(file_path: str = DEFAULT_DATA_FILE) -> dict:
    """
    Initialize application state dictionary with loaded and cleaned data.

    Parameters:
        file_path (str): Initial dataset path.

    Returns:
        dict: Application state holding df, health_stats, and low_sales_limit.
    """
    # If default file not found, try fixture file
    if not os.path.exists(file_path) and os.path.exists(FIXTURE_DATA_FILE):
        file_path = FIXTURE_DATA_FILE

    raw_df = store.load_data(file_path)
    clean_df, health = store.clean_data(raw_df)

    return {
        "df": clean_df,
        "health_stats": health,
        "low_sales_limit": DEFAULT_LOW_SALES_LIMIT,
        "active_file": file_path,
    }


def main():
    """
    Main application entry point.
    Runs interactive numbered menu loop using a dictionary dispatcher (PRD F12).
    """
    print_banner()

    try:
        state = init_app_state(DEFAULT_DATA_FILE)
        print(f"  [OK] Dataset loaded successfully ({len(state['df']):,} clean records).")
    except Exception as err:
        print(f"  [Startup Error] Could not load dataset: {err}")
        return

    # Dictionary mapping choice string to handler function (PRD requirement)
    menu_dispatch = {
        "1": handle_health_check,
        "2": handle_revenue_views,
        "3": handle_product_rankings,
        "4": handle_payment_share,
        "5": handle_low_sales_alerts,
        "6": handle_branch_gap,
        "7": handle_bill_statistics,
        "8": handle_search,
        "9": handle_bar_charts,
        "10": handle_exports,
        "11": handle_adjust_threshold,
        "12": handle_switch_dataset,
    }

    # Main menu loop (PRD F12)
    while True:
        print_menu(state["low_sales_limit"], len(state["df"]))
        choice = input("  Select an option (0-12): ").strip()

        if choice in ("0", "exit", "quit", "q"):
            print("\n  Thank you for using Supermarket Sales & Stock Insight Tool. Goodbye!\n")
            break

        handler = menu_dispatch.get(choice)
        if handler:
            handler(state)
        else:
            print(f"\n  [Invalid Choice] '{choice}' is not a valid menu option. Please enter 0-12.")

        # Pause briefly for user to read output before showing menu again
        input("\n  Press [Enter] to return to menu...")


if __name__ == "__main__":
    main()
