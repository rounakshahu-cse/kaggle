"""
Configuration Module for Supermarket Sales & Stock Insight Tool.
Syllabus topics used: variables, tuples, strings, files.
"""

import os

# Base directory for the supermarket_insight package
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data directory paths
DATA_DIR = os.path.join(PACKAGE_DIR, "data")
DEFAULT_DATA_FILE = os.path.join(DATA_DIR, "supermarket_sales.csv")
FIXTURE_DATA_FILE = os.path.join(DATA_DIR, "fixtures", "test_sales.csv")

# Output directory and export paths
OUTPUT_DIR = os.path.join(DATA_DIR, "output")
MONTHLY_REPORT_CSV = os.path.join(OUTPUT_DIR, "monthly_report.csv")
REPORT_TXT = os.path.join(OUTPUT_DIR, "report.txt")

# Business Logic Defaults
DEFAULT_LOW_SALES_LIMIT = 5000.0

# Fixed Domain Categories (Tuples)
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

# Expected CSV Column Schema (Tuple)
REQUIRED_COLUMNS = (
    "Invoice ID",
    "Branch",
    "City",
    "Customer type",
    "Gender",
    "Product line",
    "Unit price",
    "Quantity",
    "Tax 5%",
    "Total",
    "Date",
    "Time",
    "Payment",
    "cogs",
    "gross margin percentage",
    "gross income",
    "Rating",
)

# Text columns to strip and title-case
TEXT_COLUMNS = (
    "Branch",
    "City",
    "Customer type",
    "Gender",
    "Product line",
    "Payment",
)

# Numeric columns to ensure correct data types
NUMERIC_COLUMNS = (
    "Unit price",
    "Quantity",
    "Tax 5%",
    "Total",
    "cogs",
    "gross margin percentage",
    "gross income",
    "Rating",
)
