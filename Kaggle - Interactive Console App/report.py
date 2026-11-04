"""
Report Module for Supermarket Sales & Stock Insight Tool.
Generates ASCII text bar charts, aligned console tables, and exportable reports.
Syllabus topics used: strings, lists, dictionaries, files, functions, operators.
Layer rule: Formats and prints data. Can call store.py for file export.
Universal ASCII design: Fully safe across all terminal encodings (including Windows cp1252 & Colab).
"""

import pandas as pd

try:
    from config import (
        DEFAULT_LOW_SALES_LIMIT,
        MONTHLY_REPORT_CSV,
        REPORT_TXT,
    )
    import analytics
    import alerts
    import store
except ImportError:
    from supermarket_insight.config import (
        DEFAULT_LOW_SALES_LIMIT,
        MONTHLY_REPORT_CSV,
        REPORT_TXT,
    )
    import supermarket_insight.analytics as analytics
    import supermarket_insight.alerts as alerts
    import supermarket_insight.store as store


def format_table(headers: list, rows: list, alignments: list = None) -> str:
    """
    Format data rows and headers into a clean, aligned plain-text table.

    Parameters:
        headers (list[str]): Column titles.
        rows (list[list]): List of row value lists.
        alignments (list[str], optional): 'L' for left, 'R' for right.

    Returns:
        str: Aligned multi-line table string.
    """
    if not headers:
        return ""

    str_headers = [str(h) for h in headers]
    str_rows = [[str(cell) for cell in row] for row in rows]

    # Calculate column widths
    col_widths = [len(h) for h in str_headers]
    for row in str_rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(cell))

    # Default alignments: right for numbers/currencies, left for text
    if not alignments:
        alignments = []
        for h in str_headers:
            h_lower = h.lower()
            if any(term in h_lower for term in ("rev", "total", "qty", "count", "stat", "pct", "%", "price", "bill", "unit", "deficit")):
                alignments.append("R")
            else:
                alignments.append("L")

    while len(alignments) < len(col_widths):
        alignments.append("L")

    sep_line = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

    def format_row(cells):
        formatted_cells = []
        for i, cell in enumerate(cells):
            w = col_widths[i]
            align = alignments[i] if i < len(alignments) else "L"
            if align == "R":
                formatted_cells.append(f" {cell:>{w}} ")
            else:
                formatted_cells.append(f" {cell:<{w}} ")
        return "|" + "|".join(formatted_cells) + "|"

    output_lines = [sep_line, format_row(str_headers), sep_line]
    for row in str_rows:
        output_lines.append(format_row(row))
    output_lines.append(sep_line)

    return "\n".join(output_lines)


def build_text_bar(value: float, max_value: float, width: int = 28, char: str = "#") -> str:
    """
    Generate a text bar string proportional to value / max_value (PRD F10).
    Constructed using pure string multiplication with universal ASCII chars.

    Parameters:
        value (float): Metric value.
        max_value (float): Maximum scale value.
        width (int): Max bar character width.
        char (str): ASCII character used to draw the bar.

    Returns:
        str: String bar representation.
    """
    if max_value <= 0 or value <= 0:
        bar_len = 0
    else:
        bar_len = int((value / max_value) * width)
        if bar_len > width:
            bar_len = width
        elif bar_len == 0 and value > 0:
            bar_len = 1

    bar_str = char * bar_len
    empty_str = " " * (width - bar_len)
    return f"[{bar_str}{empty_str}]"


def render_bar_chart(title: str, items: list, unit: str = "$", width: int = 26) -> str:
    """
    Render a formatted visual text bar chart (PRD F10).

    Parameters:
        title (str): Chart heading.
        items (list[tuple]): List of (label: str, value: float).
        unit (str): Display prefix or suffix for numbers.
        width (int): Bar length limit.

    Returns:
        str: Rendered ASCII bar chart.
    """
    if not items:
        return f"{title}\n  (No data to display)"

    max_val = max(val for _, val in items) if items else 1.0
    max_label_len = max(len(str(lbl)) for lbl, _ in items) if items else 10

    lines = [
        f"=== {title} ===",
        "-" * (max_label_len + width + 24),
    ]

    for label, val in items:
        bar = build_text_bar(val, max_val, width=width)
        if unit == "$":
            val_str = f"${val:,.2f}"
        elif unit == "%":
            val_str = f"{val:.1f}%"
        else:
            val_str = f"{val:,.0f} {unit}"
        lines.append(f"  {label:<{max_label_len}} | {bar} {val_str:>12}")

    lines.append("-" * (max_label_len + width + 24))
    return "\n".join(lines)


