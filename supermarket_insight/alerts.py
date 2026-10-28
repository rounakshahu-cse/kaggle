"""
Alerts Module for Supermarket Sales & Stock Insight Tool.
Implements low-sales velocity alerts and branch product gap analysis.
Syllabus topics used: dictionaries, sets, operators, lists, functions.
Layer rule: Does NOT print to console. Does NOT read files directly.
"""

import pandas as pd

try:
    from config import DEFAULT_LOW_SALES_LIMIT, BRANCHES
except ImportError:
    from supermarket_insight.config import DEFAULT_LOW_SALES_LIMIT, BRANCHES


def get_low_sales_alerts(df: pd.DataFrame, limit: float = DEFAULT_LOW_SALES_LIMIT) -> dict:
    """
    Detect product lines with revenue below a configurable threshold limit (PRD F6).
    Uses operators and conditional logic to categorize sales velocity.

    Parameters:
        df (pd.DataFrame): Cleaned sales DataFrame.
        limit (float): Revenue threshold for alert (runtime configurable).

    Returns:
        dict: {
            'threshold_limit': float,
            'total_products_checked': int,
            'alert_count': int,
            'alerts': list[dict],
            'safe_products': list[dict]
        }
    """
    if df.empty or "Product line" not in df.columns or "Total" not in df.columns:
        return {
            "threshold_limit": limit,
            "total_products_checked": 0,
            "alert_count": 0,
            "alerts": [],
            "safe_products": [],
        }

    grouped = df.groupby("Product line", as_index=False).agg(
        Revenue=("Total", "sum"),
        Quantity=("Quantity", "sum"),
        Transactions=("Invoice ID", "count"),
    )

    alerts = []
    safe_products = []

    for _, row in grouped.iterrows():
        prod = str(row["Product line"])
        rev = float(row["Revenue"])
        qty = int(row["Quantity"])
        tx_count = int(row["Transactions"])

        pct_reached = round((rev / limit * 100), 2) if limit > 0 else 100.0
        deficit = round(limit - rev, 2) if rev < limit else 0.0

        item_info = {
            "product_line": prod,
            "revenue": round(rev, 2),
            "units": qty,
            "transactions": tx_count,
            "threshold": limit,
            "deficit": deficit,
            "pct_reached": pct_reached,
        }

        # Operators: comparisons and boolean checks
        if rev < limit:
            # Determine specific advisory using operators
            if qty < 100:
                advice = "Low demand: Consider promotional discount or bundling."
            else:
                advice = "Moderate unit movement but low revenue: Review item pricing."
            item_info["status"] = "LOW_SALES_ALERT"
            item_info["recommendation"] = advice
            alerts.append(item_info)
        else:
            item_info["status"] = "HEALTHY"
            item_info["recommendation"] = "Sales meet target threshold."
            safe_products.append(item_info)

    # Sort alerts by deficit descending (worst first)
    alerts.sort(key=lambda x: x["deficit"], reverse=True)

    return {
        "threshold_limit": limit,
        "total_products_checked": len(grouped),
        "alert_count": len(alerts),
        "alerts": alerts,
        "safe_products": safe_products,
    }


def get_branch_product_gap(df: pd.DataFrame) -> dict:
    """
    Perform set difference and intersection operations across branches (PRD F7).
    Discovers:
    - Products sold in ALL branches (Set Intersection)
    - Products unique to a specific branch (Set Difference)
    - Catalog completeness across branches

    Parameters:
        df (pd.DataFrame): Cleaned sales DataFrame.

    Returns:
        dict: Set analysis containing sets and formatted summary lists.
    """
    if df.empty or "Branch" not in df.columns or "Product line" not in df.columns:
        return {
            "branch_sets": {},
            "common_all_branches": set(),
            "all_catalog_products": set(),
            "exclusive_by_branch": {},
            "branch_comparisons": [],
        }

    available_branches = sorted(df["Branch"].dropna().unique())

    # Build dictionary of sets: branch -> set of product lines
    branch_sets = {}
    for b in available_branches:
        branch_products = set(df[df["Branch"] == b]["Product line"].dropna().unique())
        branch_sets[b] = branch_products

    # 1. Set Union: All distinct products across the entire business
    all_catalog = set.union(*branch_sets.values()) if branch_sets else set()

    # 2. Set Intersection: Products present in every branch
    if branch_sets:
        common_all = set.intersection(*branch_sets.values())
    else:
        common_all = set()

    # 3. Set Difference: Products exclusive to each branch (in branch B but not in any other)
    exclusive_by_branch = {}
    for b, b_set in branch_sets.items():
        other_sets = [s for other_b, s in branch_sets.items() if other_b != b]
        if other_sets:
            others_union = set.union(*other_sets)
            exclusive_by_branch[b] = b_set - others_union
        else:
            exclusive_by_branch[b] = set()

    # 4. Pairwise Set Differences between branches
    pairwise = []
    for i, b1 in enumerate(available_branches):
        for b2 in available_branches[i + 1:]:
            s1 = branch_sets[b1]
            s2 = branch_sets[b2]
            only_in_first = s1 - s2
            only_in_second = s2 - s1
            shared = s1 & s2
            pairwise.append({
                "branches": (b1, b2),
                "only_in_first": only_in_first,
                "only_in_second": only_in_second,
                "shared": shared,
            })

    return {
        "branch_sets": branch_sets,
        "common_all_branches": common_all,
        "all_catalog_products": all_catalog,
        "exclusive_by_branch": exclusive_by_branch,
        "pairwise_differences": pairwise,
    }
