from __future__ import annotations

import datetime
from typing import Any

import jdatetime
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime

# Set jdatetime default locale to Persian so month/weekday names are in Persian.
jdatetime.set_locale(jdatetime.FA_LOCALE)

PERSIAN_DIGITS_TRANS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
ASCII_DIGITS_TRANS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

PERSIAN_MONTHS = [
    "فروردین",
    "اردیبهشت",
    "خرداد",
    "تیر",
    "مرداد",
    "شهریور",
    "مهر",
    "آبان",
    "آذر",
    "دی",
    "بهمن",
    "اسفند",
]

# Jalali weekday names: in jdatetime weekday() 0 is Saturday, 6 is Friday.
PERSIAN_WEEKDAYS = [
    "شنبه",
    "یکشنبه",
    "دوشنبه",
    "سه‌شنبه",
    "چهارشنبه",
    "پنج‌شنبه",
    "جمعه",
]

PERSIAN_WEEKDAYS_SHORT = [
    "ش",
    "ی",
    "د",
    "س",
    "چ",
    "پ",
    "ج",
]


def to_persian_digits(value: Any) -> str:
    """Convert any ASCII digits in string or number representation to Persian digits."""
    if value is None:
        return ""
    return str(value).translate(PERSIAN_DIGITS_TRANS)


def to_ascii_digits(value: Any) -> str:
    """Convert any Persian or Arabic digits in string representation to ASCII digits."""
    if value is None:
        return ""
    return str(value).translate(ASCII_DIGITS_TRANS)


def to_jalali(
    value: datetime.date | datetime.datetime | str | None,
    tz: datetime.tzinfo | None = None,
) -> jdatetime.date | jdatetime.datetime | None:
    """Convert Python date, datetime, or ISO string to jdatetime date or datetime in current timezone."""
    if value is None or value == "":
        return None

    # If string, attempt parsing ISO format
    if isinstance(value, str):
        parsed = parse_datetime(value) or parse_date(value)
        if parsed is None:
            return None
        value = parsed

    # Already a jdatetime instance
    if isinstance(value, (jdatetime.date, jdatetime.datetime)):
        return value

    if tz is not None:
        target_tz = tz
    elif settings.configured:
        target_tz = timezone.get_current_timezone()
    else:
        target_tz = datetime.timezone.utc

    if isinstance(value, datetime.datetime):
        if settings.configured and timezone.is_aware(value):
            value = value.astimezone(target_tz)
        elif getattr(settings, "USE_TZ", False) if settings.configured else value.tzinfo is not None:
            if settings.configured:
                value = timezone.make_aware(value, target_tz)
            else:
                value = value.replace(tzinfo=target_tz)
        return jdatetime.datetime.fromgregorian(datetime=value)

    if isinstance(value, datetime.date):
        return jdatetime.date.fromgregorian(date=value)

    return None


def to_gregorian(
    value: jdatetime.date | jdatetime.datetime | None,
) -> datetime.date | datetime.datetime | None:
    """Convert a jdatetime date or datetime instance back to standard Gregorian Python date/datetime."""
    if value is None:
        return None
    if isinstance(value, jdatetime.datetime):
        return value.togregorian()
    if isinstance(value, jdatetime.date):
        return value.togregorian()
    return value


def format_jalali(
    value: datetime.date | datetime.datetime | str | None,
    format_str: str = "Y/m/d H:i",
    latin: bool = False,
    tz: datetime.tzinfo | None = None,
) -> str:
    """Format a date/datetime in Jalali (Solar Hijri) calendar with Django-compatible format tokens.

    Supported tokens:
    Y: 4-digit year (1403)
    y: 2-digit year (03)
    m: 2-digit month (01-12)
    n: 1-digit month (1-12)
    d: 2-digit day (01-31)
    j: 1-digit day (1-31)
    H: 24-hour (00-23)
    G: 24-hour without leading zeros (0-23)
    h: 12-hour (01-12)
    g: 12-hour without leading zeros (1-12)
    i: minutes (00-59)
    s: seconds (00-59)
    F: Full month name in Persian (فروردین)
    b: Short month name (فروردین)
    M: Short month name (فروردین)
    l: Full weekday name in Persian (شنبه)
    D: Short weekday name (ش)
    w: Numeric day of week (0 for Saturday)
    a: am/pm ('ق.ظ' / 'ب.ظ')
    A: AM/PM ('صبح' / 'عصر')
    """
    if value is None or value == "":
        return ""

    jdt = to_jalali(value, tz=tz)
    if jdt is None:
        return ""

    is_dt = isinstance(jdt, jdatetime.datetime)
    hour = jdt.hour if is_dt else 0
    minute = jdt.minute if is_dt else 0
    second = jdt.second if is_dt else 0
    hour12 = hour % 12 or 12

    # Map weekday (in jdatetime, weekday() 0 is Saturday)
    weekday_idx = jdt.weekday()
    weekday_name = PERSIAN_WEEKDAYS[weekday_idx] if 0 <= weekday_idx < len(PERSIAN_WEEKDAYS) else ""
    weekday_short = PERSIAN_WEEKDAYS_SHORT[weekday_idx] if 0 <= weekday_idx < len(PERSIAN_WEEKDAYS_SHORT) else ""
    month_name = PERSIAN_MONTHS[jdt.month - 1] if 1 <= jdt.month <= 12 else ""

    tokens = {
        "Y": f"{jdt.year:04d}",
        "y": f"{jdt.year % 100:02d}",
        "m": f"{jdt.month:02d}",
        "n": str(jdt.month),
        "d": f"{jdt.day:02d}",
        "j": str(jdt.day),
        "H": f"{hour:02d}",
        "G": str(hour),
        "h": f"{hour12:02d}",
        "g": str(hour12),
        "i": f"{minute:02d}",
        "s": f"{second:02d}",
        "F": month_name,
        "M": month_name,
        "b": month_name,
        "l": weekday_name,
        "D": weekday_short,
        "w": str(weekday_idx),
        "a": "ق.ظ" if hour < 12 else "ب.ظ",
        "A": "صبح" if hour < 12 else "عصر",
    }

    # If strftime format syntax was passed (e.g. "%Y/%m/%d %H:%M")
    if "%" in format_str:
        result = jdt.strftime(format_str)
    else:
        # Replace tokens character by character, honoring backslash escaping
        result_chars = []
        escaped = False
        for char in format_str:
            if escaped:
                result_chars.append(char)
                escaped = False
            elif char == "\\":
                escaped = True
            elif char in tokens:
                result_chars.append(tokens[char])
            else:
                result_chars.append(char)
        result = "".join(result_chars)

    if not latin:
        result = to_persian_digits(result)

    return result


