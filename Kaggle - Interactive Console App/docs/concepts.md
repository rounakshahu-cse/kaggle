# Syllabus Concepts to Code Implementation Map

This document demonstrates the full coverage of the required curriculum topics in the **Supermarket Sales & Stock Insight Tool**, satisfying all requirements in **PRD Section 11 and Section 12**.

---

## Curriculum Syllabus Coverage Matrix

| Syllabus Topic | File | Function / Identifier | Purpose & Code Description |
|---|---|---|---|
| **Variables** | [`config.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/config.py) | `DEFAULT_LOW_SALES_LIMIT`, `PACKAGE_DIR`, `DEFAULT_DATA_FILE` | Global configuration constants, thresholds, and dynamic file path strings. |
| **Variables** | [`analytics.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/analytics.py) | `get_total_revenue` | Storing metric accumulator variables like `total_rev`, `total_tx`. |
| **Operators** | [`alerts.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/alerts.py) | `get_low_sales_alerts` | Arithmetic (`limit - rev`, `(rev / limit) * 100`), comparison (`rev < limit`, `qty < 100`), and boolean operators (`and` / `or`). |
| **Operators** | [`search.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/search.py) | `filter_records` | Relational operators (`>=`, `<=`, `==`) for multi-condition data filtering. |
| **Strings** | [`store.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/store.py) | `clean_data` | String cleaning: `.strip()`, `.title()`, and text standardization on columns. |
| **Strings** | [`search.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/search.py) | `normalize_string`, `search_records` | Case normalization (`.lower()`), whitespace collapsing (`.split()`), and partial substring matching (`.contains()`). |
| **Strings** | [`report.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/report.py) | `build_text_bar`, `render_bar_chart` | Pure string multiplication (`char * bar_len`) and padding for ASCII bar charts without external plotting packages. |
| **Lists** | [`main.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/main.py) | `print_menu` | Numbered list of menu options iterated over to display UI. |
| **Lists** | [`alerts.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/alerts.py) | `get_low_sales_alerts` | Dynamic lists `alerts = []` and `safe_products = []` populated with `.append()` and sorted via `list.sort()`. |
| **Lists** | [`report.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/report.py) | `format_table` | Multi-dimensional lists of header strings and table row cells. |
| **Tuples** | [`config.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/config.py) | `BRANCHES`, `PAYMENTS`, `PRODUCT_LINES`, `REQUIRED_COLUMNS` | Immutable domain tuples preserving official categories and expected CSV schema. |
| **Tuples** | [`store.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/store.py) | `clean_data` | Returning a tuple of `(cleaned_df, health_stats_dict)`. |
| **Sets** | [`alerts.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/alerts.py) | `get_branch_product_gap` | Python sets: `set.intersection()` for common products across all branches, `set.union()` for total catalog, and set difference (`s1 - s2`) for exclusive products. |
| **Sets** | [`tests/run_tests.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/tests/run_tests.py) | `test_duplicate_invoices_removed` | Verifying invoice uniqueness: `unique_invoices = set(clean_fixture["Invoice ID"])`. |
| **Dictionaries** | [`main.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/main.py) | `main` | Menu dispatcher dictionary `menu_dispatch = {"1": handle_health_check, ...}` mapping user input choices directly to handler functions. |
| **Dictionaries** | [`store.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/store.py) | `clean_data`, `get_health_check` | Health statistics dictionary holding row counts, duplicate count, and missing counts per column. |
| **Dictionaries** | [`analytics.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/analytics.py) | `get_best_and_slowest_products`, `get_payment_share` | Key-value mapping for rankings, summary stats, and payment shares. |
| **Functions** | All modules | Modular functions across all layers | Pure procedural and functional design; each feature is encapsulated in a dedicated function with docstrings and type annotations. |
| **Files** | [`store.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/store.py) | `load_data`, `save_csv`, `save_text_report` | Reading input CSV files (`pd.read_csv`), writing output CSV files (`to_csv`), and opening/writing UTF-8 plain text reports (`open(..., 'w')`). |
| **NumPy** | [`analytics.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/analytics.py) | `get_bill_statistics` | NumPy statistical operations on invoice totals array: `np.mean()`, `np.median()`, `np.std()`, `np.percentile(..., 90)`, `np.min()`, `np.max()`. |
| **Pandas** | [`store.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/store.py) | `load_data`, `clean_data` | Reading CSV, dropping duplicates (`drop_duplicates`), converting data types (`to_numeric`, `to_datetime`), extracting date parts (`.dt.month_name`). |
| **Pandas** | [`analytics.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/analytics.py) | `get_revenue_by_branch`, `get_revenue_by_product_line` | Grouping (`groupby`), aggregations (`agg`), sorting (`sort_values`), and value normalization. |

---

## Detailed Code Reference by Topic

### 1. Variables & Global State
- **File**: [`config.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/config.py)
  - `DEFAULT_LOW_SALES_LIMIT = 5000.0`
  - `DEFAULT_DATA_FILE = os.path.join(DATA_DIR, "supermarket_sales.csv")`
  - `MONTHLY_REPORT_CSV = os.path.join(OUTPUT_DIR, "monthly_report.csv")`
  - `REPORT_TXT = os.path.join(OUTPUT_DIR, "report.txt")`
