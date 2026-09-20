"""django-unfold-farsi — drop-in RTL/Persian support and sane defaults for django-unfold."""

from unfold_farsi.jalali import (
    format_jalali,
    jalali_relative_time,
    parse_jalali,
    to_ascii_digits,
    to_gregorian,
    to_jalali,
    to_persian_digits,
)
from unfold_farsi.settings import apply_unfold_farsi_defaults, apply_unfold_rtl_defaults

__version__ = "0.2.0"

_ADMIN_EXPORTS = {
    "ModelAdmin",
    "StackedInline",
    "TabularInline",
    "JalaliModelAdminMixin",
    "JalaliInlineMixin",
    "JalaliDateListFilter",
    "JalaliAdminDateWidget",
    "JalaliAdminTimeWidget",
    "JalaliAdminSplitDateTimeWidget",
}

_WIDGET_EXPORTS = {
    "JalaliDateWidget",
    "JalaliTimeWidget",
    "JalaliSplitDateTimeWidget",
    "JalaliDateField",
    "JalaliTimeField",
    "JalaliDateTimeField",
}

__all__ = [
    "__version__",
    "apply_unfold_farsi_defaults",
    "apply_unfold_rtl_defaults",
    "ModelAdmin",
    "StackedInline",
    "TabularInline",
    "JalaliModelAdminMixin",
    "JalaliInlineMixin",
    "JalaliDateListFilter",
    "JalaliAdminDateWidget",
    "JalaliAdminTimeWidget",
    "JalaliAdminSplitDateTimeWidget",
    "JalaliDateWidget",
    "JalaliTimeWidget",
    "JalaliSplitDateTimeWidget",
    "JalaliDateField",
    "JalaliTimeField",
    "JalaliDateTimeField",
    "to_jalali",
    "to_gregorian",
    "format_jalali",
    "jalali_relative_time",
    "parse_jalali",
    "to_persian_digits",
    "to_ascii_digits",
]


def __getattr__(name: str):
    if name in _ADMIN_EXPORTS:
        from unfold_farsi import admin

        return getattr(admin, name)
    if name in _WIDGET_EXPORTS:
        from unfold_farsi import widgets

        return getattr(widgets, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
