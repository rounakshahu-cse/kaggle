# Product Requirements Document (PRD)

## Supermarket Sales & Stock Insight Tool

---

## 1. Overview

- **Product name**: Supermarket Sales & Stock Insight Tool
- **Type**: Console-based data analysis system (Python, run in Google Colab or the terminal)
- **Constraint**: No website, webpage, app, Flask or HTML
- **Syllabus limit**: variables, operators, strings, lists, tuples, sets, dictionaries, functions, files, NumPy, Pandas

## 2. Problem Statement

Small and mid-size shop owners record sales in spreadsheets but have no quick way to see which products sell, when the shop is busiest, which branch is weak, or which products need a discount or reduced stock.

## 3. Goal

Turn a raw sales CSV into clear answers in under a minute, using only syllabus topics.

## 4. Users

| User | Need |
|---|---|
| Shop owner or manager | Revenue, best and slowest products, and alerts |
| Student or evaluator | To see each syllabus topic used clearly |

## 5. Dataset

- **Name**: Supermarket Sales (public, Kaggle), about 1,000 rows
- **File**: `data/supermarket_sales.csv`
- **Columns**: Invoice ID, Branch, City, Customer type, Gender, Product line, Unit price, Quantity, Tax 5%, Total, Date, Time, Payment, cogs, gross margin percentage, gross income, Rating
- **Limitation**: the dataset has no stock column, so "stock insight" means a sales-velocity and low-sales alert with a limit the user can change

## 6. Functional Requirements

| ID | Feature | Detail |
|---|---|---|
| F1 | Load and clean | Read the CSV, drop duplicate invoices, strip and title-case text, parse dates, add Month and Hour columns |
| F2 | Data health check | Row count, missing values per column, duplicates removed |
| F3 | Revenue views | By branch, product line, month and hour |
| F4 | Best and slowest products | Ranked by revenue and by units |
| F5 | Payment share | Percentage per payment method |
| F6 | Low-sales alert | Products below a limit the user can change at runtime |
| F7 | Branch product gap | Set difference and intersection across branches |
| F8 | Bill statistics | Mean, median, standard deviation, 90th percentile (NumPy) |
| F9 | Search | By product line, branch, date or invoice, with case and space tolerance |
| F10 | Text bar charts | Bars built from strings, no plotting library |
| F11 | Exports | `monthly_report.csv` and `report.txt` |
| F12 | Menu loop | Numbered text menu, repeats until Exit |

## 7. Non-Functional Requirements

- Runs in Colab or the terminal, with no internet needed after the dataset is loaded
- Each feature is a separate function, and the code is split into modules
- Missing values must not crash the program or be reported as the worst case
- Output is readable: aligned tables, clear labels, and units

## 8. Out of Scope

- Websites, apps, Flask, HTML, JavaScript
- Classes, machine learning, matplotlib or other plotting libraries
- Live data, APIs, or databases

## 9. Architecture

```
supermarket_insight/
  main.py        menu loop only, no business logic
  store.py       load, clean, save (files, strings, Pandas)
  analytics.py   revenue, ranking, payment share, NumPy stats
  alerts.py      low-sales alerts, branch gap (dicts, sets)
  search.py      lookup by keyword (strings, lists)
  report.py      text bars, tables, report.txt, CSV export
  config.py      constants and tuples
  data/
    supermarket_sales.csv
    fixtures/
    output/
  tests/
    run_tests.py (plain assert)
  docs/
    concepts.md (topic-to-code map)
```

### Layer diagram

```
┌─────────────────────────────────────────────┐
│  main.py       Menu loop (input / print)    │
├─────────────────────────────────────────────┤
│  report.py     Text bars, tables, exports   │
├─────────────────────────────────────────────┤
│  analytics.py  Pandas + NumPy analysis      │
│  alerts.py     Low-sales rules (sets, dicts)│
│  search.py     Product and invoice lookup   │
├─────────────────────────────────────────────┤
│  store.py      Read, clean, save CSV files  │
├─────────────────────────────────────────────┤
│  data/         Raw dataset + output files   │
└─────────────────────────────────────────────┘
```

**Layer rule**: each layer calls only the layer below it. `main.py` never reads the CSV, and `analytics.py`, `alerts.py` and `search.py` never print. Only `report.py` and `main.py` print.

### Data flow

1. `store.load_data()` reads the CSV into a DataFrame.
2. `store.clean_data()` standardises text, drops duplicates and flags missing values.
3. `main.py` shows the menu and the user picks an option.
4. The matching function in `analytics`, `alerts` or `search` returns results (a DataFrame, dictionary or list).
5. `report.py` formats the result and prints it.
6. Exports go back through `store.py` into `data/output/`.

## 10. Module Responsibilities

| Module | Job | Syllabus used |
|---|---|---|
| `config.py` | File paths, `LOW_SALES_LIMIT`, `BRANCHES` and `PAYMENTS` tuples | variables, tuples |
| `store.py` | Read CSV, drop duplicates, clean text, flag missing values, save outputs | files, strings, Pandas |
| `analytics.py` | Revenue by branch, product, month and hour, payment share, rating averages | Pandas, NumPy, operators |
| `alerts.py` | Products below the limit, products sold in one branch but not another | dictionaries, sets, operators |
| `search.py` | Find records by keyword with partial matching | strings, lists, functions |
| `report.py` | Text bar charts, aligned tables, report file | strings, lists, files |
| `main.py` | Menu loop, dictionary mapping choice to function | dictionaries, functions |

## 11. Syllabus Coverage

| Topic | Where it appears |
|---|---|
| Variables | thresholds, totals, file paths |
| Operators | percentages, comparisons, `and`/`or` alert rules |
| Strings | cleaning, search, report lines, text bars |
| Lists | menu items, flagged products, report lines |
| Tuples | branches, payment types, fixed column names |
| Sets | unique products, branch gap, products in all branches |
| Dictionaries | alerts, menu-to-function map, category totals |
| Functions | one per feature, across all modules |
| Files | read dataset, write reports and log |
| NumPy | mean, median, standard deviation, percentiles |
| Pandas | `groupby`, `agg`, `value_counts`, filter, sort, `to_csv` |

## 12. Acceptance Criteria

- [x] All 12 features work from the menu without errors
- [x] The low-sales alert changes when the limit is changed
- [x] Exports open correctly and match the on-screen numbers
- [x] A missing rating or a duplicate invoice is handled safely
- [x] All tests pass
- [x] `concepts.md` maps every syllabus topic to a function

## 13. Test Plan (plain `assert`)

| Test | Expected result |
|---|---|
| Total revenue | Greater than 0 |
| Duplicate invoices after cleaning | None remain |
| Missing rating | Does not crash the program and stays blank (NaN) |
| Raising the low-sales limit | The alert fires |
| Search for "health and beauty" | Found in any case or spacing |
| Exported CSV | Same row count as the DataFrame |

## 14. Milestones

| Step | Deliverable |
|---|---|
| 1 | `config.py` and `store.py` |
| 2 | `analytics.py` |
| 3 | `alerts.py` and `search.py` |
| 4 | `report.py` |
| 5 | `main.py` |
| 6 | Tests and `concepts.md` |

## 15. Risks and Notes

- The dataset has no stock column, so the stock feature is a low-sales alert, not real inventory tracking.
- Files created in Colab's `/content/` folder disappear when the session ends, so download outputs before closing.
- If the teacher does not allow `try/except` or the `os` module, remove them from the build and check the file path another way.
