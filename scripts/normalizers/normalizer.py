from utils.data_cleaner import clean_integer


OLD_CATEGORY_COLUMNS = [
    "OC_BOYS",
    "OC_GIRLS",
    "BC_A_BOYS",
    "BC_A_GIRLS",
    "BC_B_BOYS",
    "BC_B_GIRLS",
    "BC_C_BOYS",
    "BC_C_GIRLS",
    "BC_D_BOYS",
    "BC_D_GIRLS",
    "BC_E_BOYS",
    "BC_E_GIRLS",
    "SC_BOYS",
    "SC_GIRLS",
    "ST_BOYS",
    "ST_GIRLS",
    "EWS_GEN_OU",
    "EWS_GIRLS_OU"
]


NEW_CATEGORY_COLUMNS = [
    "OC_BOYS",
    "OC_GIRLS",
    "BC_A_BOYS",
    "BC_A_GIRLS",
    "BC_B_BOYS",
    "BC_B_GIRLS",
    "BC_C_BOYS",
    "BC_C_GIRLS",
    "BC_D_BOYS",
    "BC_D_GIRLS",
    "BC_E_BOYS",
    "BC_E_GIRLS",
    "SC_I_BOYS",
    "SC_I_GIRLS",
    "SC_II_BOYS",
    "SC_II_GIRLS",
    "SC_III_BOYS",
    "SC_III_GIRLS",
    "ST_BOYS",
    "ST_GIRLS",
    "EWS_BOYS",
    "EWS_GIRLS"
]


def normalize_row(row, year, phase):

    # --------------------------------------------------
    # 2023 / 2024 FORMAT
    # --------------------------------------------------

    if year in (2023, 2024):

        college = {
            "collegeCode": row[0],
            "collegeName": row[1],
            "place": row[2],
            "district": row[3],
            "coEducation": row[4],
            "collegeType": row[5],
            "yearEstablished": clean_integer(row[6]),
            "tuitionFee": clean_integer(row[27]),
            "affiliatedTo": row[28]
        }

        branch_code = row[7]
        branch_name = row[8]

        cutoff_start = 9
        categories = OLD_CATEGORY_COLUMNS

    # --------------------------------------------------
    # 2025 FORMAT
    # --------------------------------------------------

    elif year == 2025:

        college = {
            "collegeCode": row[0],
            "collegeName": row[1],
            "place": row[2],
            "district": row[3],
            "coEducation": row[4],
            "collegeType": row[5],

            # Not present in 2025 PDF
            "yearEstablished": None,

            # Not present in 2025 PDF
            "tuitionFee": None,

            "affiliatedTo": row[30]
        }

        branch_code = row[6]
        branch_name = row[7]

        cutoff_start = 8
        categories = NEW_CATEGORY_COLUMNS

    else:
        raise ValueError(f"Unsupported EAPCET year: {year}")

    # --------------------------------------------------
    # Branch
    # --------------------------------------------------

    branch = {
        "collegeCode": row[0],
        "branchCode": branch_code,
        "branchName": str(branch_name).replace("\n", " ").strip()
    }

    # --------------------------------------------------
    # Cutoffs
    # --------------------------------------------------

    cutoffs = []

    for i, category in enumerate(categories):

        value = row[cutoff_start + i]

        if value in (None, "", "NA"):
            continue

        try:
            rank = clean_integer(value)

            if rank is None:
                continue

        except ValueError:
            continue

        cutoffs.append({
            "year": year,
            "phase": phase,
            "collegeCode": row[0],
            "branchCode": branch_code,
            "category": category,
            "closingRank": rank
        })

    return college, branch, cutoffs