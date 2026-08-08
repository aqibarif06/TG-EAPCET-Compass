from pathlib import Path
import pandas as pd


class CSVExporter:

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_colleges(self, colleges):

        df = pd.DataFrame(colleges.values())

        df = df.sort_values("collegeCode")

        file = self.output_dir / "colleges.csv"

        df.to_csv(file, index=False)

        return file

    def export_branches(self, branches):

        df = pd.DataFrame(branches.values())

        df = df.sort_values(
            ["collegeCode", "branchCode"]
        )

        file = self.output_dir / "branches.csv"

        df.to_csv(file, index=False)

        return file

    def export_cutoffs(self, cutoffs):

        df = pd.DataFrame(cutoffs)

        df = df.sort_values(
            [
                "year",
                "phase",
                "collegeCode",
                "branchCode",
                "category"
            ]
        )

        file = self.output_dir / "cutoffs.csv"

        df.to_csv(file, index=False)

        return file

    def export(self, repo):

        return {
            "colleges": self.export_colleges(repo.colleges),
            "branches": self.export_branches(repo.branches),
            "cutoffs": self.export_cutoffs(repo.cutoffs)
        }