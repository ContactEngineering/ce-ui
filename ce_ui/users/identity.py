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

from allauth.account import app_settings as account_settings
from django.conf import settings
from django.core.exceptions import PermissionDenied

#: allauth provider id of ORCID.
ORCID_PROVIDER_ID = "orcid"

#: The pseudo-provider id of the local email/password account. Not an allauth
#: provider: it stands for "signs in here, with a password".
LOCAL_PROVIDER_ID = "local"

#: Human-readable names for the providers we know about. `SocialAccount` can
#: name its own provider, but only by going through the provider registry,
#: which needs the provider app to still be installed; a name is kept here so
#: an account whose provider was switched off is still listed as something
#: other than a bare id.
PROVIDER_NAMES = {
    ORCID_PROVIDER_ID: "ORCID",
    "google": "Google",
    LOCAL_PROVIDER_ID: "Email and password",
}

#: Shown wherever publishing is refused for a missing ORCID iD. The UI, the API
#: error and the documentation should all say the same thing.
#: Deliberately says "publishing" rather than "publishing a dataset": the same
#: message answers the collection endpoint too.
ORCID_REQUIRED_FOR_PUBLICATION = (
    "Publishing requires a connected ORCID iD, because a publication is a "
    "citable record and its authors must be identifiable. Connect your ORCID "
    "account to your profile and then publish."
)


def signup_providers():
    """
    The identity providers that may bring a new account into existence.

    These providers *anchor* an account: an account always has one, because
    that is the only way it can have been created, and it cannot be
    disconnected afterwards. Every other way of signing in -- another provider,
    a password, a second email address -- is something the user attaches to an
    account that already exists.

    `None` lifts the restriction, letting any configured provider sign somebody
    up and every connection be removed again.
    """
    return getattr(settings, "SOCIALACCOUNT_SIGNUP_PROVIDERS", None)


def is_anchor_provider(provider_id):
    """Whether an account at this provider is what identifies its user."""
    providers = signup_providers()
    return providers is not None and provider_id in providers


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

    return list(SocialAccount.objects.filter(user_id=user.pk).order_by("date_joined"))


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

    This is what account recovery and password sign-in rest on. ORCID does not
    always pass an address on, so an account can start out with none.
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


def can_sign_in_locally(user):
    """
    Whether this user could sign in with an email address and a password.

    A usable password is not enough on its own. Under mandatory email
    verification django-allauth refuses the login of an account with no
    verified address and sends a confirmation instead -- and ORCID does not
    necessarily release an address, so such an account may have none at all.
    Counting the password alone would let somebody disconnect their last
    identity provider and lock themselves out, and would have the connected
    identities page name a way in that does not work.
    """
    if user is None or not getattr(user, "is_authenticated", False):
        return False
    if not user.has_usable_password():
        return False
    if (
        account_settings.EMAIL_VERIFICATION
        != account_settings.EmailVerificationMethod.MANDATORY
    ):
        return True
    return has_verified_email(user)


def can_remove_password(user):
    """
    Whether the password may be taken off this account.

    Only while something else still signs the user in. Every account here is
    anchored by the provider that created it (see `signup_providers`), so in
    practice there always is -- but an account with a password and nothing else
    would be locked out for good, and the rule should not depend on a setting
    somewhere else staying the way it is.
    """
    if user is None or not getattr(user, "is_authenticated", False):
        return False
    if not user.has_usable_password():
        return False
    return bool(_social_accounts(user))


def leaves_a_way_in(user, without_email=None):
    """
    Whether `user` could still sign in once `without_email` is gone.

    django-allauth guards the last address only when email is the *only* login
    method (`LOGIN_METHODS == {"email"}`). This site also accepts a username,
    so that guard never fires here, and an account whose password is its only
    way in could delete the address that password depends on -- after which it
    can neither be signed in to (mandatory verification refuses an account with
    no confirmed address) nor recovered (no address for a reset to reach).

    Mirrors what the login actually accepts, so it stays true to the rule it is
    protecting rather than to a summary of it.
    """
    if _social_accounts(user):
        return True
    if not user.has_usable_password():
        return False
    if (
        account_settings.EMAIL_VERIFICATION
        != account_settings.EmailVerificationMethod.MANDATORY
    ):
        # Username and password is enough; no address has to survive.
        return True

    try:
        from allauth.account.models import EmailAddress
    except ImportError:
        return False
    remaining = EmailAddress.objects.filter(user_id=user.pk, verified=True)
    if without_email is not None and without_email.pk:
        remaining = remaining.exclude(pk=without_email.pk)
    return remaining.exists()


