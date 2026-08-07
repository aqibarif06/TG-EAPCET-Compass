class DataValidator:

    @staticmethod
    def validate_colleges(colleges):

        errors = []

        for code, college in colleges.items():

            if not college["collegeCode"]:
                errors.append(f"Missing college code: {college}")

            if not college["collegeName"]:
                errors.append(f"Missing college name: {college}")

        return errors


    @staticmethod
    def validate_branches(branches):

        errors = []

        for key, branch in branches.items():

            if not branch["branchCode"]:
                errors.append(f"Missing branch code: {branch}")

            if not branch["branchName"]:
                errors.append(f"Missing branch name: {branch}")

        return errors


    @staticmethod
    def validate_cutoffs(cutoffs):

        errors = []

        for cutoff in cutoffs:

            if cutoff["closingRank"] is None:
                errors.append(f"Invalid cutoff: {cutoff}")

            elif cutoff["closingRank"] <= 0:
                errors.append(f"Invalid rank: {cutoff}")

        return errors