from __future__ import annotations

from typing import Any

from django import template

from unfold_farsi.jalali import (
    format_jalali,
    jalali_relative_time,
    to_ascii_digits,
    to_persian_digits,
)

register = template.Library()


def _parse_format_and_latin(format_str: str | None, default_format: str) -> tuple[str, bool]:
    """Parse format string and optional latin flag from template filter argument."""
    if not format_str:
        return default_format, False

    fmt = str(format_str).strip()
    latin = False

    if fmt.lower() == "latin":
        return default_format, True

    if fmt.lower().endswith(":latin"):
        fmt = fmt[:-6]
        latin = True
    elif fmt.lower().endswith(",latin"):
        fmt = fmt[:-6]
        latin = True

    return fmt, latin


@register.filter(name="jdate")
def jdate_filter(value: Any, format_str: str | None = None) -> str:
    """Format date/datetime as Jalali date.

    Usage:
        {{ val|jdate }}                  -> ۱۴۰۳/۰۶/۲۵
        {{ val|jdate:"Y/m/d" }}           -> ۱۴۰۳/۰۶/۲۵
        {{ val|jdate:"j F Y" }}           -> ۲۵ شهریور ۱۴۰۳
        {{ val|jdate:"Y/m/d:latin" }}     -> 1403/06/25
    """
    if not value:
        return ""
    fmt, latin = _parse_format_and_latin(format_str, "Y/m/d")
    return format_jalali(value, format_str=fmt, latin=latin)


@register.simple_tag(name="jdate")
def jdate_tag(value: Any, format_str: str = "Y/m/d", latin: bool = False) -> str:
    """Template tag for formatting Jalali date.

    Usage:
        {% jdate val "Y/m/d" %}
        {% jdate val "Y/m/d" latin=True %}
    """
    if not value:
        return ""
    return format_jalali(value, format_str=format_str, latin=latin)


@register.filter(name="jdatetime")
def jdatetime_filter(value: Any, format_str: str | None = None) -> str:
    """Format date/datetime as Jalali date and time.

    Usage:
        {{ val|jdatetime }}               -> ۱۴۰۳/۰۶/۲۵ ۱۴:۳۰
        {{ val|jdatetime:"Y/m/d H:i" }}   -> ۱۴۰۳/۰۶/۲۵ ۱۴:۳۰
        {{ val|jdatetime:"j F · H:i" }}   -> ۲۵ شهریور · ۱۴:۳۰
        {{ val|jdatetime:"m/d H:i:latin" }} -> 06/25 14:30
    """
    if not value:
        return ""
    fmt, latin = _parse_format_and_latin(format_str, "Y/m/d H:i")
    return format_jalali(value, format_str=fmt, latin=latin)


@register.simple_tag(name="jdatetime")
def jdatetime_tag(value: Any, format_str: str = "Y/m/d H:i", latin: bool = False) -> str:
    """Template tag for formatting Jalali date and time."""
    if not value:
        return ""
    return format_jalali(value, format_str=format_str, latin=latin)


@register.filter(name="jtime")
def jtime_filter(value: Any, format_str: str | None = None) -> str:
    """Format time component of date/datetime.

    Usage:
        {{ val|jtime }}                   -> ۱۴:۳۰
        {{ val|jtime:"H:i:s" }}           -> ۱۴:۳۰:۰۰
        {{ val|jtime:"H:i:s:latin" }}     -> 14:30:00
    """
    if not value:
        return ""
    fmt, latin = _parse_format_and_latin(format_str, "H:i")
    return format_jalali(value, format_str=fmt, latin=latin)


@register.simple_tag(name="jtime")
def jtime_tag(value: Any, format_str: str = "H:i", latin: bool = False) -> str:
    """Template tag for formatting Jalali time."""
    if not value:
        return ""
    return format_jalali(value, format_str=format_str, latin=latin)


@register.filter(name="jdate_latin")
def jdate_latin_filter(value: Any, format_str: str = "Y/m/d") -> str:
    """Format date/datetime as Jalali date with Latin digits (e.g. for charts/inputs)."""
    if not value:
        return ""
    return format_jalali(value, format_str=format_str, latin=True)


@register.filter(name="jdatetime_latin")
def jdatetime_latin_filter(value: Any, format_str: str = "Y/m/d H:i") -> str:
    """Format date/datetime as Jalali date and time with Latin digits."""
    if not value:
        return ""
    return format_jalali(value, format_str=format_str, latin=True)


@register.filter(name="jrelative")
def jrelative_filter(value: Any) -> str:
    """Format date/datetime as natural Persian relative time (e.g. '۵ دقیقه پیش', 'دیروز')."""
    if not value:
        return ""
    return jalali_relative_time(value)


@register.filter(name="persian_digits")
def persian_digits_filter(value: Any) -> str:
    """Convert ASCII digits to Persian digits."""
    if value is None:
        return ""
    return to_persian_digits(value)


@register.filter(name="ascii_digits")
def ascii_digits_filter(value: Any) -> str:
    """Convert Persian or Arabic digits to ASCII digits."""
    if value is None:
        return ""
    return to_ascii_digits(value)
