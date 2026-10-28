"""
Search Module for Supermarket Sales & Stock Insight Tool.
Provides case- and space-tolerant search across sales records.
Syllabus topics used: strings, lists, dictionaries, functions, operators, Pandas.
Layer rule: Does NOT print to console. Does NOT read files directly.
"""

import pandas as pd


def normalize_string(text: str) -> str:
    """
    Clean and normalize user query by stripping whitespace and lowercasing.

    Parameters:
        text (str): Input text string.

    Returns:
        str: Cleaned lowercase string with collapsed whitespace.
    """
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
    return " ".join(text.strip().lower().split())


def search_records(
    df: pd.DataFrame,
    query: str,
    search_field: str = "all",
) -> pd.DataFrame:
    """
    Search transactions by product line, branch, date, or invoice ID (PRD F9).
    Offers full tolerance for casing, leading/trailing spaces, and internal multi-spaces.

    Parameters:
        df (pd.DataFrame): Cleaned sales DataFrame.
        query (str): Keyword or phrase to look for.
        search_field (str): Field to search in ('all', 'product', 'branch', 'invoice', 'date', 'city').

    Returns:
        pd.DataFrame: Matching subset of sales records.
    """
    if df.empty or not query or not query.strip():
        return df.copy()

    clean_q = normalize_string(query)
    field_lower = search_field.strip().lower()

    # Define candidate columns based on user selection
    field_map = {
        "product": ["Product line"],
        "branch": ["Branch"],
        "invoice": ["Invoice ID"],
        "date": ["Date", "Month"],
        "city": ["City"],
        "payment": ["Payment"],
        "all": ["Invoice ID", "Branch", "City", "Product line", "Payment", "Date", "Month"],
    }

    target_cols = field_map.get(field_lower, field_map["all"])
    available_cols = [c for c in target_cols if c in df.columns]

    if not available_cols:
        return pd.DataFrame(columns=df.columns)

    # Build boolean mask across candidate columns using vectorized string operations
    mask = pd.Series(False, index=df.index)
    for col in available_cols:
        # Normalize column string representations on the fly
        col_normalized = (
            df[col]
            .astype(str)
            .str.strip()
            .str.lower()
            .str.replace(r"\s+", " ", regex=True)
        )
        mask = mask | col_normalized.str.contains(clean_q, regex=False, na=False)

    return df[mask].reset_index(drop=True)


def get_transaction_by_invoice(df: pd.DataFrame, invoice_id: str) -> dict:
    """
    Lookup a specific transaction by invoice ID with whitespace and case tolerance.

    Parameters:
        df (pd.DataFrame): Sales DataFrame.
        invoice_id (str): Target invoice ID.

    Returns:
        dict: Transaction fields as key-value pairs, or empty dict if not found.
    """
    if df.empty or "Invoice ID" not in df.columns or not invoice_id:
        return {}

    target = normalize_string(invoice_id)
    matches = df[
        df["Invoice ID"].astype(str).str.strip().str.lower() == target
    ]

    if matches.empty:
        return {}

    return matches.iloc[0].to_dict()


def filter_records(
    df: pd.DataFrame,
    branch: str = None,
    product_line: str = None,
    min_total: float = None,
    max_total: float = None,
) -> pd.DataFrame:
    """
    Multi-criteria filter using operators and conditional combinations.

    Parameters:
        df (pd.DataFrame): Sales DataFrame.
        branch (str, optional): Filter by branch letter.
        product_line (str, optional): Filter by product line name.
        min_total (float, optional): Minimum invoice total.
        max_total (float, optional): Maximum invoice total.

    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    if df.empty:
        return df.copy()

    filtered = df.copy()

    if branch:
        filtered = filtered[
            filtered["Branch"].astype(str).str.strip().str.upper() == branch.strip().upper()
        ]

    if product_line:
        clean_prod = normalize_string(product_line)
        filtered = filtered[
            filtered["Product line"].astype(str).str.strip().str.lower() == clean_prod
        ]

    if min_total is not None and "Total" in filtered.columns:
        filtered = filtered[filtered["Total"] >= min_total]

    if max_total is not None and "Total" in filtered.columns:
        filtered = filtered[filtered["Total"] <= max_total]

    return filtered.reset_index(drop=True)
