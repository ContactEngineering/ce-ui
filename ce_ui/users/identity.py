"""
The identities a user can sign in with, and the policy that depends on them.

A user reaches the site through one of several routes: an ORCID account, a
Google account, or a local account with an email address and a password. Any
number of these can be connected to the same user, and they can be connected in
any order -- somebody who registered with an email address today can add their
ORCID iD tomorrow.

One thing does depend on *which* identity is connected. Publishing a dataset
mints a citable, immutable record, and the person who mints it has to be
identifiable as a researcher, so a publication requires a connected ORCID
account. That rule lives here rather than in the publication code because it is
a statement about identity, and because the check has to be available to the UI
(to explain the requirement before somebody fills in a publication form) as
well as to the view layer (to enforce it).
"""

from django.core.exceptions import PermissionDenied

#: allauth provider id of ORCID.
ORCID_PROVIDER_ID = "orcid"

#: Human-readable names for the providers we know about. `SocialAccount` can
#: name its own provider, but only by going through the provider registry,
#: which needs the provider app to still be installed; a name is kept here so
#: an account whose provider was switched off is still listed as something
#: other than a bare id.
PROVIDER_NAMES = {
    ORCID_PROVIDER_ID: "ORCID",
    "google": "Google",
}

#: Shown wherever publishing is refused for a missing ORCID iD. The UI, the API
#: error and the documentation should all say the same thing.
ORCID_REQUIRED_FOR_PUBLICATION = (
    "Publishing a dataset requires a connected ORCID iD, because a publication "
    "is a citable record and its authors must be identifiable. Connect your "
    "ORCID account to your profile and then publish."
)


def _social_accounts(user):
    """
    All social accounts of `user`, or an empty list.

    Returns nothing for the anonymous user, and nothing when django-allauth's
    social account app is not installed -- the plugin has to keep working on a
    deployment that only offers local accounts.
    """
    if user is None or not getattr(user, "is_authenticated", False):
        return []
    if not getattr(user, "pk", None):
        return []

    try:
        from allauth.socialaccount.models import SocialAccount
    except ImportError:
        return []

    return list(SocialAccount.objects.filter(user_id=user.pk))


def provider_name(provider_id):
    """Human-readable name of a provider, e.g. `orcid` -> `ORCID`."""
    return PROVIDER_NAMES.get(provider_id, provider_id.replace("_", " ").title())


def has_orcid(user):
    """Whether an ORCID account is connected to this user."""
    return any(
        account.provider == ORCID_PROVIDER_ID for account in _social_accounts(user)
    )


def has_verified_email(user):
    """
    Whether a confirmed email address is on file for this user.

    This is what account recovery, password sign-in and -- because a Google
    account is recognised by its address -- Google sign-in all rest on. ORCID
    does not always pass an address on, so an account can start out with none.
    """
    if user is None or not getattr(user, "is_authenticated", False):
        return False
    if not getattr(user, "pk", None):
        return False

    try:
        from allauth.account.utils import \
            has_verified_email as _allauth_has_verified_email
    except ImportError:
        return False

    return _allauth_has_verified_email(user)


def connected_identities(user):
    """
    Describe every identity this user can sign in with.

    Returns a list of dictionaries with the keys `provider` (the allauth
    provider id, or `"local"` for the email/password account), `name` (for
    display), `uid` (the identifier at the provider, empty for the local
    account) and `url` (a link to the identity's public page, or `None`).

    A local account is reported when the user has a usable password: that is
    exactly the condition under which they can sign in with email and password.
    """
    identities = []

    for account in _social_accounts(user):
        url = None
        if account.provider == ORCID_PROVIDER_ID:
            url = f"https://orcid.org/{account.uid}"
        identities.append(
            {
                "provider": account.provider,
                "name": provider_name(account.provider),
                "uid": account.uid,
                "url": url,
            }
        )

    if getattr(user, "is_authenticated", False) and user.has_usable_password():
        identities.append(
            {
                "provider": "local",
                "name": "Email and password",
                "uid": user.email or "",
                "url": None,
            }
        )

    return identities


def can_publish(user):
    """Whether this user is allowed to publish a dataset."""
    return has_orcid(user)


def check_can_publish(user):
    """
    Raise `PermissionDenied` unless this user may publish a dataset.

    Django turns `PermissionDenied` into a 403, and Django REST Framework
    turns it into a 403 response carrying the message, so the reason reaches
    the browser either way.
    """
    if not can_publish(user):
        raise PermissionDenied(ORCID_REQUIRED_FOR_PUBLICATION)
