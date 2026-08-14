---
name: unfold-rtl-setup
description: >
  Hands-on guide for wiring django-unfold-rtl into a Django project and building
  a Persian / RTL Unfold admin. Use when a user asks to add RTL or Persian support
  to a django-unfold admin, integrate django-unfold-rtl, translate admin classes to
  Persian, or debug RTL layout / language-switching issues in Unfold. Self-contained:
  all examples are inline or under this skill's reference/ directory.
---

# django-unfold-rtl — setup & implementation skill

Turn a stock django-unfold admin into a Persian-first, right-to-left admin using
this package. Everything you need is in this skill — no external repo files.

- `reference/persian_admin_example.py` — a complete Persian Unfold admin
  covering widgets, filters, inlines, tabs, actions, badge displays and the
  prefix/suffix-icon gotcha. Copy patterns from it.

## Integration checklist

Work top to bottom. After each project change, run `python manage.py check` and
resolve any `unfold_rtl.W001–W003` warnings before moving on.

### 1. Install

```bash
pip install django-unfold-rtl        # or: uv add django-unfold-rtl
```

### 2. `INSTALLED_APPS` — `unfold_rtl` before `unfold`

```python
INSTALLED_APPS = [
    "unfold_rtl",   # MUST precede unfold — its template/static overrides win
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "django.contrib.admin",
    # ...project apps
]
```
Wrong order → `unfold_rtl.W001`.

### 3. `MIDDLEWARE` — before `LocaleMiddleware`

```python
MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "unfold_rtl.middleware.PersianDefaultLanguageMiddleware",  # before LocaleMiddleware
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    # ...
]
```
Missing → `W002`; after `LocaleMiddleware` → `W003`.

### 4. Language settings

```python
LANGUAGE_CODE = "fa"
LANGUAGES = [("fa", "فارسی"), ("en", "English")]
USE_I18N = True
```

### 5. `set_language` view (for the switcher)

```python
# urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin.site.urls),
]
```

### 6. Apply the UNFOLD helper

```python
from django.templatetags.static import static
from unfold_rtl.settings import apply_unfold_rtl_defaults

UNFOLD = apply_unfold_rtl_defaults(
    {"SITE_TITLE": "پنل مدیریت", "SITE_HEADER": "سایت من"},
    static=static,
)
```
Non-destructive: appends STYLES/SCRIPTS, defaults COLORS + `SHOW_LANGUAGES`,
caller keys win. `static` must be `django.templatetags.static.static`.

### 7. Collect static + verify

```bash
python manage.py collectstatic --noinput
python manage.py check          # expect: no issues
```

## Building Persian admin classes

Layout is handled automatically by the shipped CSS/JS — your job is only
**content**. See `reference/persian_admin_example.py` for a full worked example.
Core rules:

- Wrap every human-facing string in `gettext_lazy`:
  ```python
  from django.utils.translation import gettext_lazy as _
  ```
  then `description=_("راننده")`, fieldset titles `_("اطلاعات شخصی")`, action
  labels, filter titles, choice labels.
- Subclass Unfold's `ModelAdmin` (and `TabularInline`/`StackedInline`/
  `GenericStackedInline`) — never `django.contrib.admin.ModelAdmin`.
- Use `@display` / `@action` from `unfold.decorators` with Persian `description=`.
- `label={...}` on `@display` maps values to badge colors
  (`danger`/`warning`/`info`/`success`).
- Return `(value, obj.get_<field>_display())` from a `@display` so the color
  mapping keeps working while the Persian label shows:
  ```python
  @display(description=_("وضعیت"), label={"INACTIVE": "danger", "ACTIVE": "success"})
  def display_status(self, obj):
      return obj.status, obj.get_status_display()
  ```
- Prefix/suffix input icons are a known RTL trouble spot — set them in the form's
  `__init__` and eyeball them:
  ```python
  self.fields["first_name"].widget.attrs.update(
      {"prefix_icon": "search", "suffix_icon": "euro"}
  )
  ```

Do **not** ship `SIDEBAR`, `SITE_TITLE`, `SITE_ICON` from the package — set them
per project in the dict you pass to the helper.

## Do NOT

- Don't fork Unfold templates to fix layout — the package's scoped CSS already
  handles it. For a new RTL glitch, add a rule scoped to `html[dir="rtl"]` in
  the project's own stylesheet (loaded after Unfold) rather than patching templates.
- Don't hardcode `dir="rtl"` — it follows the active language automatically.
- Don't add a "Persian mode" flag; everything keys off the active language.

## Debugging

| Symptom | Likely cause |
|---------|--------------|
| Admin still LTR/English | `LANGUAGE_CODE` not `fa`, or middleware order wrong (`check`) |
| Fonts/CSS missing | `collectstatic` not run, or `unfold_rtl` after `unfold` |
| Bulk-actions "Run" clipped / bar collapses | package JS not served |
| `jsi18n` strings untranslated | catalog not compiled — `compilemessages` |
| Layout override not applying | rule not scoped to `html[dir="rtl"]`, or Unfold loads after |

## Translations workflow

```bash
django-admin makemessages -l fa
django-admin compilemessages      # requires GNU gettext (msgfmt)
```
Keep the `fa` catalog sorted/deduped with `msgcat --sort-output` if it grows.
