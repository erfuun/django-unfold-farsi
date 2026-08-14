"""Self-contained reference: a Persian / RTL Unfold admin.

Distilled from a working django-unfold-rtl demo. It is illustrative — adapt the
model/field names to your project. The point is the *patterns*, all in one place:
gettext_lazy everywhere, Unfold base classes, @display badge colors, @action
buttons, inlines/tabs, and the prefix/suffix-icon RTL gotcha.

Prereqs (see SKILL.md): unfold_rtl wired into INSTALLED_APPS/MIDDLEWARE/UNFOLD,
LANGUAGE_CODE = "fa". Layout/RTL is automatic; this file is only *content*.
"""

from django import forms
from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.contrib.filters.admin import (
    BooleanRadioFilter,
    RangeNumericFilter,
    TextFilter,
)
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.decorators import action, display
from unfold.enums import ActionVariant
from unfold.widgets import UnfoldAdminTextInputWidget

from myapp.models import Driver, Race, Standing  # adapt to your project


# ── Custom text filter (Persian title) ────────────────────────────────────────
class FullNameFilter(TextFilter):
    title = _("نام کامل")
    parameter_name = "fullname"

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        return queryset.filter(last_name__icontains=value)


# ── Form: prefix/suffix icons are a known RTL trouble spot ─────────────────────
class DriverAdminForm(forms.ModelForm):
    custom_text_input = forms.CharField(
        label=_("ورودی متنی سفارشی"),
        required=False,
        widget=UnfoldAdminTextInputWidget,
    )

    class Meta:
        model = Driver
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eyeball these under RTL — the leading/trailing icons flip sides.
        self.fields["first_name"].widget.attrs.update(
            {"prefix_icon": "search", "suffix_icon": "euro"}
        )


# ── Inlines: subclass Unfold's, not django.contrib.admin's ─────────────────────
class DriverStandingInline(TabularInline):
    model = Standing
    fields = ["position", "points", "laps", "race"]
    extra = 0
    tab = True  # render as a tab on the change form


class RaceWinnerInline(StackedInline):
    model = Race
    fields = ["winner", "year", "laps"]
    extra = 0
    collapsible = True


@admin.register(Driver)
class DriverAdmin(ModelAdmin):
    form = DriverAdminForm
    search_fields = ["last_name", "first_name", "code"]
    compressed_fields = True
    list_filter = [FullNameFilter, ("is_active", BooleanRadioFilter)]
    list_filter_submit = True
    inlines = [DriverStandingInline, RaceWinnerInline]

    list_display = [
        "display_header",
        "display_status",
        "display_category",
        "is_active",
    ]

    # Persian fieldset titles + tabbed sections.
    fieldsets = [
        (None, {"fields": ["first_name", "last_name", "code", "salary"]}),
        (
            _("وضعیت"),
            {"classes": ["tab"], "fields": ["status", "category", "is_active"]},
        ),
    ]

    # Dropdown / dot / list of actions — labels in Persian.
    actions_list = [
        "action_reindex",
        {
            "title": _("بیشتر"),
            "variant": ActionVariant.PRIMARY,
            "items": ["action_optimize"],
        },
    ]
    actions_row = ["action_sync"]

    # ── @display: header, and badge-colored value displays ────────────────────
    @display(description=_("راننده"), header=True)
    def display_header(self, obj):
        # header=True → [title, subtitle, avatar-initials]
        return [obj.full_name, obj.code, obj.initials]

    @display(
        description=_("وضعیت"),
        label={"INACTIVE": "danger", "ACTIVE": "success"},
    )
    def display_status(self, obj):
        if not obj.status:
            return None
        # Return (value, label): value drives the color, label shows Persian text.
        return obj.status, obj.get_status_display()

    @display(
        description=_("دسته‌بندی"),
        label={
            "ROOKIE": "danger",
            "EXPERIENCED": "warning",
            "VETERAN": "info",
            "CHAMPION": "success",
        },
    )
    def display_category(self, obj):
        if not obj.category:
            return None
        return obj.category, obj.get_category_display()

    # ── @action: buttons that run server-side and redirect back ───────────────
    @action(description=_("بازسازی نمایه کش"), icon="database")
    def action_reindex(self, request):
        messages.success(request, _("نمایه کش بازسازی شد."))
        return redirect(reverse_lazy("admin:myapp_driver_changelist"))

    @action(description=_("بهینه‌سازی پرس‌وجوها"), icon="bolt")
    def action_optimize(self, request):
        messages.success(request, _("پرس‌وجوها بهینه شدند."))
        return redirect(reverse_lazy("admin:myapp_driver_changelist"))

    @action(description=_("همگام‌سازی"), url_path="actions-row-sync-driver")
    def action_sync(self, request, object_id):
        messages.success(request, _("راننده همگام‌سازی شد."))
        return redirect(reverse_lazy("admin:myapp_driver_changelist"))
