def is_valid_row(row):
    """
    Returns True only if the row looks like a valid college record.
    """

    if not row:
        return False

    if len(row) < 29:
        return False

    if row[0] is None:
        return False

    first = str(row[0]).strip()

    # Remove footer rows
    if first.startswith("8."):
        return False

    if first.startswith("9."):
        return False

    if first.startswith("Note"):
        return False

    # College code should usually be 4 uppercase letters
    if len(first) != 4:
        return False

    return True


def clean_rows(rows):
    return [row for row in rows if is_valid_row(row)]