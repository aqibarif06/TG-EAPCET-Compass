from config import RAW_DATA_DIR
from cleaner import clean_rows
from extractors.pdf_extractor import PDFExtractor
from normalizers.normalizer import normalize_row
from utils.file_parser import get_pdf_metadata

extractor = PDFExtractor()

all_colleges = []
all_branches = []
all_cutoffs = []

pdf_files = sorted(RAW_DATA_DIR.rglob("*.pdf"))

for pdf in pdf_files:

    year, phase = get_pdf_metadata(pdf)

    print(f"\nProcessing {pdf.name} ({year} - {phase})")

    rows = extractor.extract_rows(pdf)

    rows = clean_rows(rows)

    for row in rows:

        college, branch, cutoffs = normalize_row(
            row,
            year,
            phase
        )

        all_colleges.append(college)
        all_branches.append(branch)
        all_cutoffs.extend(cutoffs)

print("\n============================")
print("SUMMARY")
print("============================")

print("Colleges :", len(all_colleges))
print("Branches :", len(all_branches))
print("Cutoffs  :", len(all_cutoffs))