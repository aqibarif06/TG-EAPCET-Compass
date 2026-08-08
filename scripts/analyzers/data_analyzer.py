import pandas as pd


class DataAnalyzer:

    def __init__(self, csv_dir):

        self.colleges = pd.read_csv(csv_dir / "colleges.csv")
        self.branches = pd.read_csv(csv_dir / "branches.csv")
        self.cutoffs = pd.read_csv(csv_dir / "cutoffs.csv")

    def analyze(self):

        print("\n" + "=" * 70)
        print("TG EAPCET DATA ANALYTICS")
        print("=" * 70)

        print(f"Total Colleges      : {len(self.colleges)}")
        print(f"Total Branches      : {len(self.branches)}")
        print(f"Total Cutoffs       : {len(self.cutoffs)}")

        print("\nCollege Type Distribution")
        print("-------------------------")
        print(self.colleges["collegeType"].value_counts())

        print("\nDistrict Distribution")
        print("-------------------------")
        print(self.colleges["district"].value_counts())

        print("\nTop 10 Colleges by Branch Count")
        print("-------------------------------")

        top = (
            self.branches
            .groupby("collegeCode")
            .size()
            .sort_values(ascending=False)
            .head(10)
        )

        print(top)

        print("\nTop 10 Branch Codes")
        print("-------------------")

        print(
            self.branches["branchCode"]
            .value_counts()
            .head(10)
        )

        print("\nCategory Distribution")
        print("---------------------")

        print(
            self.cutoffs["category"]
            .value_counts()
        )

        print("\nYear Distribution")
        print("-----------------")

        print(
            self.cutoffs["year"]
            .value_counts()
            .sort_index()
        )

        print("\nPhase Distribution")
        print("------------------")

        print(
            self.cutoffs["phase"]
            .value_counts()
        )

        print("=" * 70)