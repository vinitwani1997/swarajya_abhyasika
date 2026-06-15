from datetime import date


def add_months(d: date, months: int) -> date:
    """Add `months` to date `d`, clamping the day if the target month is shorter
    (e.g. Jan 31 + 1 month -> Feb 28/29)."""
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1

    if month == 12:
        next_month_first = date(year + 1, 1, 1)
    else:
        next_month_first = date(year, month + 1, 1)
    last_day_of_month = (next_month_first - date(year, month, 1)).days
    day = min(d.day, last_day_of_month)

    return date(year, month, day)
