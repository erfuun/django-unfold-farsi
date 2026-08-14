from pathlib import Path

from django.apps import AppConfig
from django.core.checks import Warning, register


class UnfoldRtlConfig(AppConfig):
    name = "unfold_rtl"
    verbose_name = "Unfold RTL / Persian"

    def ready(self) -> None:
        register(_check_wiring)
        _register_locale_path()


def _register_locale_path() -> None:
    """Expose this package's `locale/` via LOCALE_PATHS.

    The admin's `jsi18n` view builds its JavaScript catalog from
    `django.contrib.admin` + settings.LOCALE_PATHS only — it does *not* merge
    installed-app catalogs. So our `djangojs` fa strings (SelectFilter help text
    etc.) are only picked up once this dir is on LOCALE_PATHS.
    """
    from django.conf import settings

    locale_dir = str(Path(__file__).resolve().parent / "locale")
    paths = list(getattr(settings, "LOCALE_PATHS", []))
    if locale_dir not in paths:
        settings.LOCALE_PATHS = [*paths, locale_dir]


def _check_wiring(app_configs, **kwargs):
    """Warn when the host project wired the plugin in the wrong order."""
    from django.conf import settings

    warnings = []
    apps = list(getattr(settings, "INSTALLED_APPS", []))

    # unfold_rtl must precede unfold so its templates/static override Unfold's.
    if "unfold_rtl" in apps and "unfold" in apps:
        if apps.index("unfold_rtl") > apps.index("unfold"):
            warnings.append(
                Warning(
                    "'unfold_rtl' should come before 'unfold' in INSTALLED_APPS so its "
                    "template and static overrides take precedence.",
                    id="unfold_rtl.W001",
                )
            )

    mw = list(getattr(settings, "MIDDLEWARE", []))
    default = "unfold_rtl.middleware.PersianDefaultLanguageMiddleware"
    locale = "django.middleware.locale.LocaleMiddleware"
    if default not in mw:
        warnings.append(
            Warning(
                "unfold_rtl middleware is not installed. Add "
                f"'{default}' before '{locale}' in MIDDLEWARE.",
                id="unfold_rtl.W002",
            )
        )
    elif locale in mw and mw.index(default) > mw.index(locale):
        warnings.append(
            Warning(
                f"'{default}' should run before '{locale}'.",
                id="unfold_rtl.W003",
            )
        )
    return warnings
