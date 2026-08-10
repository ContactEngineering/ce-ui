"""
View and URL plumbing for the ORCID requirement on publications.

The publication endpoints live in a separate plugin. Rather than reaching into
it, the site that composes the URL configuration wraps the routes that mint a
publication, which is where the requirement can be enforced no matter how the
request arrives -- the publication form, a script, or a direct POST.
"""

import functools

from django.core.exceptions import ImproperlyConfigured
from django.urls import URLPattern

from .identity import check_can_publish


def orcid_required(view_func):
    """
    Refuse the request unless the user has a connected ORCID account.

    Raises `PermissionDenied`, which Django renders as a 403 page and Django
    REST Framework as a 403 response carrying the explanation.
    """

    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        check_can_publish(request.user)
        return view_func(request, *args, **kwargs)

    return wrapper


def _normalize(route):
    """
    A route in a form that compares equal however the plugin spelled it.

    `path("publish/")` and `re_path(r"^publish/$")` describe the same endpoint
    but stringify differently, and the caller should not have to know which one
    the plugin happens to use.
    """
    return route.strip("^$").strip("/")


def require_orcid_for_routes(urlpatterns, routes):
    """
    Return a copy of `urlpatterns` with `routes` guarded by `orcid_required`.

    Parameters
    ----------
    urlpatterns : list of URLPattern
        The patterns of the plugin providing the routes, used unchanged apart
        from the ones named in `routes`.
    routes : iterable of str
        Route strings, exactly as the plugin declares them, e.g. `publish/`.

    Raises
    ------
    ImproperlyConfigured
        If a requested route is not among the patterns. A plugin that renames
        its publication endpoint would otherwise silently drop the requirement,
        which is the one failure mode this guard exists to prevent.
    """
    routes = {_normalize(route) for route in routes}
    seen = set()
    guarded = []

    for pattern in urlpatterns:
        route = _normalize(str(getattr(pattern, "pattern", "")))
        if isinstance(pattern, URLPattern) and route in routes:
            seen.add(route)
            pattern = URLPattern(
                pattern.pattern,
                orcid_required(pattern.callback),
                pattern.default_args,
                pattern.name,
            )
        guarded.append(pattern)

    missing = routes - seen
    if missing:
        raise ImproperlyConfigured(
            "Cannot require an ORCID iD for "
            f"{', '.join(sorted(missing))}: no such route. The publication "
            "plugin appears to have renamed its endpoints; update the list of "
            "guarded routes to match."
        )

    return guarded
