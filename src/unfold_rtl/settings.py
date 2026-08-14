"""Helper to merge RTL/Persian defaults into a project's UNFOLD settings dict."""

from __future__ import annotations

from typing import Any, Callable

# Asset paths shipped by this package (served under STATIC_URL once collectstatic runs).
_STYLES = ["unfold_rtl/css/fonts.css", "unfold_rtl/css/unfold_custom.css"]
_SCRIPTS = ["unfold_rtl/js/unfold_custom.js"]

# Purple primary palette (Unfold expects "R G B" strings, no commas).
_DEFAULT_COLORS = {
    "primary": {
        "50": "250 245 255",
        "100": "243 232 255",
        "200": "233 213 255",
        "300": "216 180 254",
        "400": "192 132 252",
        "500": "168 85 247",
        "600": "147 51 234",
        "700": "126 34 206",
        "800": "107 33 168",
        "900": "88 28 135",
        "950": "59 7 100",
    },
}


def apply_unfold_rtl_defaults(
    unfold: dict[str, Any] | None = None,
    *,
    static: Callable[[str], str],
) -> dict[str, Any]:
    """Merge RTL/Persian STYLES, SCRIPTS and default COLORS into an UNFOLD dict.

    Non-destructive: the caller's keys win. STYLES/SCRIPTS from this package are
    appended after any the caller already set. COLORS is filled in only when the
    caller didn't provide one.

    `static` must be django.templatetags.static.static — Unfold requires each
    STYLES/SCRIPTS entry to be a `lambda request: ...` callable, which is built here.
    """
    result: dict[str, Any] = dict(unfold or {})

    result["STYLES"] = list(result.get("STYLES", [])) + [
        (lambda path: lambda request: static(path))(p) for p in _STYLES
    ]
    result["SCRIPTS"] = list(result.get("SCRIPTS", [])) + [
        (lambda path: lambda request: static(path))(p) for p in _SCRIPTS
    ]
    result.setdefault("COLORS", _DEFAULT_COLORS)
    # Show Unfold's built-in language switcher (uses your LANGUAGES setting +
    # the set_language view). Harmless with a single language configured.
    result.setdefault("SHOW_LANGUAGES", True)
    return result
