"""Template access to the identity rules, for the connected-identities page."""

from allauth.socialaccount.adapter import get_adapter
from django import template

from ce_ui.users.identity import PROVIDER_NAMES, signup_providers

register = template.Library()


@register.simple_tag
def anchor_providers():
    """
    Providers that created an account and therefore cannot be disconnected.

    See `ce_ui.users.identity.signup_providers`. Returns an empty list when the
    restriction is lifted, so a template can test membership either way.
    """
    return signup_providers() or []


@register.simple_tag(takes_context=True)
def unconnected_providers(context):
    """
    The providers this user could still connect, in display order.

    Offering a provider that is already connected would send somebody through a
    whole OAuth handshake only to be told the account is already theirs, so the
    connect buttons are built from what is *missing* rather than from the full
    list. Mirrors django-allauth's own `get_providers`, minus the hidden ones.

    Returns ``{"id", "name"}`` pairs rather than provider objects: the names
    are the ones the rest of the site uses (django-allauth calls ORCID
    "Orcid"), and the id is all `provider_login_url` needs.
    """
    request = context["request"]
    user = getattr(request, "user", None)
    connected = set()
    if user is not None and user.is_authenticated:
        connected = set(user.socialaccount_set.values_list("provider", flat=True))

    providers = [
        {"id": provider.id, "name": PROVIDER_NAMES.get(provider.id, provider.name)}
        for provider in get_adapter().list_providers(request)
        if (not provider.uses_apps or not provider.app.settings.get("hidden"))
        and provider.id not in connected
    ]
    return sorted(providers, key=lambda provider: provider["name"])