def display_header(title: str, subtitle: str = ""):
    """Print an eye-catching section banner."""
    print()
    print("=" * 68)
    print(f"  {title.upper()}")
    if subtitle:
        print(f"  {subtitle}")
    print("=" * 68)


def display_health_check(health_stats: dict):
    """Display data quality and integrity health check (PRD F2)."""
    display_header("Data Health Check", "Integrity, Duplicates & Missing Values")
    print(f"  Total Clean Records       : {health_stats.get('cleaned_rows', 0):,}")
    print(f"  Duplicate Invoices Dropped: {health_stats.get('duplicates_removed', 0):,}")
    print(f"  Total Missing Fields      : {health_stats.get('total_missing', 0):,}")
    print()

    missing = health_stats.get("missing_values", {})
    headers = ["Column Name", "Missing Count", "Status"]
    rows = []
    for col, count in missing.items():
        status = "OK (Complete)" if count == 0 else f"Notice ({count} null)"
        rows.append([col, count, status])
    print(format_table(headers, rows))


def display_revenue_views(df: pd.DataFrame):
    """Display revenue aggregated by branch, product, month, and hour (PRD F3)."""
    display_header("Revenue Views", "Sales Aggregated by Dimension")

    # 1. By Branch
    print("\n--- 1. Revenue by Branch ---")
    b_df = analytics.get_revenue_by_branch(df)
    b_rows = [
        [r["Branch"], f"${r['Revenue']:,.2f}", f"{r['Quantity']:,}", f"{r['Transactions']:,}", f"${r['Avg_Bill']:,.2f}"]
        for _, r in b_df.iterrows()
    ]
    print(format_table(["Branch", "Revenue", "Units Sold", "Transactions", "Avg Bill"], b_rows))

    # 2. By Product Line
    print("\n--- 2. Revenue by Product Line ---")
    p_df = analytics.get_revenue_by_product_line(df)
    p_rows = [
        [r["Product line"], f"${r['Revenue']:,.2f}", f"{r['Quantity']:,}", f"{r['Transactions']:,}", f"${r['Avg_Price']:,.2f}"]
        for _, r in p_df.iterrows()
    ]
    print(format_table(["Product Line", "Revenue", "Units Sold", "Transactions", "Avg Unit Price"], p_rows))

    # 3. By Month
    print("\n--- 3. Revenue by Month ---")
    m_df = analytics.get_revenue_by_month(df)
    m_rows = [
        [r["Month"], f"${r['Revenue']:,.2f}", f"{r['Quantity']:,}", f"{r['Transactions']:,}"]
        for _, r in m_df.iterrows()
    ]
    print(format_table(["Month", "Revenue", "Units Sold", "Transactions"], m_rows))

    # 4. By Hour
    print("\n--- 4. Peak Hours Revenue ---")
    h_df = analytics.get_revenue_by_hour(df)
    h_rows = [
        [f"{int(r['Hour']):02d}:00", f"${r['Revenue']:,.2f}", f"{r['Quantity']:,}", f"{r['Transactions']:,}"]
        for _, r in h_df.iterrows()
    ]
    print(format_table(["Hour", "Revenue", "Units Sold", "Transactions"], h_rows))


def display_product_rankings(df: pd.DataFrame):
    """Display best and slowest products ranked by revenue and units (PRD F4)."""
    display_header("Product Performance Rankings", "Best & Slowest Performing Items")
    rankings = analytics.get_best_and_slowest_products(df)

    best_rev = rankings["best_by_revenue"]
    slow_rev = rankings["slowest_by_revenue"]
    best_units = rankings["best_by_units"]
    slow_units = rankings["slowest_by_units"]

    print(f"  [BEST] Highest Revenue Leader : {best_rev['product_line']} (${best_rev['revenue']:,.2f} from {best_rev['units']:,} units)")
    print(f"  [LOW]  Lowest Revenue Performer: {slow_rev['product_line']} (${slow_rev['revenue']:,.2f} from {slow_rev['units']:,} units)")
    print(f"  [BEST] Most Units Sold        : {best_units['product_line']} ({best_units['units']:,} units sold, ${best_units['revenue']:,.2f})")
    print(f"  [LOW]  Fewest Units Sold      : {slow_units['product_line']} ({slow_units['units']:,} units sold, ${slow_units['revenue']:,.2f})")
    print()

    print("Complete Product Ranking (Sorted by Revenue):")
    rev_df = rankings["revenue_ranking"]
    rows = [
        [i + 1, r["Product line"], f"${r['Revenue']:,.2f}", f"{r['Quantity']:,}", f"{r['Transactions']:,}"]
        for i, (_, r) in enumerate(rev_df.iterrows())
    ]
    print(format_table(["Rank", "Product Line", "Revenue", "Units Sold", "Transactions"], rows))