- **File**: [`main.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/main.py)
  - Application state stored in `state` dictionary (`df`, `health_stats`, `low_sales_limit`).

### 2. Operators
- **File**: [`alerts.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/alerts.py)
  - Arithmetic operators:
    ```python
    pct_reached = round((rev / limit * 100), 2)
    deficit = round(limit - rev, 2) if rev < limit else 0.0
    ```
  - Comparison and Logical operators:
    ```python
    if rev < limit:
        if qty < 100:
            advice = "Low demand: Consider promotional discount or bundling."
        else:
            advice = "Moderate unit movement but low revenue: Review item pricing."
    ```

### 3. Strings
- **File**: [`store.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/store.py)
  - Stripping leading/trailing whitespace and standardizing casing:
    ```python
    df_cleaned.loc[non_null_mask, col] = (
        df_cleaned.loc[non_null_mask, col]
        .astype(str)
        .str.strip()
        .str.title()
    )
    ```
- **File**: [`report.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/report.py)
  - Constructing visual bar charts using pure string manipulation (PRD F10):
    ```python
    bar_str = char * bar_len
    empty_str = " " * (width - bar_len)
    return f"[{bar_str}{empty_str}]"
    ```

### 4. Lists
- **File**: [`main.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/main.py)
  - List of menu item strings displayed dynamically.
- **File**: [`alerts.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/alerts.py)
  - Appending item dictionary objects to `alerts = []` and `safe_products = []`.
- **File**: [`report.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/report.py)
  - 2D list matrix `rows = [...]` passed into `format_table(headers, rows)`.

### 5. Tuples
- **File**: [`config.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/config.py)
  - Domain constants defined as immutable tuples:
    ```python
    BRANCHES = ("A", "B", "C")
    PAYMENTS = ("Cash", "Credit Card", "Ewallet")
    PRODUCT_LINES = (
        "Health And Beauty",
        "Electronic Accessories",
        "Home And Lifestyle",
        "Sports And Travel",
        "Food And Beverages",
        "Fashion Accessories",
    )
    REQUIRED_COLUMNS = ("Invoice ID", "Branch", "City", ...)
    ```

### 6. Sets
- **File**: [`alerts.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/alerts.py)
  - Set theory operations implemented in `get_branch_product_gap(df)`:
    - **Set Union**: `set.union(*branch_sets.values())` -> Total distinct products in catalog.
    - **Set Intersection**: `set.intersection(*branch_sets.values())` -> Products present in every branch.
    - **Set Difference**: `branch_sets[b] - others_union` -> Products exclusive to branch `b`.
    - **Pairwise Differences**: `s1 - s2`, `s2 - s1`, and `s1 & s2`.

### 7. Dictionaries
- **File**: [`main.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/main.py)
  - Dictionary mapping numbered input strings directly to handler functions (PRD F12):
    ```python
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
    ```
- **File**: [`store.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/store.py)
  - Dictionary holding data health metrics: `missing_values`, `cleaned_rows`, `duplicates_removed`.

### 8. Functions
- Each functional requirement (F1 through F12) is implemented as a standalone, modular function.
- **Layer Rule adherence**:
  - `main.py` only handles user input and menu routing.
  - `analytics.py`, `alerts.py`, and `search.py` compute and return data structures—they **never print**.
  - `report.py` formats and prints data structures to the console or strings.
  - `store.py` manages loading and writing files.

### 9. Files
- Reading dataset CSV: `pd.read_csv(file_path)` in `store.load_data()`.
- Exporting monthly aggregated CSV: `df.to_csv(file_path, index=False)` in `store.save_csv()`.
- Exporting executive summary text file: `open(file_path, "w", encoding="utf-8")` in `store.save_text_report()`.

### 10. NumPy
- **File**: [`analytics.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/analytics.py)
  - Function `get_bill_statistics(df)` converts invoice totals into a NumPy 1D array and computes:
    - Mean: `np.mean(totals)`
    - Median: `np.median(totals)`
    - Standard Deviation: `np.std(totals)`
    - 90th Percentile: `np.percentile(totals, 90)`
    - Minimum & Maximum: `np.min(totals)`, `np.max(totals)`

### 11. Pandas
- **File**: [`store.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/store.py)
  - `df.drop_duplicates(subset=["Invoice ID"])`
  - `pd.to_datetime(df["Date"])`, `.dt.month_name()`
  - `pd.to_numeric(...)`
- **File**: [`analytics.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/analytics.py)
  - `df.groupby("Branch").agg(...)`
  - `df.groupby("Product line").agg(...)`
  - `df.sort_values(by="Revenue", ascending=False)`
- **File**: [`search.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/search.py)
  - Vectorized string boolean mask: `df[mask]`
