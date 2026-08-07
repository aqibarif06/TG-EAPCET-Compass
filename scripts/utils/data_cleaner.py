import re


def clean_integer(value):
    """
    Converts values like:
    10000
    10000P
    10000*
    10000#
    into integers.
    """

    if value is None:
        return None

    value = str(value).strip()

    numbers = re.findall(r"\d+", value)

    if not numbers:
        return None

    return int(numbers[0])