def display_payment_share(df: pd.DataFrame):
    """Display payment method percentage breakdown (PRD F5)."""
    display_header("Payment Method Breakdown", "Transaction Volume and Revenue Share")
    pay_data = analytics.get_payment_share(df)
    summary_df = pay_data.get("summary_table", pd.DataFrame())

    rows = [
        [
            r["Payment"],
            f"{r['Transactions']:,}",
            f"{r['Tx_Share_Pct']:.2f}%",
            f"${r['Revenue']:,.2f}",
            f"{r['Revenue_Share_Pct']:.2f}%",
        ]
        for _, r in summary_df.iterrows()
    ]
    print(format_table(["Payment Method", "Transactions", "Tx Share %", "Revenue", "Revenue Share %"], rows))

    items = [(str(r["Payment"]), float(r["Revenue_Share_Pct"])) for _, r in summary_df.iterrows()]
    print()
    print(render_bar_chart("Payment Revenue Share (%)", items, unit="%"))


def display_low_sales_alerts(df: pd.DataFrame, limit: float = DEFAULT_LOW_SALES_LIMIT):
    """Display products triggering low-sales alerts (PRD F6)."""
    display_header("Low-Sales Velocity Alerts", f"Target Threshold: ${limit:,.2f}")
    alerts_data = alerts.get_low_sales_alerts(df, limit)

    flagged = alerts_data["alerts"]
    safe = alerts_data["safe_products"]

    print(f"  Total Product Lines Checked : {alerts_data['total_products_checked']}")
    print(f"  Products Requiring Attention: {len(flagged)}")
    print()

    if not flagged:
        print(f"  [OK] Excellent: All product lines met or exceeded the ${limit:,.2f} threshold!")
    else:
        print("  [ALERT] FLAGGED ITEMS BELOW TARGET THRESHOLD:")
        headers = ["Product Line", "Revenue", "Target", "Deficit", "% Achieved", "Advisory"]
        rows = [
            [
                item["product_line"],
                f"${item['revenue']:,.2f}",
                f"${item['threshold']:,.2f}",
                f"${item['deficit']:,.2f}",
                f"{item['pct_reached']:.1f}%",
                item["recommendation"],
            ]
            for item in flagged
        ]
        print(format_table(headers, rows))

    if safe:
        print(f"\n  [HEALTHY] Products Above ${limit:,.2f}:")
        for s in safe:
            print(f"      - {s['product_line']}: ${s['revenue']:,.2f} ({s['pct_reached']:.1f}% of target)")


def display_branch_gap(df: pd.DataFrame):
    """Display branch product gap set analysis (PRD F7)."""
    display_header("Branch Product Gap Analysis", "Set Intersection & Differences")
    gap_data = alerts.get_branch_product_gap(df)

    branch_sets = gap_data["branch_sets"]
    common_all = gap_data["common_all_branches"]
    all_cat = gap_data["all_catalog_products"]
    exclusive = gap_data["exclusive_by_branch"]

    print(f"  Total Catalog Products : {len(all_cat)}")
    print(f"  Common to ALL Branches : {len(common_all)}")
    print(f"    -> {', '.join(sorted(common_all)) if common_all else 'None'}")
    print()

    print("Branch Catalog Coverage:")
    for b, p_set in sorted(branch_sets.items()):
        ex = exclusive.get(b, set())
        ex_str = f"Exclusive: {', '.join(sorted(ex))}" if ex else "No exclusive products"
        print(f"  Branch {b}: {len(p_set)} product lines | {ex_str}")

    print("\nPairwise Set Comparisons:")
    for comp in gap_data["pairwise_differences"]:
        b1, b2 = comp["branches"]
        only_1 = comp["only_in_first"]
        only_2 = comp["only_in_second"]
        only_1_str = ", ".join(sorted(only_1)) if only_1 else "None"
        only_2_str = ", ".join(sorted(only_2)) if only_2 else "None"
        print(f"  * In Branch {b1} but NOT in {b2} : {only_1_str}")
        print(f"  * In Branch {b2} but NOT in {b1} : {only_2_str}")


