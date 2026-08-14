from collections.abc import Callable

from django.http import HttpRequest, HttpResponse


class PersianDefaultLanguageMiddleware:
    """
    Make Persian the default/preferred language regardless of the browser.

    Django's LocaleMiddleware would otherwise pick the language from the
    Accept-Language header, sending e.g. English browsers to /en/. Dropping
    that header makes detection fall through to LANGUAGE_CODE ("fa") when the
    visitor hasn't explicitly chosen. An explicit choice (django_language
    cookie / session, set via the language switcher) still takes priority.

    Must run before django.middleware.locale.LocaleMiddleware.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request.META.pop("HTTP_ACCEPT_LANGUAGE", None)
        return self.get_response(request)
