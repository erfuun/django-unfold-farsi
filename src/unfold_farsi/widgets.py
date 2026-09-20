from __future__ import annotations

import datetime
from typing import Any

from django import forms
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from unfold_farsi.jalali import format_jalali, parse_jalali, to_ascii_digits


class JalaliDateWidget(forms.DateInput):
    """Jalali datepicker widget for Django forms.

    Renders a text input with data attributes for auto-initialization by
    jalali-datepicker.js, formats Gregorian dates to Jalali for display,
    and converts Jalali inputs back to Gregorian on form submission.
    """

    template_name = "django/forms/widgets/text.html"
    input_type = "text"

    class Media:
        js = ("unfold_farsi/js/jalali-datepicker.js",)

    def __init__(self, attrs: dict[str, Any] | None = None, format: str | None = None) -> None:
        default_attrs = {
            "class": "jalali-datepicker",
            "data-jalali-datepicker": "true",
            "placeholder": "1404/01/01",
            "dir": "ltr",
            "autocomplete": "off",
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, format=format)

    def format_value(self, value: Any) -> str:
        if not value:
            return ""
        if isinstance(value, (datetime.date, datetime.datetime)):
            return format_jalali(value, format_str="Y/m/d", latin=True)
        if isinstance(value, str):
            clean = to_ascii_digits(value).strip()
            # If standard Gregorian ISO string, format to Jalali
            if "-" in clean and len(clean.split("-")[0]) == 4:
                try:
                    d = datetime.date.fromisoformat(clean)
                    return format_jalali(d, format_str="Y/m/d", latin=True)
                except ValueError:
                    pass
            return clean
        return str(value)

    def value_from_datadict(self, data: dict[str, Any], files: Any, name: str) -> Any:
        value = data.get(name)
        if value:
            clean = to_ascii_digits(str(value)).strip()
            try:
                gregorian_date = parse_jalali(clean)
                return gregorian_date.strftime("%Y-%m-%d")
            except ValueError:
                return value
        return value


class JalaliDateField(forms.DateField):
    """FormField that parses Jalali (e.g. 1404/01/15) and Gregorian (e.g. 2026-03-01) date strings into datetime.date."""

    widget = JalaliDateWidget

    default_error_messages = {
        "invalid": _("Enter a valid date (e.g. 1404/01/15)."),
    }

    def to_python(self, value: Any) -> datetime.date | None:
        if value in self.empty_values:
            return None
        if isinstance(value, datetime.date):
            return value
        if isinstance(value, datetime.datetime):
            return value.date()
        clean = to_ascii_digits(str(value)).strip()
        try:
            return parse_jalali(clean)
        except ValueError:
            raise forms.ValidationError(self.error_messages["invalid"], code="invalid")


class JalaliTimeWidget(forms.TimeInput):
    """Timepicker widget for Django forms with HH:MM format."""

    template_name = "django/forms/widgets/text.html"
    input_type = "text"

    class Media:
        js = ("unfold_farsi/js/jalali-datepicker.js",)

    def __init__(self, attrs: dict[str, Any] | None = None, format: str | None = "%H:%M") -> None:
        default_attrs = {
            "class": "jalali-timepicker",
            "data-jalali-timepicker": "true",
            "placeholder": "12:00",
            "dir": "ltr",
            "autocomplete": "off",
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, format=format)

    def format_value(self, value: Any) -> str:
        if not value:
            return ""
        if isinstance(value, datetime.time):
            return value.strftime("%H:%M")
        if isinstance(value, datetime.datetime):
            return value.strftime("%H:%M")
        clean = to_ascii_digits(str(value)).strip()
        parts = clean.split(":")
        if len(parts) >= 2:
            return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}"
        return clean

    def value_from_datadict(self, data: dict[str, Any], files: Any, name: str) -> Any:
        value = data.get(name)
        if value:
            return to_ascii_digits(str(value)).strip()
        return value