def jalali_relative_time(
    value: datetime.date | datetime.datetime | str | None,
    now: datetime.datetime | None = None,
) -> str:
    """Return a natural Persian relative time string (e.g. 'چند لحظه پیش', '۵ دقیقه پیش', '۲ ساعت پیش', 'دیروز')."""
    if value is None or value == "":
        return ""

    if isinstance(value, str):
        parsed = parse_datetime(value) or parse_date(value)
        if parsed is None:
            return ""
        value = parsed

    if settings.configured:
        tz = timezone.get_current_timezone()
        current_now = now or timezone.now()
        if timezone.is_naive(current_now) and getattr(settings, "USE_TZ", False):
            current_now = timezone.make_aware(current_now, tz)

        if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
            # Convert date to datetime at start of day
            value = datetime.datetime.combine(value, datetime.time.min)

        if timezone.is_naive(value) and getattr(settings, "USE_TZ", False):
            value = timezone.make_aware(value, tz)
    else:
        tz = datetime.timezone.utc
        current_now = now or datetime.datetime.now(tz)
        if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
            value = datetime.datetime.combine(value, datetime.time.min, tzinfo=tz)
        elif isinstance(value, datetime.datetime) and value.tzinfo is None:
            value = value.replace(tzinfo=tz)

    delta = current_now - value
    seconds = int(delta.total_seconds())

    # Future date
    if seconds < 0:
        future_seconds = abs(seconds)
        if future_seconds < 60:
            return "چند لحظه بعد"
        minutes = future_seconds // 60
        if minutes < 60:
            return f"{to_persian_digits(minutes)} دقیقه بعد"
        hours = minutes // 60
        if hours < 24:
            return f"{to_persian_digits(hours)} ساعت بعد"
        days = future_seconds // 86400
        return f"{to_persian_digits(days)} روز بعد"

    # Past date
    if seconds < 60:
        return "چند لحظه پیش"

    minutes = seconds // 60
    if minutes < 60:
        return f"{to_persian_digits(minutes)} دقیقه پیش"

    hours = minutes // 60
    if hours < 24:
        return f"{to_persian_digits(hours)} ساعت پیش"

    days = seconds // 86400
    if days == 1:
        return "دیروز"
    if days < 7:
        return f"{to_persian_digits(days)} روز پیش"
    if days < 30:
        weeks = days // 7
        return f"{to_persian_digits(weeks)} هفته پیش"
    if days < 365:
        months = days // 30
        return f"{to_persian_digits(months)} ماه پیش"

    years = days // 365
    return f"{to_persian_digits(years)} سال پیش"


def parse_jalali(date_str: str) -> datetime.date:
    """Parse a Jalali date string (e.g. '1403/06/25', '۱۴۰۳/۰۶/۲۵', '1403-06-25') into a standard Gregorian datetime.date."""
    if not date_str:
        raise ValueError("Empty date string")

    clean_str = to_ascii_digits(date_str).strip()
    # Replace common separators
    clean_str = clean_str.replace("-", "/").replace(".", "/")
    parts = clean_str.split("/")

    if len(parts) != 3:
        raise ValueError(f"Invalid Jalali date format: '{date_str}'. Expected YYYY/MM/DD.")

    try:
        year = int(parts[0])
        month = int(parts[1])
        day = int(parts[2])
    except ValueError as exc:
        raise ValueError(f"Non-numeric values in date: '{date_str}'") from exc

    if year >= 1600:
        return datetime.date(year, month, day)

    try:
        jdate = jdatetime.date(year, month, day)
        return jdate.togregorian()
    except Exception as exc:
        raise ValueError(f"Invalid Jalali date '{date_str}': {exc}") from exc
