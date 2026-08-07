class DataRepository:

    def __init__(self):

        self.colleges = {}

        self.branches = {}

        self.cutoffs = []

    def add_college(self, college):

        self.colleges[college["collegeCode"]] = college

    def add_branch(self, branch):

        key = f'{branch["collegeCode"]}_{branch["branchCode"]}'

        self.branches[key] = branch

    def add_cutoffs(self, cutoffs):

        self.cutoffs.extend(cutoffs)

    def stats(self):

        return {
            "colleges": len(self.colleges),
            "branches": len(self.branches),
            "cutoffs": len(self.cutoffs)
        }