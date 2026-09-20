from __future__ import annotations

import datetime
from typing import Any

import jdatetime
from django.contrib import admin
from django.contrib.admin.filters import DateFieldListFilter
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from unfold.admin import (
    ModelAdmin as UnfoldModelAdmin,
    StackedInline as UnfoldStackedInline,
    TabularInline as UnfoldTabularInline,
)

from unfold_farsi.jalali import format_jalali
from unfold_farsi.widgets import (
    JalaliDateField,
    JalaliDateTimeField,
    JalaliDateWidget,
    JalaliSplitDateTimeWidget,
    JalaliTimeField,
    JalaliTimeWidget,
)


class JalaliAdminDateWidget(JalaliDateWidget):
    """Widget for editing DateField with Jalali calendar popup in Django Unfold Admin."""

    template_name = "unfold/widgets/date.html"

    def __init__(self, attrs: dict[str, Any] | None = None, format: str | None = None) -> None:
        default_attrs = {
            "class": (
                "jalali-datepicker border border-base-200 bg-white font-medium "
                "placeholder-base-400 rounded-default shadow-xs text-font-default-light text-sm "
                "focus:outline-2 focus:-outline-offset-2 focus:outline-primary-600 "
                "dark:bg-base-900 dark:border-base-700 dark:text-font-default-dark "
                "px-3 py-2 pe-10 w-full min-w-52"
            ),
            "data-jalali-datepicker": "true",
            "placeholder": "1404/01/01",
            "dir": "ltr",
            "size": "10",
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, format=format)


class JalaliAdminTimeWidget(JalaliTimeWidget):
    """Widget for editing TimeField with modern timepicker in Django Unfold Admin."""

    template_name = "unfold/widgets/time.html"

    def __init__(self, attrs: dict[str, Any] | None = None, format: str | None = "%H:%M") -> None:
        default_attrs = {
            "class": (
                "jalali-timepicker border border-base-200 bg-white font-medium "
                "placeholder-base-400 rounded-default shadow-xs text-font-default-light text-sm "
                "focus:outline-2 focus:-outline-offset-2 focus:outline-primary-600 "
                "dark:bg-base-900 dark:border-base-700 dark:text-font-default-dark "
                "px-3 py-2 pe-10 w-full min-w-52"
            ),
            "data-jalali-timepicker": "true",
            "placeholder": "12:00",
            "dir": "ltr",
            "size": "8",
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, format=format)


class JalaliAdminSplitDateTimeWidget(JalaliSplitDateTimeWidget):
    """Admin split widget combining JalaliAdminDateWidget and JalaliAdminTimeWidget."""

    template_name = "unfold/widgets/split_datetime.html"

    def __init__(
        self,
        attrs: dict[str, Any] | None = None,
        date_format: str | None = None,
        time_format: str | None = "%H:%M",
        date_attrs: dict[str, Any] | None = None,
        time_attrs: dict[str, Any] | None = None,
    ) -> None:
        widgets = (
            JalaliAdminDateWidget(attrs=date_attrs, format=date_format),
            JalaliAdminTimeWidget(attrs=time_attrs, format=time_format),
        )
        super(JalaliSplitDateTimeWidget, self).__init__(widgets, attrs)


