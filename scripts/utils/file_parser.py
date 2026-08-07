from pathlib import Path


def get_pdf_metadata(pdf_path: Path):
    """
    Extract year and phase from:
    data/raw/2023/final.pdf
    """

    year = int(pdf_path.parent.name)

    phase = pdf_path.stem.lower()

    phase_map = {
        "phase1": "Phase 1",
        "phase2": "Phase 2",
        "final": "Final"
    }

    return year, phase_map.get(phase, phase)