from pathlib import Path
import pdfplumber

pdf = Path("data/raw/2023/final.pdf")

with pdfplumber.open(pdf) as pdf_file:

    page = pdf_file.pages[0]

    table = page.extract_tables()[0]

    print(f"Total Rows: {len(table)}")

    # Skip title row and header row
    for row_index, row in enumerate(table[2:12], start=1):

        print("\n" + "=" * 100)
        print(f"DATA ROW {row_index}")
        print("=" * 100)

        for i, value in enumerate(row):
            print(f"{i:02d}: {repr(value)}")