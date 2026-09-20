# django-unfold-farsi

> Drop-in **RTL / Persian** support and sane defaults for the
> [django-unfold](https://unfoldadmin.com/) admin.

`django-unfold-farsi` turns the Unfold admin into a polished right-to-left,
Persian-first experience with a single settings helper — no template forks, no
manual CSS patching. It bundles the [Vazirmatn](https://github.com/rastikerdar/vazirmatn)
font, a set of surgical `dir="rtl"` layout overrides, a translated login/logout
page, and language-forcing middleware. Everything is **i18n-driven**: RTL styling
activates only while the active language is bidirectional (`fa`, `ar`, `he`, …).
Switch the admin to English and you get Unfold's stock LTR look untouched.

[![PyPI version](https://img.shields.io/pypi/v/django-unfold-farsi.svg)](https://pypi.org/project/django-unfold-farsi/)
[![Python versions](https://img.shields.io/pypi/pyversions/django-unfold-farsi.svg)](https://pypi.org/project/django-unfold-farsi/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](#license)

---

## Table of contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Configuration](#configuration)
  - [1. `INSTALLED_APPS`](#1-installed_apps--order-matters)
  - [2. `MIDDLEWARE`](#2-middleware--bracket-localemiddleware)
  - [3. `UNFOLD`](#3-unfold--apply-the-defaults)
  - [4. Language switching](#4-language-switching-optional)
  - [5. Collect static](#5-collect-static)
- [Jalali Date & Time](#jalali-date--time)
- [How it works](#how-it-works)
- [API reference](#api-reference)
- [System checks](#system-checks)
- [What's shipped](#whats-shipped)
- [Customization](#customization)
- [Translations](#translations)
- [Compatibility](#compatibility)
- [FAQ](#faq)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)

---

## Features

- **One-call setup** — `apply_unfold_farsi_defaults()` merges STYLES, SCRIPTS and a
  default color palette into your existing `UNFOLD` dict. Your keys always win.
- **Modern Jalali Date & Time pickers** — zero-dependency standalone popup calendar
  and dual-column timepicker (`jalali-datepicker.js`), dark/light mode aware, suppressing
  broken Django `DateTimeShortcuts`.
- **Automatic Jalali ModelAdmin & Inlines** — `unfold_farsi.admin.ModelAdmin`,
  `StackedInline`, `TabularInline`, or `JalaliModelAdminMixin` dynamically formats
  changelist dates with Persian digits while preserving column sorting, and maps
  form fields to modern Jalali pickers.
- **Jalali Date List Filter** — `JalaliDateListFilter` provides Solar Hijri period
  filtering (`امروز`, `۷ روز گذشته`, `این ماه (جلالی)`, `امسال (جلالی)`).
- **Template tags & utilities** — `{% jdate %}`, `{% jdatetime %}`, `{% jtime %}`,
  `{% jrelative %}`, and digit converters with Persian and Latin numeral support.
- **True RTL layout** — every override is scoped to `html[dir="rtl"]`, covering
  the sidebar, dashboard, changelist, forms, inlines, buttons, breadcrumbs,
  tabs, date/select/select2 autocomplete widgets and the bulk-actions bar.
- **Self-hosted Vazirmatn font** — no external CDN; ships subsetted `woff2`
  files (arabic / latin / latin-ext) and applies them in RTL only.
- **Persian-first, still switchable** — middleware makes Persian the default
  regardless of the browser's `Accept-Language`, while an explicit language
  choice from the switcher is always honoured.
- **Translated auth screens** — Persianized login and logout templates plus a
  bundled `fa` message catalog for Unfold's own UI strings.
- **Guardrails** — Django system checks warn you when the app or middleware is
  wired in the wrong order.

---

## Requirements

| Dependency | Supported versions |
|------------|--------------------|
| Python     | 3.10 – 3.14        |
| Django     | 4.2 LTS – 6.1      |
| django-unfold | 0.20+           |
| jdatetime  | 5.0+               |

---

## Installation

```bash
pip install django-unfold-farsi
```

Using [uv](https://github.com/astral-sh/uv):

```bash
uv add django-unfold-farsi
```

From a local checkout (editable):

```bash
uv add --editable ../django-unfold-farsi
```

`django` and `django-unfold` are pulled in automatically as dependencies.

---

## Quick start

The minimum to go from a stock Unfold admin to RTL/Persian:

```python
# settings.py
from django.templatetags.static import static
from unfold_farsi.settings import apply_unfold_farsi_defaults

INSTALLED_APPS = [
    "unfold_farsi",   # before unfold
    "unfold",
    "django.contrib.admin",
    # ...
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "unfold_farsi.middleware.PersianDefaultLanguageMiddleware",  # before LocaleMiddleware
    "django.middleware.locale.LocaleMiddleware",
    # ...
]

LANGUAGE_CODE = "fa"
USE_I18N = True

UNFOLD = apply_unfold_farsi_defaults(
    {"SITE_TITLE": "پنل مدیریت", "SITE_HEADER": "سایت من"},
    static=static,
)
```

```bash
python manage.py collectstatic --noinput
python manage.py check      # confirms the wiring (see System checks)
```

That's it — open `/admin/` and you're in a Persian, right-to-left Unfold.

---

## Configuration

### 1. `INSTALLED_APPS` — order matters

Place `unfold_farsi` **before** `unfold` so its templates and static assets take
precedence over Unfold's originals.

```python
INSTALLED_APPS = [
    "unfold_farsi",   # must precede unfold so its template/static overrides win
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "django.contrib.admin",
    # ...your apps
]
```

### 2. `MIDDLEWARE` — bracket `LocaleMiddleware`

```python
MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "unfold_farsi.middleware.PersianDefaultLanguageMiddleware",  # before LocaleMiddleware
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    # ...
]
```

`PersianDefaultLanguageMiddleware` strips the incoming `Accept-Language` header
so Django's language detection falls through to `LANGUAGE_CODE` (`fa`) instead of
following the browser. An explicit choice from the language switcher (the
`django_language` cookie / session) still wins, so users can switch to English at
will. It **must** run before `LocaleMiddleware`.

### 3. `UNFOLD` — apply the defaults

Wrap your existing `UNFOLD` dict with the helper:

```python
from django.templatetags.static import static
from unfold_farsi.settings import apply_unfold_farsi_defaults

UNFOLD = apply_unfold_farsi_defaults(
    {
        "SITE_TITLE": "پنل مدیریت",
        "SITE_HEADER": "سایت من",
        # ...your project-specific SIDEBAR, SITE_ICON, COLORS, etc.
    },
    static=static,
)
```

The helper is **non-destructive**:

- Appends this package's `STYLES` and `SCRIPTS` after any you already declared.
- Fills in a purple `COLORS` palette **only if** you didn't set one.
- Sets `SHOW_LANGUAGES = True` (the language switcher) unless you override it.

Your own keys always take priority. `static` must be
`django.templatetags.static.static` — Unfold requires each asset entry to be a
`lambda request: ...` callable, which the helper builds for you.

> **Note** — `SIDEBAR`, `SITE_TITLE`, `SITE_ICON` and friends are intentionally
> **not** shipped; they're project-specific. Set them yourself in the dict you
> pass in.

### 4. Language switching (optional)

To let users switch languages, declare them and wire Django's `set_language`
view:

```python
# settings.py
LANGUAGE_CODE = "fa"
LANGUAGES = [("fa", "فارسی"), ("en", "English")]
USE_I18N = True
```

```python
# urls.py
from django.urls import include, path

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    # ...
]
```

Switch the admin to English and the RTL layout, Vazirmatn font and Persian copy
all deactivate automatically — you get a clean LTR English admin on Unfold's
default font.

### 5. Collect static

```bash
python manage.py collectstatic --noinput
```

---

## Jalali Date & Time

`django-unfold-farsi` ships a complete Jalali (Solar Hijri) calendar and modern time system that seamlessly integrates into Django Unfold.

### 1. ModelAdmin & Inlines

Use `unfold_farsi.admin.ModelAdmin` instead of `unfold.admin.ModelAdmin`:

```python
from django.contrib import admin
from unfold_farsi.admin import ModelAdmin, StackedInline, TabularInline, JalaliDateListFilter
from .models import Order, OrderItem

class OrderItemInline(TabularInline):
    model = OrderItem

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ["id", "customer", "created_at", "delivery_date"]
    list_filter = [("created_at", JalaliDateListFilter)]
    inlines = [OrderItemInline]
```

- **Automatic changelist formatting**: `DateField` and `DateTimeField` columns in `list_display` are dynamically formatted as Jalali dates (`۱۴۰۳/۰۶/۲۵`) while preserving sorting (`admin_order_field`) and column titles.
- **Form date & time pickers**: Form inputs for `DateField`, `TimeField`, and `DateTimeField` automatically render with the self-contained Jalali calendar and compact dual-column timepicker.
- **Jalali period filter**: `JalaliDateListFilter` provides quick filters (`امروز`, `۷ روز گذشته`, `این ماه (جلالی)`, `امسال (جلالی)`).

If you have an existing custom `ModelAdmin` base class, simply mix in `JalaliModelAdminMixin`:

```python
from unfold_farsi.admin import JalaliModelAdminMixin
from unfold.admin import ModelAdmin as BaseModelAdmin

class MyCustomAdmin(JalaliModelAdminMixin, BaseModelAdmin):
    pass
```

### 2. Standalone Form Widgets & Fields

You can use the Jalali widgets and fields in any standard Django `Form` or `ModelForm`:

```python
from django import forms
from unfold_farsi.widgets import (
    JalaliDateField,
    JalaliDateTimeField,
    JalaliTimeField,
    JalaliDateWidget,
    JalaliTimeWidget,
    JalaliSplitDateTimeWidget,
)

class EventForm(forms.Form):
    start_date = JalaliDateField(widget=JalaliDateWidget)
    start_time = JalaliTimeField(widget=JalaliTimeWidget)
    created_at = JalaliDateTimeField(widget=JalaliSplitDateTimeWidget)
```

Inputs accept Persian or Latin digits (`۱۴۰۳/۰۶/۲۵` or `1403/06/25`) and transparently convert back to Python `datetime.date`, `datetime.time`, and timezone-aware `datetime.datetime` objects.

### 3. Template Tags & Filters

Load `jalali_tags` in any Django template:

```html
{% load jalali_tags %}

<!-- Format date/datetime -->
{{ order.created_at|jdate }}                   <!-- ۱۴۰۳/۰۶/۲۵ -->
{{ order.created_at|jdate:"j F Y" }}           <!-- ۲۵ شهریور ۱۴۰۳ -->
{{ order.created_at|jdate:"Y/m/d:latin" }}     <!-- 1403/06/25 -->

<!-- Format datetime with time -->
{{ order.created_at|jdatetime }}               <!-- ۱۴۰۳/۰۶/۲۵ ۱۴:۳۰ -->
{{ order.created_at|jdatetime:"j F · H:i" }}   <!-- ۲۵ شهریور · ۱۴:۳۰ -->

<!-- Format time -->
{{ order.created_at|jtime }}                   <!-- ۱۴:۳۰ -->

<!-- Natural Persian relative time -->
{{ order.created_at|jrelative }}               <!-- ۵ دقیقه پیش / دیروز / ۳ ماه پیش -->

<!-- Digit converters -->
{{ "Order #1234"|persian_digits }}            <!-- Order #۱۲۳۴ -->
{{ "۱۲۳۴"|ascii_digits }}                      <!-- 1234 -->
```

### 4. Utility Functions

Direct calendar conversion and formatting functions:

```python
from unfold_farsi import format_jalali, to_jalali, parse_jalali, jalali_relative_time

# Formatting
format_jalali(datetime.date.today(), "Y/m/d")  # "۱۴۰۳/۰۶/۲۵"
format_jalali(datetime.date.today(), latin=True)  # "1403/06/25"

# Parsing
parse_jalali("۱۴۰۳/۰۶/۲۵")  # datetime.date(2024, 9, 15)

# Relative time
jalali_relative_time(past_datetime)  # "۲ ساعت پیش"
```

---

## How it works

**i18n-driven, not settings-driven.** Nothing keys off a "Persian mode" flag.
The overrides target `html[dir="rtl"]`, and Django sets `dir="rtl"` on the
`<html>` element whenever the active language is bidirectional. So the same build
serves a right-to-left Persian admin and a left-to-right English one depending
only on the active language.

**Three layers:**

1. **CSS** (`unfold_custom.css`) — logical mirroring of Unfold's physical
   `ml-*`/`mr-*` utilities, plus targeted fixes for widgets Unfold pins to a
   physical edge (date/time shortcut, select & select2 chevrons, timezone
   badge, collapsible/summary chevrons, accent bar, breadcrumb separator).
2. **JavaScript** (`unfold_custom.js`) — the few fixes CSS can't express:
   mirroring the inline offset Unfold sets on the bulk-actions bar from JS, and
   seeding Alpine's `changeListWidth` when its `ResizeObserver` reports `0`.
   Guarded by `document.documentElement.dir !== 'rtl'` — a no-op in LTR.
3. **Middleware + templates + locale** — Persian-default language selection and
   translated auth screens.

---

## API reference

### `apply_unfold_farsi_defaults(unfold=None, *, static)`

Merge this package's RTL/Persian defaults into an `UNFOLD` settings dict.
(Also aliased as `apply_unfold_rtl_defaults` for backwards compatibility).

| Parameter | Type | Description |
|-----------|------|-------------|
| `unfold`  | `dict \| None` | Your existing `UNFOLD` dict. Copied, not mutated. |
| `static`  | `Callable[[str], str]` | Must be `django.templatetags.static.static`. |

**Returns** a new `dict` with `STYLES`/`SCRIPTS` appended, `COLORS` defaulted, and
`SHOW_LANGUAGES` enabled — caller keys preserved.

### `PersianDefaultLanguageMiddleware`

`unfold_farsi.middleware.PersianDefaultLanguageMiddleware` — drops the request's
`Accept-Language` header so language detection falls back to `LANGUAGE_CODE`.
Must be listed before `django.middleware.locale.LocaleMiddleware`.

---

## System checks

Run `python manage.py check`. The app registers checks that surface common
wiring mistakes:

| ID | Warning |
|----|---------|
| `unfold_farsi.W001` | `unfold_farsi` is listed **after** `unfold` in `INSTALLED_APPS`. |
| `unfold_farsi.W002` | The middleware is not installed at all. |
| `unfold_farsi.W003` | The middleware runs **after** `LocaleMiddleware`. |

---

## What's shipped

| Path | Purpose |
|------|---------|
| `static/unfold_farsi/css/fonts.css` | Self-hosted Vazirmatn (`@font-face`), RTL only |
| `static/unfold_farsi/css/unfold_custom.css` | `html[dir="rtl"]` layout/typography overrides |
| `static/unfold_farsi/js/unfold_custom.js` | Runtime RTL fixups (RTL only) |
| `static/unfold_farsi/fonts/vazirmatn/*.woff2` | Subsetted font files |
| `templates/admin/login.html` | Translatable Unfold login page |
| `templates/registration/logged_out.html` | Translatable Unfold logout page |
| `locale/fa/LC_MESSAGES/` | Persian catalog for the strings above + Unfold UI |
| `unfold_farsi.middleware.PersianDefaultLanguageMiddleware` | Persian-default, switchable |
| `unfold_farsi.settings.apply_unfold_farsi_defaults` | The wiring helper |

---

## Customization

- **Colors** — pass your own `COLORS` in the `UNFOLD` dict and the helper leaves
  it alone. The bundled default is a purple `primary` ramp.
- **Extra CSS/JS** — declare your own `STYLES`/`SCRIPTS` in the dict; the
  package appends its assets after yours, so your rules can override.
- **A different font** — override the `font-family` under `html[dir="rtl"]` in a
  stylesheet loaded after this package's.

---

## Translations

The bundled `fa` catalog covers the auth templates plus Unfold's own UI strings
(Unfold ships no locale of its own). If you edit the translatable strings in the
templates, refresh the catalog:

```bash
django-admin makemessages -l fa
django-admin compilemessages   # requires GNU gettext
```

The package also registers its `locale/` directory on `LOCALE_PATHS` at startup
so the admin's `jsi18n` JavaScript catalog picks up the `djangojs` strings.

---

## Compatibility

Any RTL/bidirectional language works — the overrides key off `dir="rtl"`, which
Django sets for `fa`, `ar`, `he`, `ur`, etc. Persian is only the *default*; the
CSS itself is language-agnostic. The Vazirmatn font is optimised for Persian and
Arabic script.

---

## FAQ

**Does this affect the English admin?** No. Every override is scoped to
`html[dir="rtl"]`; in LTR you get stock Unfold.

**Do I need to set a Persian mode flag anywhere?** No. It follows the active
language via `dir="rtl"`.

**Can users still use English?** Yes — wire the language switcher (step 4). The
middleware only sets the *default*; an explicit choice always wins.

**The bulk-actions "Run" button is clipped / the bar collapses.** Make sure
`collectstatic` ran and `unfold_custom.js` is being served; those are the exact
issues it fixes.

---

## Development

```bash
git clone <your-fork-url>
cd django-unfold-farsi
uv sync                       # or: pip install -e .

# Run the bundled demo project
cd demo
python manage.py migrate
python manage.py runserver
```

The `demo/` project is a minimal Unfold admin wired exactly as the docs
describe — use it to see changes live.

---

## Contributing

Issues and pull requests are welcome. Please keep CSS overrides scoped to
`html[dir="rtl"]`, and run `python manage.py check` in the demo before
submitting.

---

## License

Released under the [MIT License](#license).

---

## Credits

- [django-unfold](https://unfoldadmin.com/) — the admin theme this builds on.
- [Vazirmatn](https://github.com/rastikerdar/vazirmatn) by Saber Rastikerdar —
  the bundled Persian font.
