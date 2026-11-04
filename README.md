# Supermarket Sales & Stock Insight Tool

A fast, modular, console-based retail analytics engine developed in Python for small and mid-size supermarket shop managers and academic evaluation.

Designed strictly within the curriculum syllabus constraints:
- **Core Topics**: Variables, Operators, Strings, Lists, Tuples, Sets, Dictionaries, Functions, Files, NumPy, Pandas.
- **Constraints**: No website, HTML, Flask, or OOP classes. All features implemented as modular functions.
- **Visuals**: ASCII text bar charts without external plotting libraries.
- **Environments**: Runs seamlessly in Google Colab, Linux, macOS, and Windows PowerShell terminals.

---

## Project Structure

```
.
├── supermarket_insight_colab.ipynb  # Interactive Google Colab walkthrough notebook
├── supermarket_insight/
│   ├── config.py             # File paths, low-sales limit default, domain tuples
│   ├── store.py              # Load CSV, drop duplicates, clean text, flag missing values, exports
│   ├── analytics.py          # Revenue by dimension, rankings, payment share, NumPy bill stats
│   ├── alerts.py             # Low-sales alerts (threshold check), branch product gap (sets)
│   ├── search.py             # Keyword lookup with case- and space-tolerance
│   ├── report.py             # Aligned ASCII tables, text bar charts, export formatters
│   ├── main.py               # Interactive CLI numbered menu loop with dictionary dispatcher
│   │
│   ├── data/
│   │   ├── supermarket_sales.csv   # Main Kaggle Myanmar supermarket sales dataset (~1,000 rows)
│   │   ├── fixtures/
│   │   │   └── test_sales.csv      # Edge-case fixture (duplicates, missing values, irregular casing)
│   │   └── output/
│   │       ├── monthly_report.csv  # Exported aggregated monthly sales dataset
│   │       └── report.txt          # Exported executive text summary report
│   │
│   ├── tests/
│   │   └── run_tests.py      # Test suite using plain asserts (and pytest compatible)
│   │
│   └── docs/
│       └── concepts.md       # Comprehensive topic-to-code mapping for syllabus evaluation
```

---

## Quick Start

### 1. Run in Google Colab or Jupyter Notebook
Upload or open [`supermarket_insight_colab.ipynb`](file:///d:/Project/SL%20mini%20project/supermarket_insight_colab.ipynb) in [Google Colab](https://colab.research.google.com/) or run locally via Jupyter. It provides an end-to-end interactive guided walkthrough of all 12 PRD features, test execution, and CSV/TXT file downloads.

### 2. Run the Interactive Console Application
```bash
python supermarket_insight/main.py
```

### 3. Run the Automated Test Suite
With plain Python:
```bash
python supermarket_insight/tests/run_tests.py
```
Or with pytest:
```bash
python -m pytest supermarket_insight/tests/run_tests.py
```

---

## Features Overview (PRD F1 - F12)

| Feature | Description | Module |
|---|---|---|
| **F1: Load & Clean** | Reads dataset, drops duplicate invoices, strips whitespace, title-cases text, derives `Month` and `Hour`. | [`store.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/store.py) |
| **F2: Data Health Check** | Reports record counts, duplicates removed, and missing values per column. | [`store.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/store.py), [`report.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/report.py) |
| **F3: Revenue Views** | Aggregated sales by Branch (A, B, C), Product Line, Month, and Hour of day. | [`analytics.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/analytics.py) |
| **F4: Product Rankings** | Best and slowest performing products ranked by revenue and by physical units sold. | [`analytics.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/analytics.py) |
| **F5: Payment Share** | Transaction count percentage and revenue volume share per payment method. | [`analytics.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/analytics.py) |
| **F6: Low-Sales Alert** | Identifies items falling short of a customizable sales threshold, advising price or promo actions. | [`alerts.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/alerts.py) |
| **F7: Branch Product Gap** | Set intersection (products in all branches) and set difference (branch-exclusive products). | [`alerts.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/alerts.py) |
| **F8: Bill Statistics** | NumPy-computed Mean, Median, Standard Deviation, and 90th Percentile invoice amounts. | [`analytics.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/analytics.py) |
| **F9: Search Engine** | Case- and space-tolerant multi-column search across transactions and invoice IDs. | [`search.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/search.py) |
| **F10: Text Bar Charts** | Terminal visual bar charts drawn purely from strings with no plotting dependencies. | [`report.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/report.py) |
| **F11: File Exports** | Generates `data/output/monthly_report.csv` and formatted `data/output/report.txt`. | [`store.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/store.py), [`report.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/report.py) |
| **F12: Menu Loop** | Numbered console menu with dictionary dispatch loop that runs until user exits. | [`main.py`](file:///d:/Project/SL%20mini%20project/supermarket_insight/main.py) |

---

## Topic-to-Code Mapping

For detailed academic mapping of each curriculum concept (Variables, Operators, Strings, Lists, Tuples, Sets, Dictionaries, Functions, Files, NumPy, Pandas), see [`docs/concepts.md`](file:///d:/Project/SL%20mini%20project/supermarket_insight/docs/concepts.md).
