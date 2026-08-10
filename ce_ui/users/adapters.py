from allauth.account import app_settings as account_settings
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from allauth.account.utils import has_verified_email
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.core.exceptions import ValidationError

from .identity import provider_name


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


def _can_sign_in_locally(user):
    """
    Whether this user could sign in with an email address and a password.

    A usable password is not enough on its own. Under mandatory email
    verification django-allauth refuses the login of an account with no
    verified address and sends a confirmation instead -- and ORCID does not
    necessarily release an address, so such an account may have none at all.
    Counting the password alone would let somebody disconnect their last
    identity provider and lock themselves out.
    """
    if not user.has_usable_password():
        return False
    if (
        account_settings.EMAIL_VERIFICATION
        != account_settings.EmailVerificationMethod.MANDATORY
    ):
        return True
    return has_verified_email(user)


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        """
        Whether somebody may register a local email/password account.

        Controlled by `ACCOUNT_ALLOW_SIGNUP` so a deployment can offer social
        login only. Note that django-allauth's social adapter consults this
        method too; `SocialAccountAdapter` below overrides that, so switching
        local registration off does not also close the door on ORCID and
        Google.
        """
        return getattr(settings, "ACCOUNT_ALLOW_SIGNUP", True)

    def save_user(self, request, user, form, commit=True):
        """
        This is called when saving user via allauth registration.
        We override this to set additional data on user object.
        """
        # Do not persist the user yet so we pass commit=False
        # (last argument)
        user = super().save_user(request, user, form, commit=False)
        # The signup form carries a full name, but other callers of this
        # adapter (password reset flows, tests) may not. `User.save` falls back
        # to the first/last name pair when the name is left blank.
        user.name = form.cleaned_data.get("name") or user.name
        user.save()
        return user


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        """
        Whether this provider may bring a new account into existence.

        Only the providers in `SOCIALACCOUNT_SIGNUP_PROVIDERS` may; signing in
        through any other one reaches an existing account or nothing at all.
        django-allauth turns a `False` here into `account/signup_closed.html`,
        which explains how to get an account.

        The default implementation defers to the account adapter, which speaks
        for local registration only, so this override is what keeps closing
        local registration from also closing the door on ORCID.
        """
        providers = signup_providers()
        if providers is None:
            return True
        account = getattr(sociallogin, "account", None)
        return account is not None and account.provider in providers

    def authenticate_by_email(self, sociallogin):
        """
        Match a social login against an existing account by email address.

        django-allauth offers the address to any local account holding it,
        preferring a verified one but falling back to an unverified one. That
        fallback would let somebody who had merely *claimed* an address --
        without ever confirming it -- receive the sign-in of whoever really
        owns it at the provider. Only a confirmed address counts here.
        """
        match = super().authenticate_by_email(sociallogin)
        if match is None:
            return None
        user, email = match
        if not EmailAddress.objects.filter(
            user=user, email__iexact=email, verified=True
        ).exists():
            return None
        return match

    def populate_user(self, request, sociallogin, data):
        """
        Fill in the full name from what the provider told us about the user.

        ORCID and Google both supply a name, in one field or as a first/last
        pair depending on the provider; without this the account would start
        out nameless and be shown by username everywhere.
        """
        user = super().populate_user(request, sociallogin, data)
        name = (data.get("name") or "").strip()
        if not name:
            name = " ".join(
                part
                for part in (data.get("first_name"), data.get("last_name"))
                if part
            ).strip()
        if name:
            user.name = name
        return user

    def validate_disconnect(self, account, accounts):
        """
        Refuse to remove an account's anchor, or the last way back in.

        The provider that created the account stays: it is what identifies the
        person behind it, and what publishing requires. Everything else can be
        connected and disconnected freely, as long as one way of signing back
        in remains.
        """
        providers = signup_providers()
        if providers is not None and account.provider in providers:
            raise ValidationError(
                f"Your {provider_name(account.provider)} account identifies you "
                "on this site and cannot be disconnected. Contact support if it "
                "has to be changed."
            )
        remaining = [other for other in accounts if other.pk != account.pk]
        if remaining or _can_sign_in_locally(account.user):
            return
        raise ValidationError(
            "This is the only way you can sign in to your account. Connect "
            "another account, or set a password and confirm your email "
            "address, before disconnecting this one."
        )