def display_bill_statistics(df: pd.DataFrame):
    """Display NumPy bill statistics (PRD F8)."""
    display_header("Invoice Bill Statistics (NumPy)", "Distribution of Transaction Values")
    stats = analytics.get_bill_statistics(df)

    headers = ["Metric", "Value"]
    rows = [
        ["Total Invoices Analyzed", f"{stats['count']:,}"],
        ["Mean Bill Amount", f"${stats['mean']:,.2f}"],
        ["Median Bill Amount", f"${stats['median']:,.2f}"],
        ["Standard Deviation", f"${stats['std_dev']:,.2f}"],
        ["90th Percentile Bill", f"${stats['percentile_90']:,.2f}"],
        ["Minimum Invoice Total", f"${stats['min']:,.2f}"],
        ["Maximum Invoice Total", f"${stats['max']:,.2f}"],
    ]
    print(format_table(headers, rows))


def display_search_results(results_df: pd.DataFrame, query: str):
    """Display matching transaction search results (PRD F9)."""
    display_header("Search Results", f"Keyword Query: '{query}'")
    match_count = len(results_df)
    print(f"  Found {match_count:,} matching transaction(s).")
    print()

    if results_df.empty:
        print("  No records matched your search query. Try another keyword.")
        return

    display_df = results_df.head(15)
    headers = ["Invoice ID", "Branch", "Product Line", "Total", "Date", "Payment", "Rating"]
    rows = []
    for _, r in display_df.iterrows():
        rating_str = f"{r['Rating']:.1f}" if pd.notnull(r.get("Rating")) else "N/A"
        rows.append([
            r.get("Invoice ID", ""),
            r.get("Branch", ""),
            r.get("Product line", ""),
            f"${r.get('Total', 0.0):,.2f}",
            str(r.get("Date", ""))[:10],
            r.get("Payment", ""),
            rating_str,
        ])
    print(format_table(headers, rows))

    if match_count > 15:
        print(f"  ... and {match_count - 15} more records (showing top 15).")


def display_bar_charts(df: pd.DataFrame):
    """Render full suite of ASCII text bar charts (PRD F10)."""
    display_header("Text Bar Charts", "Visual Performance Without External Plotting")

    prod_df = analytics.get_revenue_by_product_line(df)
    prod_items = [(str(r["Product line"]), float(r["Revenue"])) for _, r in prod_df.iterrows()]
    print(render_bar_chart("Revenue by Product Line ($)", prod_items, unit="$"))
    print()

    branch_df = analytics.get_revenue_by_branch(df)
    branch_items = [(f"Branch {r['Branch']}", float(r["Revenue"])) for _, r in branch_df.iterrows()]
    print(render_bar_chart("Revenue by Branch ($)", branch_items, unit="$"))
    print()

    month_df = analytics.get_revenue_by_month(df)
    month_items = [(str(r["Month"]), float(r["Revenue"])) for _, r in month_df.iterrows()]
    print(render_bar_chart("Monthly Revenue ($)", month_items, unit="$"))