def _identity_label(account):
    """
    What to show next to a social identity: whatever names it to a human.

    The uid is the provider's own identifier. For ORCID that *is* the iD one
    reads and cites; for anything else it is an opaque number, so an address
    the provider handed over is preferred where there is one.
    """
    if account.provider == ORCID_PROVIDER_ID:
        return account.uid
    extra_data = account.extra_data if isinstance(account.extra_data, dict) else {}
    return extra_data.get("email") or account.uid


def connected_identities(user):
    """
    Describe every identity this user can sign in with.

    Returns a list of dictionaries with the keys

    ``provider``
        the allauth provider id, or ``"local"`` for the email/password account
    ``name``
        for display
    ``uid``
        the identifier at the provider, the primary address for the local
        account
    ``url``
        a link to the identity's public page, or ``None``
    ``account_id``
        primary key of the underlying ``SocialAccount``, or ``None`` for the
        local account -- what the disconnect form posts back
    ``is_anchor``
        whether this identity created the account and therefore cannot be
        disconnected, see `signup_providers`
    ``usable``
        whether it can be signed in with *right now*. Only the local account
        can be unusable: a password is refused until an address is confirmed.

    A local account is reported when the user has a usable password, whether or
    not it can be used yet -- somebody who set one should see it listed, with
    the reason it does not work, rather than wonder where it went.
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
                "uid": _identity_label(account),
                "url": url,
                "account_id": account.pk,
                "is_anchor": is_anchor_provider(account.provider),
                "usable": True,
            }
        )

    if getattr(user, "is_authenticated", False) and user.has_usable_password():
        identities.append(
            {
                "provider": LOCAL_PROVIDER_ID,
                "name": provider_name(LOCAL_PROVIDER_ID),
                "uid": user.email or "",
                "url": None,
                "account_id": None,
                "is_anchor": False,
                "usable": can_sign_in_locally(user),
            }
        )

    return identities


def provider_of_email(user, email):
    """
    The connected provider that vouches for `email`, or `None`.

    An address a provider handed over is how its sign-in finds this account
    (see `docs/authentication.rst`), so it has to stay for as long as the
    provider is connected. Nothing links an address row to the account that
    supplied it, so the answer is read back out of what each provider stored.
    """
    if not email:
        return None
    wanted = email.lower()

    for account in _social_accounts(user):
        for candidate in _emails_from(account):
            if candidate.lower() == wanted:
                return account.provider
    return None


def _emails_from(account):
    """Every address a `SocialAccount` carries in its stored provider data."""
    extra_data = account.extra_data if isinstance(account.extra_data, dict) else {}

    # The provider knows how to read its own payload, which is worth more than
    # guessing at key names -- but it is only reachable when its app is still
    # installed and configured, and it wants a request in scope.
    try:
        provider = account.get_provider()
        addresses = provider.extract_email_addresses(extra_data)
    except Exception:  # noqa: BLE001 -- any provider/registry problem
        addresses = []
    emails = [address.email for address in addresses if address.email]

    # Fall back to the conventional key, which is where Google and ORCID put it.
    candidate = extra_data.get("email")
    if not emails and isinstance(candidate, str):
        emails = [candidate]
    return emails


def email_addresses(user):
    """
    Every address on the account, with what the page has to show for each.

    Returns dictionaries with `email`, `verified`, `primary`, `provider` (the
    id of a connected provider that vouches for the address, else `None`),
    `provider_name` and `removable`.

    `removable` comes from django-allauth's own `can_delete_email`, which this
    site extends in `AccountAdapter`, so the button appears exactly when the
    removal would be allowed rather than on a rule of the template's own.
    """
    if user is None or not getattr(user, "is_authenticated", False):
        return []
    if not getattr(user, "pk", None):
        return []

    try:
        from allauth.account.adapter import get_adapter
        from allauth.account.models import EmailAddress
    except ImportError:
        return []

    adapter = get_adapter()
    addresses = []
    for address in EmailAddress.objects.filter(user_id=user.pk).order_by(
        "-primary", "email"
    ):
        provider = provider_of_email(user, address.email)
        addresses.append(
            {
                "email": address.email,
                "verified": address.verified,
                "primary": address.primary,
                "provider": provider,
                "provider_name": provider_name(provider) if provider else None,
                "removable": adapter.can_delete_email(address),
            }
        )
    return addresses


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
