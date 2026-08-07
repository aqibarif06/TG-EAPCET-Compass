from config import RAW_DATA_DIR

from auditors.data_auditor import DataAuditor
from cleaner import clean_rows
from extractors.pdf_extractor import PDFExtractor
from normalizers.normalizer import normalize_row
from repositories.data_repository import DataRepository
from utils.file_parser import get_pdf_metadata
from validators.data_validator import DataValidator


def main():

    print("=" * 60)
    print("TG EAPCET Compass - Data Pipeline")
    print("=" * 60)

    extractor = PDFExtractor()
    repo = DataRepository()

    pdf_files = sorted(RAW_DATA_DIR.rglob("*.pdf"))

    print(f"\nFound {len(pdf_files)} PDF(s).\n")

    # --------------------------
    # Process All PDFs
    # --------------------------

    for pdf in pdf_files:

        year, phase = get_pdf_metadata(pdf)

        print(f"Processing: {pdf.name} ({year} - {phase})")

        rows = extractor.extract_rows(pdf)
        rows = clean_rows(rows)

        for row in rows:

            college, branch, cutoffs = normalize_row(
                row=row,
                year=year,
                phase=phase
            )

            repo.add_college(college)
            repo.add_branch(branch)
            repo.add_cutoffs(cutoffs)

    # --------------------------
    # Pipeline Summary
    # --------------------------

    stats = repo.stats()

    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)

    print(f"Unique Colleges : {stats['colleges']}")
    print(f"Unique Branches : {stats['branches']}")
    print(f"Cutoff Records  : {stats['cutoffs']}")

    # --------------------------
    # Validation
    # --------------------------

    print("\nRunning Validation...\n")

    college_errors = DataValidator.validate_colleges(repo.colleges)
    branch_errors = DataValidator.validate_branches(repo.branches)
    cutoff_errors = DataValidator.validate_cutoffs(repo.cutoffs)

    print("=" * 60)
    print("VALIDATION REPORT")
    print("=" * 60)

    print(f"College Errors : {len(college_errors)}")
    print(f"Branch Errors  : {len(branch_errors)}")
    print(f"Cutoff Errors  : {len(cutoff_errors)}")

    total_errors = (
        len(college_errors)
        + len(branch_errors)
        + len(cutoff_errors)
    )

    print("-" * 60)
    print(f"Total Errors   : {total_errors}")

    if total_errors == 0:
        print("\n✅ Dataset validation passed successfully.")
    else:
        print("\n⚠ Dataset contains validation errors.")

        print("\nSample Errors:\n")

        for error in (
            college_errors[:5]
            + branch_errors[:5]
            + cutoff_errors[:5]
        ):
            print("-", error)

    # --------------------------
    # Data Audit
    # --------------------------

    print("\nRunning Data Audit...\n")
    DataAuditor.audit(repo)

    print("\nPipeline Finished Successfully.")


if __name__ == "__main__":
    main()