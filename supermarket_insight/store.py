"""
Store Module for Supermarket Sales & Stock Insight Tool.
Handles file I/O, data loading, cleaning, validation, and exports.
Syllabus topics used: files, strings, dictionaries, tuples, lists, Pandas.
Layer rule: Does NOT print to console. Does NOT call analytics or UI layers.
"""

import os
import pandas as pd

try:
    from config import (
        DEFAULT_DATA_FILE,
        MONTHLY_REPORT_CSV,
        REPORT_TXT,
        TEXT_COLUMNS,
        NUMERIC_COLUMNS,
        OUTPUT_DIR,
    )
except ImportError:
    from supermarket_insight.config import (
        DEFAULT_DATA_FILE,
        MONTHLY_REPORT_CSV,
        REPORT_TXT,
        TEXT_COLUMNS,
        NUMERIC_COLUMNS,
        OUTPUT_DIR,
    )


def load_data(file_path: str = DEFAULT_DATA_FILE) -> pd.DataFrame:
    """
    Load supermarket sales CSV file into a pandas DataFrame.

    Parameters:
        file_path (str): Path to CSV data file.

    Returns:
        pd.DataFrame: Loaded raw dataset.

    Raises:
        FileNotFoundError: If the specified file does not exist.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found at: {file_path}")

    return pd.read_csv(file_path)


def clean_data(df: pd.DataFrame) -> tuple:
    """
    Clean and normalize sales data according to PRD F1 and F2:
    - Drops duplicate invoices by 'Invoice ID'
    - Strips whitespace and title-cases text fields
    - Safely converts numeric columns (preserving NaNs where values are missing)
    - Parses dates to derive 'Month' (month name)
    - Parses time to derive 'Hour' (0-23 integer)
    - Compiles data health check metrics

    Parameters:
        df (pd.DataFrame): Raw sales DataFrame.

    Returns:
        tuple: (cleaned_df: pd.DataFrame, health_stats: dict)
    """
    initial_rows = len(df)

    # 1. Drop duplicate invoices
    if "Invoice ID" in df.columns:
        df_cleaned = df.drop_duplicates(subset=["Invoice ID"]).copy()
    else:
        df_cleaned = df.copy()

    duplicates_removed = initial_rows - len(df_cleaned)

    # 2. Strip whitespace and title-case text columns
    for col in TEXT_COLUMNS:
        if col in df_cleaned.columns:
            # Preserve NaN values without converting them into the string 'Nan'
            non_null_mask = df_cleaned[col].notnull()
            df_cleaned.loc[non_null_mask, col] = (
                df_cleaned.loc[non_null_mask, col]
                .astype(str)
                .str.strip()
                .str.title()
            )

    # 3. Ensure numeric columns have correct float/int types
    for col in NUMERIC_COLUMNS:
        if col in df_cleaned.columns:
            df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors="coerce")

    # 4. Parse Date and extract Month
    if "Date" in df_cleaned.columns:
        parsed_dates = pd.to_datetime(df_cleaned["Date"], errors="coerce")
        df_cleaned["Month"] = parsed_dates.dt.month_name()
    else:
        df_cleaned["Month"] = "Unknown"

    # 5. Parse Time and extract Hour
    if "Time" in df_cleaned.columns:
        # Some times may have seconds or missing parts, split or parse
        time_series = df_cleaned["Time"].astype(str).str.strip()
        parsed_hours = []
        for val in time_series:
            parts = val.split(":")
            if parts and parts[0].isdigit():
                parsed_hours.append(int(parts[0]))
            else:
                parsed_hours.append(0)
        df_cleaned["Hour"] = parsed_hours
    else:
        df_cleaned["Hour"] = 0

    # 6. Gather health check statistics (dictionary)
    missing_values = {}
    for col in df_cleaned.columns:
        missing_count = int(df_cleaned[col].isnull().sum())
        missing_values[col] = missing_count

    health_stats = {
        "initial_rows": initial_rows,
        "cleaned_rows": len(df_cleaned),
        "duplicates_removed": duplicates_removed,
        "missing_values": missing_values,
        "total_missing": sum(missing_values.values()),
    }

    return df_cleaned, health_stats


def get_health_check(df: pd.DataFrame, duplicates_removed: int = 0) -> dict:
    """
    Return data health statistics for a DataFrame.

    Parameters:
        df (pd.DataFrame): DataFrame to inspect.
        duplicates_removed (int): Number of duplicate records previously dropped.

    Returns:
        dict: Health check metrics.
    """
    missing_values = {col: int(df[col].isnull().sum()) for col in df.columns}
    return {
        "total_rows": len(df),
        "duplicates_removed": duplicates_removed,
        "missing_values": missing_values,
        "total_missing": sum(missing_values.values()),
    }


def save_csv(df: pd.DataFrame, file_path: str = MONTHLY_REPORT_CSV) -> bool:
    """
    Save DataFrame to CSV file, ensuring target directory exists.

    Parameters:
        df (pd.DataFrame): DataFrame to export.
        file_path (str): Output file destination.

    Returns:
        bool: True if file write succeeded.
    """
    out_dir = os.path.dirname(file_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    df.to_csv(file_path, index=False)
    return True


def save_text_report(content: str, file_path: str = REPORT_TXT) -> bool:
    """
    Write text content to file, creating destination folders if needed.

    Parameters:
        content (str): Text report content.
        file_path (str): File destination path.

    Returns:
        bool: True if write succeeded.
    """
    out_dir = os.path.dirname(file_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return True
