from collections import Counter


class DataAuditor:

    @staticmethod
    def audit(repo):

        print("\n" + "=" * 70)
        print("TG EAPCET COMPASS - DATA AUDIT REPORT")
        print("=" * 70)

        DataAuditor.audit_colleges(repo)
        DataAuditor.audit_branches(repo)
        DataAuditor.audit_cutoffs(repo)

        print("=" * 70)

    @staticmethod
    def audit_colleges(repo):

        college_codes = list(repo.colleges.keys())

        duplicates = len(college_codes) - len(set(college_codes))

        print(f"Unique Colleges      : {len(repo.colleges)}")
        print(f"Duplicate Colleges   : {duplicates}")

    @staticmethod
    def audit_branches(repo):

        branch_keys = list(repo.branches.keys())

        duplicates = len(branch_keys) - len(set(branch_keys))

        print(f"Unique Branches      : {len(repo.branches)}")
        print(f"Duplicate Branches   : {duplicates}")

    @staticmethod
    def audit_cutoffs(repo):

        keys = []

        for cutoff in repo.cutoffs:

            key = (
                cutoff["year"],
                cutoff["phase"],
                cutoff["collegeCode"],
                cutoff["branchCode"],
                cutoff["category"],
            )

            keys.append(key)

        counter = Counter(keys)

        duplicate_count = sum(
            count - 1
            for count in counter.values()
            if count > 1
        )

        print(f"Cutoff Records       : {len(repo.cutoffs)}")
        print(f"Duplicate Cutoffs    : {duplicate_count}")