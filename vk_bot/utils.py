from datetime import datetime


def calculate_age(birth_date_str: str) -> int:
    """Calculate the age based on the given birth date string.

    Args:
        birth_date_str (str): A string representing the birth date
            in the format "%d.%m.%Y".

    Returns:
        int: The calculated age based on the current date and
            the provided birth date.
    """
    today = datetime.today()
    birth_date = datetime.strptime(birth_date_str, "%d.%m.%Y")

    return today.year - birth_date.year - (today < birth_date)
