from django.conf import settings
from django.shortcuts import reverse
from django.urls import NoReverseMatch
from topobank.authorization import get_anonymous_user

HEADLESS_ONLY = hasattr(settings, "HEADLESS_ONLY") and settings.HEADLESS_ONLY

# Default to headful mode, but allow to switch to headless mode
_no_anonymous_substitution_urls = []
if not HEADLESS_ONLY:
    # some abbreviations in order to save time on every request
    try:
        _no_anonymous_substitution_urls += [reverse("account_signup")]
    except NoReverseMatch:
        pass
    try:
        _no_anonymous_substitution_urls += [reverse("account_login")]
    except NoReverseMatch:
        pass


def anonymous_user_middleware(get_response):
    """Modify user of each request if not authenticated.

    Parameters
    ----------
    get_response
        Function which returns response giving a request.

    Returns
    -------
    Middleware function. Can be used in configuration of MIDDLEWARE.
    """

    def middleware(request):
        should_substitute = (
            HEADLESS_ONLY
            and not request.user.is_authenticated
        ) or (
            not HEADLESS_ONLY
            and not request.user.is_authenticated
            and request.path not in _no_anonymous_substitution_urls
        )
        if should_substitute:
            anonymous_user = get_anonymous_user()
            if anonymous_user is not None:
                request.user = anonymous_user

        response = get_response(request)
        return response

    return middleware
