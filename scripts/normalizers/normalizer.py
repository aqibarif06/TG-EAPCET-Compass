from utils.data_cleaner import clean_integer
CATEGORY_COLUMNS = [
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


def normalize_row(row, year, phase):
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

    branch = {
        "collegeCode": row[0],
        "branchCode": row[7],
        "branchName": row[8].replace("\n", " ")
    }

    cutoffs = []

    for i, category in enumerate(CATEGORY_COLUMNS):
        value = row[9 + i]

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
            "branchCode": row[7],
            "category": category,
            "closingRank": rank
        })

    return college, branch, cutoffs