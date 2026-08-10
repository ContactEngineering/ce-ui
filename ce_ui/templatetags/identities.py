"""Template access to the identity rules, for the connected-identities page."""

from django import template

from ce_ui.users.adapters import signup_providers

register = template.Library()


@register.simple_tag
def anchor_providers():
    """
    Providers that created an account and therefore cannot be disconnected.

    See `ce_ui.users.adapters.signup_providers`. Returns an empty list when the
    restriction is lifted, so a template can test membership either way.
    """
    return signup_providers() or []
