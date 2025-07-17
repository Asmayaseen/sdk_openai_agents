from datetime import datetime
from typing import Union

def format_date(date_obj: Union[datetime, str]) -> str:
    """
    Convert a datetime object or ISO date string into a formatted date string (YYYY-MM-DD).

    Args:
        date_obj (Union[datetime, str]): A datetime object or a date string in ISO format.

    Returns:
        str: Formatted date string in 'YYYY-MM-DD' format.

    Raises:
        ValueError: If input string is not a valid ISO date format.
        TypeError: If input is not a datetime or string.
    """
    if isinstance(date_obj, datetime):
        return date_obj.strftime("%Y-%m-%d")
    elif isinstance(date_obj, str):
        try:
            dt = datetime.fromisoformat(date_obj)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid ISO date string format. Expected format: YYYY-MM-DD")
    else:
        raise TypeError("date_obj must be a datetime object or ISO format string")
