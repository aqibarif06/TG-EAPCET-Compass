def validate_row(row):

    # 2023 / 2024 format
    if len(row) == 29:

        if not row[0]:
            return False

        branch_code = str(row[7]).strip()
        branch_name = str(row[8]).strip()

    # 2025 format
    elif len(row) == 31:

        if not row[0]:
            return False

        branch_code = str(row[6]).strip()
        branch_name = str(row[7]).strip()

    else:
        return False

    # Branch code must look like CSE, ECE, CSM, etc.
    if not branch_code.isalpha() or not (2 <= len(branch_code) <= 5):
        return False

    # Branch name must exist and not be numeric
    if not branch_name:
        return False

    if branch_name.isdigit():
        return False

    return True