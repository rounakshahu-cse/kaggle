"""
Analytics Module for Supermarket Sales & Stock Insight Tool.
Provides revenue aggregation, product rankings, payment shares,
rating metrics, and NumPy statistical analysis.
Syllabus topics used: Pandas, NumPy, operators, dictionaries, lists, tuples, functions.
Layer rule: Does NOT print to console. Does NOT read files directly.
"""

import numpy as np
import pandas as pd


def get_total_revenue(df: pd.DataFrame) -> float:
    """
    Calculate the total gross revenue from all transactions.

    Parameters:
        df (pd.DataFrame): Sales DataFrame.

    Returns:
        float: Total revenue sum.
    """
    if df.empty or "Total" not in df.columns:
        return 0.0
    return float(df["Total"].sum())


def get_total_units(df: pd.DataFrame) -> int:
    """
    Calculate the total quantity of items sold.

    Parameters:
        df (pd.DataFrame): Sales DataFrame.

    Returns:
        int: Total units sold.
    """
    if df.empty or "Quantity" not in df.columns:
        return 0
    return int(df["Quantity"].sum())


def get_revenue_by_branch(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate sales metrics grouped by Branch.

    Parameters:
        df (pd.DataFrame): Sales DataFrame.

    Returns:
        pd.DataFrame: Table sorted by Revenue descending with columns:
                      ['Branch', 'Revenue', 'Quantity', 'Transactions', 'Avg_Bill']
    """
    if df.empty:
        return pd.DataFrame(columns=["Branch", "Revenue", "Quantity", "Transactions", "Avg_Bill"])

    grouped = df.groupby("Branch", as_index=False).agg(
        Revenue=("Total", "sum"),
        Quantity=("Quantity", "sum"),
        Transactions=("Invoice ID", "count"),
        Avg_Bill=("Total", "mean"),
    )
    return grouped.sort_values(by="Revenue", ascending=False).reset_index(drop=True)


def get_revenue_by_product_line(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate sales metrics grouped by Product line.

    Parameters:
        df (pd.DataFrame): Sales DataFrame.

    Returns:
        pd.DataFrame: Table sorted by Revenue descending with columns:
                      ['Product line', 'Revenue', 'Quantity', 'Transactions', 'Avg_Price']
    """
    if df.empty:
        return pd.DataFrame(columns=["Product line", "Revenue", "Quantity", "Transactions", "Avg_Price"])

    grouped = df.groupby("Product line", as_index=False).agg(
        Revenue=("Total", "sum"),
        Quantity=("Quantity", "sum"),
        Transactions=("Invoice ID", "count"),
        Avg_Price=("Unit price", "mean"),
    )
    return grouped.sort_values(by="Revenue", ascending=False).reset_index(drop=True)


def get_revenue_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate sales metrics grouped by Month.

    Parameters:
        df (pd.DataFrame): Sales DataFrame containing 'Month' column.

    Returns:
        pd.DataFrame: Table grouped by Month with columns:
                      ['Month', 'Revenue', 'Quantity', 'Transactions']
    """
    if df.empty or "Month" not in df.columns:
        return pd.DataFrame(columns=["Month", "Revenue", "Quantity", "Transactions"])

    grouped = df.groupby("Month", as_index=False).agg(
        Revenue=("Total", "sum"),
        Quantity=("Quantity", "sum"),
        Transactions=("Invoice ID", "count"),
    )

    # Order months chronologically if possible
    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]
    grouped["_sort_key"] = grouped["Month"].apply(
        lambda m: month_order.index(m) if m in month_order else 99
    )
    grouped = grouped.sort_values(by="_sort_key").drop(columns=["_sort_key"]).reset_index(drop=True)
    return grouped


def get_revenue_by_hour(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate sales metrics grouped by Hour of the day.

    Parameters:
        df (pd.DataFrame): Sales DataFrame containing 'Hour' column.

    Returns:
        pd.DataFrame: Table grouped by Hour sorted chronologically.
    """
    if df.empty or "Hour" not in df.columns:
        return pd.DataFrame(columns=["Hour", "Revenue", "Quantity", "Transactions"])

    grouped = df.groupby("Hour", as_index=False).agg(
        Revenue=("Total", "sum"),
        Quantity=("Quantity", "sum"),
        Transactions=("Invoice ID", "count"),
    )
    return grouped.sort_values(by="Hour", ascending=True).reset_index(drop=True)


def get_best_and_slowest_products(df: pd.DataFrame) -> dict:
    """
    Determine the best and slowest selling products ranked by revenue and by units.

    Parameters:
        df (pd.DataFrame): Sales DataFrame.

    Returns:
        dict: Detailed rankings and top/bottom items:
              {
                  'best_by_revenue': dict,
                  'slowest_by_revenue': dict,
                  'best_by_units': dict,
                  'slowest_by_units': dict,
                  'revenue_ranking': pd.DataFrame,
                  'units_ranking': pd.DataFrame
              }
    """
    prod_summary = get_revenue_by_product_line(df)
    if prod_summary.empty:
        empty_item = {"product_line": "N/A", "revenue": 0.0, "units": 0}
        return {
            "best_by_revenue": empty_item,
            "slowest_by_revenue": empty_item,
            "best_by_units": empty_item,
            "slowest_by_units": empty_item,
            "revenue_ranking": prod_summary,
            "units_ranking": prod_summary,
        }

    # Revenue ranking
    rev_sorted = prod_summary.sort_values(by="Revenue", ascending=False).reset_index(drop=True)
    units_sorted = prod_summary.sort_values(by="Quantity", ascending=False).reset_index(drop=True)

    best_rev_row = rev_sorted.iloc[0]
    slow_rev_row = rev_sorted.iloc[-1]
    best_units_row = units_sorted.iloc[0]
    slow_units_row = units_sorted.iloc[-1]

    return {
        "best_by_revenue": {
            "product_line": str(best_rev_row["Product line"]),
            "revenue": float(best_rev_row["Revenue"]),
            "units": int(best_rev_row["Quantity"]),
        },
        "slowest_by_revenue": {
            "product_line": str(slow_rev_row["Product line"]),
            "revenue": float(slow_rev_row["Revenue"]),
            "units": int(slow_rev_row["Quantity"]),
        },
        "best_by_units": {
            "product_line": str(best_units_row["Product line"]),
            "revenue": float(best_units_row["Revenue"]),
            "units": int(best_units_row["Quantity"]),
        },
        "slowest_by_units": {
            "product_line": str(slow_units_row["Product line"]),
            "revenue": float(slow_units_row["Revenue"]),
            "units": int(slow_units_row["Quantity"]),
        },
        "revenue_ranking": rev_sorted,
        "units_ranking": units_sorted,
    }


def get_payment_share(df: pd.DataFrame) -> dict:
    """
    Calculate the percentage share and volume for each payment method.

    Parameters:
        df (pd.DataFrame): Sales DataFrame.

    Returns:
        dict: {
            'count_share_pct': dict[str, float],
            'revenue_share_pct': dict[str, float],
            'summary_table': pd.DataFrame
        }
    """
    if df.empty or "Payment" not in df.columns:
        return {"count_share_pct": {}, "revenue_share_pct": {}, "summary_table": pd.DataFrame()}

    total_rev = get_total_revenue(df)
    total_tx = len(df)

    summary = df.groupby("Payment", as_index=False).agg(
        Transactions=("Invoice ID", "count"),
        Revenue=("Total", "sum"),
    )

    summary["Tx_Share_Pct"] = (
        (summary["Transactions"] / total_tx * 100).round(2) if total_tx > 0 else 0.0
    )
    summary["Revenue_Share_Pct"] = (
        (summary["Revenue"] / total_rev * 100).round(2) if total_rev > 0 else 0.0
    )
    summary = summary.sort_values(by="Revenue", ascending=False).reset_index(drop=True)

    count_share = dict(zip(summary["Payment"], summary["Tx_Share_Pct"]))
    revenue_share = dict(zip(summary["Payment"], summary["Revenue_Share_Pct"]))

    return {
        "count_share_pct": count_share,
        "revenue_share_pct": revenue_share,
        "summary_table": summary,
    }


def get_rating_averages(df: pd.DataFrame) -> dict:
    """
    Calculate customer rating averages overall, by branch, and by product line.
    Handles NaN values safely without crashing or skewing.

    Parameters:
        df (pd.DataFrame): Sales DataFrame.

    Returns:
        dict: {
            'overall_avg': float,
            'by_branch': dict[str, float],
            'by_product': dict[str, float]
        }
    """
    if df.empty or "Rating" not in df.columns:
        return {"overall_avg": 0.0, "by_branch": {}, "by_product": {}}

    valid_ratings = df["Rating"].dropna()
    overall = float(valid_ratings.mean()) if not valid_ratings.empty else 0.0

    branch_ratings = (
        df.groupby("Branch")["Rating"].mean().dropna().round(2).to_dict()
    )
    product_ratings = (
        df.groupby("Product line")["Rating"].mean().dropna().round(2).to_dict()
    )

    return {
        "overall_avg": round(overall, 2),
        "by_branch": branch_ratings,
        "by_product": product_ratings,
    }


def get_bill_statistics(df: pd.DataFrame) -> dict:
    """
    Compute invoice bill statistics using NumPy according to PRD F8:
    Mean, Median, Standard Deviation, and 90th Percentile.

    Parameters:
        df (pd.DataFrame): Sales DataFrame.

    Returns:
        dict: NumPy statistical metrics on invoice totals.
    """
    if df.empty or "Total" not in df.columns:
        return {
            "mean": 0.0,
            "median": 0.0,
            "std_dev": 0.0,
            "percentile_90": 0.0,
            "min": 0.0,
            "max": 0.0,
            "count": 0,
        }

    # Extract NumPy array from Total column, excluding any nulls
    totals = np.array(df["Total"].dropna(), dtype=float)

    if len(totals) == 0:
        return {
            "mean": 0.0,
            "median": 0.0,
            "std_dev": 0.0,
            "percentile_90": 0.0,
            "min": 0.0,
            "max": 0.0,
            "count": 0,
        }

    return {
        "mean": float(np.mean(totals)),
        "median": float(np.median(totals)),
        "std_dev": float(np.std(totals)),
        "percentile_90": float(np.percentile(totals, 90)),
        "min": float(np.min(totals)),
        "max": float(np.max(totals)),
        "count": int(len(totals)),
    }
