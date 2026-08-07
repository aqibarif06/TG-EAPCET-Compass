from pathlib import Path

# Project Root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Data Directories
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
CSV_DIR = PROJECT_ROOT / "data" / "csv"

# Supported Years
YEARS = ["2023", "2024", "2025"]

# PDF Extension
PDF_EXTENSION = ".pdf"