class JalaliDateListFilter(DateFieldListFilter):
    """Admin list filter using Persian Jalali calendar periods (امروز, این ماه جلالی, امسال جلالی)."""

    def __init__(self, field: Any, request: Any, params: Any, model: Any, model_admin: Any, field_path: str) -> None:
        self.field_generic = f"{field_path}__"
        self.date_params = {k: v[-1] for k, v in params.items() if k.startswith(self.field_generic)}

        now = timezone.now()
        if timezone.is_aware(now):
            now = timezone.localtime(now)

        if isinstance(field, models.DateTimeField):
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            today = now.date()

        tomorrow = today + datetime.timedelta(days=1)

        # Compute Jalali boundaries
        jnow = (
            jdatetime.datetime.fromgregorian(datetime=now)
            if isinstance(today, datetime.datetime)
            else jdatetime.date.fromgregorian(date=today)
        )

        # Start of current Jalali month & next Jalali month
        j_month_start = jdatetime.date(jnow.year, jnow.month, 1)
        if jnow.month == 12:
            j_next_month_start = jdatetime.date(jnow.year + 1, 1, 1)
        else:
            j_next_month_start = jdatetime.date(jnow.year, jnow.month + 1, 1)

        # Start of current Jalali year & next Jalali year
        j_year_start = jdatetime.date(jnow.year, 1, 1)
        j_next_year_start = jdatetime.date(jnow.year + 1, 1, 1)

        g_month_start = j_month_start.togregorian()
        g_next_month_start = j_next_month_start.togregorian()
        g_year_start = j_year_start.togregorian()
        g_next_year_start = j_next_year_start.togregorian()

        if isinstance(field, models.DateTimeField):
            tz = timezone.get_current_timezone()
            month_start = timezone.make_aware(datetime.datetime.combine(g_month_start, datetime.time.min), tz)
            next_month_start = timezone.make_aware(datetime.datetime.combine(g_next_month_start, datetime.time.min), tz)
            year_start = timezone.make_aware(datetime.datetime.combine(g_year_start, datetime.time.min), tz)
            next_year_start = timezone.make_aware(datetime.datetime.combine(g_next_year_start, datetime.time.min), tz)
        else:
            month_start = g_month_start
            next_month_start = g_next_month_start
            year_start = g_year_start
            next_year_start = g_next_year_start

        self.lookup_kwarg_since = f"{field_path}__gte"
        self.lookup_kwarg_until = f"{field_path}__lt"

        self.links = (
            (_("همه تاریخ‌ها"), {}),
            (
                _("امروز"),
                {
                    self.lookup_kwarg_since: today,
                    self.lookup_kwarg_until: tomorrow,
                },
            ),
            (
                _("۷ روز گذشته"),
                {
                    self.lookup_kwarg_since: today - datetime.timedelta(days=7),
                    self.lookup_kwarg_until: tomorrow,
                },
            ),
            (
                _("این ماه (جلالی)"),
                {
                    self.lookup_kwarg_since: month_start,
                    self.lookup_kwarg_until: next_month_start,
                },
            ),
            (
                _("امسال (جلالی)"),
                {
                    self.lookup_kwarg_since: year_start,
                    self.lookup_kwarg_until: next_year_start,
                },
            ),
        )

        if field.null:
            self.lookup_kwarg_isnull = f"{field_path}__isnull"
            self.links += (
                (_("بدون تاریخ"), {self.field_generic + "isnull": True}),
                (_("دارای تاریخ"), {self.field_generic + "isnull": False}),
            )

        admin.FieldListFilter.__init__(self, field, request, params, model, model_admin, field_path)


class JalaliInlineMixin:
    """Mixin for Inlines providing Jalali admin widgets for DateField, DateTimeField, and TimeField."""

    def formfield_for_dbfield(self, db_field: Any, request: Any, **kwargs: Any) -> Any:
        if isinstance(db_field, models.DateTimeField):
            kwargs.setdefault("widget", JalaliAdminSplitDateTimeWidget)
            kwargs.setdefault("form_class", JalaliDateTimeField)
        elif isinstance(db_field, models.DateField):
            kwargs.setdefault("widget", JalaliAdminDateWidget)
            kwargs.setdefault("form_class", JalaliDateField)
        elif isinstance(db_field, models.TimeField):
            kwargs.setdefault("widget", JalaliAdminTimeWidget)
            kwargs.setdefault("form_class", JalaliTimeField)
        if hasattr(super(), "formfield_for_dbfield"):
            return super().formfield_for_dbfield(db_field, request, **kwargs)
        return db_field.formfield(**kwargs)


class JalaliModelAdminMixin(JalaliInlineMixin):
    """ModelAdmin mixin that displays Jalali dates in changelist and provides Jalali widgets in forms."""

    class Media:
        js = ("unfold_farsi/js/jalali-datepicker.js",)

    def get_list_display(self, request: Any) -> list[Any]:
        if hasattr(super(), "get_list_display"):
            list_display = list(super().get_list_display(request))
        else:
            list_display = list(getattr(self, "list_display", []))
        new_list_display = []

        for item in list_display:
            if isinstance(item, str):
                try:
                    field = self.model._meta.get_field(item)
                    if isinstance(field, (models.DateField, models.DateTimeField)):
                        method_name = f"_jalali_{item}"
                        if not hasattr(self, method_name):

                            def make_display(fname: str, is_dt: bool, vname: Any):
                                def display_func(admin_self: Any, obj: Any) -> str:
                                    val = getattr(obj, fname, None)
                                    if not val:
                                        return "-"
                                    fmt = "Y/m/d H:i" if is_dt else "Y/m/d"
                                    return format_jalali(val, format_str=fmt, latin=False)

                                display_func.short_description = vname
                                display_func.admin_order_field = fname
                                return display_func

                            bound_method = make_display(
                                item, isinstance(field, models.DateTimeField), field.verbose_name
                            ).__get__(self, self.__class__)
                            setattr(self, method_name, bound_method)
                        new_list_display.append(method_name)
                        continue
                except Exception:
                    pass
            new_list_display.append(item)

        return new_list_display


class ModelAdmin(JalaliModelAdminMixin, UnfoldModelAdmin):
    """Pre-configured Unfold ModelAdmin with automatic Jalali date and time support."""
    pass


class StackedInline(JalaliInlineMixin, UnfoldStackedInline):
    """Pre-configured Unfold StackedInline with automatic Jalali date and time support."""
    pass


class TabularInline(JalaliInlineMixin, UnfoldTabularInline):
    """Pre-configured Unfold TabularInline with automatic Jalali date and time support."""
    pass