class JalaliTimeField(forms.TimeField):
    """FormField that parses time strings into datetime.time."""

    widget = JalaliTimeWidget

    default_error_messages = {
        "invalid": _("Enter a valid time (e.g. 14:30)."),
    }

    def to_python(self, value: Any) -> datetime.time | None:
        if value in self.empty_values:
            return None
        if isinstance(value, datetime.time):
            return value
        clean = to_ascii_digits(str(value)).strip()
        parts = clean.split(":")
        if len(parts) >= 2:
            try:
                h = int(parts[0])
                m = int(parts[1])
                s = int(parts[2]) if len(parts) >= 3 else 0
                if 0 <= h <= 23 and 0 <= m <= 59 and 0 <= s <= 59:
                    return datetime.time(h, m, s)
            except (ValueError, TypeError):
                pass
        raise forms.ValidationError(self.error_messages["invalid"], code="invalid")


class JalaliSplitDateTimeWidget(forms.MultiWidget):
    """Split widget for DateTime fields rendering JalaliDateWidget and JalaliTimeWidget."""

    template_name = "unfold/widgets/split_datetime.html"

    class Media:
        js = ("unfold_farsi/js/jalali-datepicker.js",)

    def __init__(
        self,
        attrs: dict[str, Any] | None = None,
        date_format: str | None = None,
        time_format: str | None = "%H:%M",
        date_attrs: dict[str, Any] | None = None,
        time_attrs: dict[str, Any] | None = None,
    ) -> None:
        widgets = (
            JalaliDateWidget(attrs=date_attrs, format=date_format),
            JalaliTimeWidget(attrs=time_attrs, format=time_format),
        )
        super().__init__(widgets, attrs)

    def decompress(self, value: Any) -> list[Any]:
        if not value:
            return [None, None]
        if isinstance(value, datetime.datetime):
            tz = timezone.get_current_timezone()
            if timezone.is_aware(value):
                value = timezone.localtime(value, tz)
            return [value.date(), value.time().strftime("%H:%M")]
        if isinstance(value, datetime.date):
            return [value, None]
        if isinstance(value, str):
            clean = to_ascii_digits(value).strip()
            parts = clean.split()
            if len(parts) == 2:
                return [parts[0], parts[1]]
            return [clean, None]
        return [None, None]

    def value_from_datadict(self, data: dict[str, Any], files: Any, name: str) -> Any:
        vals = super().value_from_datadict(data, files, name)
        if not vals or not vals[0]:
            return None
        date_part = vals[0]
        time_part = vals[1] if len(vals) > 1 and vals[1] else "00:00"
        return f"{date_part} {time_part}".strip()


class JalaliDateTimeField(forms.DateTimeField):
    """FormField that parses Jalali date and time inputs into datetime.datetime."""

    widget = JalaliSplitDateTimeWidget

    default_error_messages = {
        "invalid": _("Enter a valid date and time (e.g. 1404/01/15 14:30)."),
    }

    def to_python(self, value: Any) -> datetime.datetime | None:
        if value in self.empty_values:
            return None
        if isinstance(value, datetime.datetime):
            return value
        if isinstance(value, datetime.date):
            dt = datetime.datetime.combine(value, datetime.time.min)
            if getattr(settings, "USE_TZ", False):
                dt = timezone.make_aware(dt, timezone.get_current_timezone())
            return dt

        if isinstance(value, (list, tuple)):
            if not value or not value[0]:
                return None
            date_str = to_ascii_digits(str(value[0])).strip()
            time_str = to_ascii_digits(str(value[1])).strip() if len(value) > 1 and value[1] else "00:00"
        elif isinstance(value, str):
            clean = to_ascii_digits(value).strip()
            parts = clean.split()
            if not parts or not parts[0]:
                return None
            date_str = parts[0]
            time_str = parts[1] if len(parts) > 1 else "00:00"
        else:
            return None

        try:
            greg_date = parse_jalali(date_str)
        except ValueError:
            raise forms.ValidationError(self.error_messages["invalid"], code="invalid")

        t_parts = time_str.split(":")
        try:
            h = int(t_parts[0])
            m = int(t_parts[1]) if len(t_parts) > 1 else 0
            s = int(t_parts[2]) if len(t_parts) > 2 else 0
            if not (0 <= h <= 23 and 0 <= m <= 59 and 0 <= s <= 59):
                raise ValueError()
            greg_time = datetime.time(h, m, s)
        except (ValueError, IndexError):
            raise forms.ValidationError(self.error_messages["invalid"], code="invalid")

        dt = datetime.datetime.combine(greg_date, greg_time)
        if getattr(settings, "USE_TZ", False):
            tz = timezone.get_current_timezone()
            dt = timezone.make_aware(dt, tz)
        return dt