def prepare_monthly_report_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate comprehensive aggregated dataset for monthly_report.csv export (PRD F11).

    Parameters:
        df (pd.DataFrame): Sales DataFrame.

    Returns:
        pd.DataFrame: Aggregated monthly performance dataset.
    """
    if df.empty or "Month" not in df.columns:
        return pd.DataFrame()

    grouped = df.groupby(["Month", "Branch"], as_index=False).agg(
        Revenue=("Total", "sum"),
        Units_Sold=("Quantity", "sum"),
        Transactions=("Invoice ID", "count"),
        Avg_Bill=("Total", "mean"),
        Gross_Income=("gross income", "sum"),
    )
    grouped["Revenue"] = grouped["Revenue"].round(2)
    grouped["Avg_Bill"] = grouped["Avg_Bill"].round(2)
    grouped["Gross_Income"] = grouped["Gross_Income"].round(2)
    return grouped


def build_full_text_report(df: pd.DataFrame, low_sales_limit: float = DEFAULT_LOW_SALES_LIMIT) -> str:
    """
    Build complete comprehensive executive plain-text report for report.txt (PRD F11).

    Parameters:
        df (pd.DataFrame): Sales DataFrame.
        low_sales_limit (float): Low sales alert threshold.

    Returns:
        str: Multi-line plain-text report string.
    """
    tot_rev = analytics.get_total_revenue(df)
    tot_units = analytics.get_total_units(df)
    b_df = analytics.get_revenue_by_branch(df)
    p_df = analytics.get_revenue_by_product_line(df)
    pay = analytics.get_payment_share(df)
    stats = analytics.get_bill_statistics(df)
    rankings = analytics.get_best_and_slowest_products(df)
    alert_info = alerts.get_low_sales_alerts(df, low_sales_limit)

    sections = [
        "==================================================================",
        "          SUPERMARKET SALES & STOCK INSIGHT REPORT                ",
        "==================================================================",
        f"Transactions Analyzed          : {len(df):,}",
        f"Total Revenue Generated        : ${tot_rev:,.2f}",
        f"Total Units Sold               : {tot_units:,}",
        f"Average Bill Amount            : ${stats['mean']:,.2f}",
        "------------------------------------------------------------------",
        "",
        "1. PERFORMANCE BY BRANCH",
        "------------------------",
    ]

    for _, r in b_df.iterrows():
        sections.append(
            f"  Branch {r['Branch']}: ${r['Revenue']:,.2f} | {r['Quantity']:,} units | {r['Transactions']:,} txs | Avg Bill: ${r['Avg_Bill']:,.2f}"
        )

    sections.extend([
        "",
        "2. PERFORMANCE BY PRODUCT LINE",
        "------------------------------",
    ])
    for _, r in p_df.iterrows():
        sections.append(
            f"  {r['Product line']:<25}: ${r['Revenue']:>10,.2f} | {r['Quantity']:>5,} units | Avg Price: ${r['Avg_Price']:,.2f}"
        )

    sections.extend([
        "",
        "3. BEST & SLOWEST PERFORMERS",
        "----------------------------",
        f"  Best by Revenue    : {rankings['best_by_revenue']['product_line']} (${rankings['best_by_revenue']['revenue']:,.2f})",
        f"  Slowest by Revenue : {rankings['slowest_by_revenue']['product_line']} (${rankings['slowest_by_revenue']['revenue']:,.2f})",
        f"  Best by Units Sold : {rankings['best_by_units']['product_line']} ({rankings['best_by_units']['units']:,} units)",
        f"  Fewest Units Sold  : {rankings['slowest_by_units']['product_line']} ({rankings['slowest_by_units']['units']:,} units)",
        "",
        "4. PAYMENT METHOD DISTRIBUTION",
        "------------------------------",
    ])
    for meth, pct in pay["revenue_share_pct"].items():
        sections.append(f"  {meth:<18}: {pct:>5.2f}% of Revenue")

    sections.extend([
        "",
        "5. NUMPY BILL STATISTICS",
        "------------------------",
        f"  Mean Bill          : ${stats['mean']:,.2f}",
        f"  Median Bill        : ${stats['median']:,.2f}",
        f"  Std Deviation      : ${stats['std_dev']:,.2f}",
        f"  90th Percentile    : ${stats['percentile_90']:,.2f}",
        f"  Min Bill           : ${stats['min']:,.2f}",
        f"  Max Bill           : ${stats['max']:,.2f}",
        "",
        f"6. LOW-SALES VELOCITY ALERTS (Threshold: ${low_sales_limit:,.2f})",
        "----------------------------------------------------------",
    ])

    if not alert_info["alerts"]:
        sections.append(f"  No products below the ${low_sales_limit:,.2f} threshold.")
    else:
        for itm in alert_info["alerts"]:
            sections.append(
                f"  [ALERT] {itm['product_line']}: ${itm['revenue']:,.2f} (Deficit: ${itm['deficit']:,.2f}) -> {itm['recommendation']}"
            )

    sections.extend([
        "",
        "==================================================================",
        "End of Report",
        "==================================================================",
    ])

    return "\n".join(sections)


def export_all_reports(
    df: pd.DataFrame,
    low_sales_limit: float = DEFAULT_LOW_SALES_LIMIT,
    csv_path: str = MONTHLY_REPORT_CSV,
    txt_path: str = REPORT_TXT,
) -> tuple:
    """
    Execute exports of monthly_report.csv and report.txt (PRD F11).

    Parameters:
        df (pd.DataFrame): Sales DataFrame.
        low_sales_limit (float): Low sales threshold.
        csv_path (str): CSV export target path.
        txt_path (str): Text report export target path.

    Returns:
        tuple: (csv_success: bool, txt_success: bool)
    """
    monthly_df = prepare_monthly_report_df(df)
    csv_ok = store.save_csv(monthly_df, csv_path)

    full_txt = build_full_text_report(df, low_sales_limit)
    txt_ok = store.save_text_report(full_txt, txt_path)

    return csv_ok, txt_ok
