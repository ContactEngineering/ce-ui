from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.core.exceptions import ValidationError

from .identity import (can_sign_in_locally, is_anchor_provider,
                       leaves_a_way_in, provider_name, provider_of_email,
                       signup_providers)

# Re-exported: `signup_providers` used to live here, and the template tag and
# the tests reach for it under this name.
__all__ = ["AccountAdapter", "SocialAccountAdapter", "signup_providers"]


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

    def can_delete_email(self, email_address):
        """
        Whether this address may be removed from its account.

        django-allauth's own rules first: it keeps the primary address while
        others remain, and keeps the last one when signing in depends on it.

        On top of that, two rules of this site's own. An address a connected
        provider vouches for stays for as long as that provider is connected:
        it is how the provider's sign-in finds this account -- a Google sign-in
        is matched by address -- so removing it would quietly break a way in
        that the page above still lists as working. Disconnecting the provider
        first releases it.

        And the last address of an account that signs in with a password and
        nothing else stays, because allauth's own guard for that case only
        fires when email is the sole login method, which it is not here; see
        `leaves_a_way_in`.

        Consulted by `allauth.account.internal.flows.manage_email.delete_email`,
        so the rule holds for anything that removes an address, not only for
        the button on the connected identities page.
        """
        if not super().can_delete_email(email_address):
            return False
        if provider_of_email(email_address.user, email_address.email) is not None:
            return False
        return leaves_a_way_in(email_address.user, without_email=email_address)

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

    def can_authenticate_by_email(self, login, email):
        """
        Whether a sign-in at this provider may reach an account by `email`.

        django-allauth offers the address to any local account holding it,
        preferring a verified one but falling back to an unverified one -- and
        falling back further to the raw `User.email` field, which nobody ever
        confirmed. That would let somebody who had merely *claimed* an address
        receive the sign-in of whoever really owns it at the provider. Only an
        address confirmed here counts.

        This is the hook django-allauth consults per address in
        `SocialLogin._lookup_by_email`, immediately before it looks a user up,
        so refusing here is what actually stops the match. The base
        implementation decides whether email authentication is switched on for
        the provider at all; that answer still stands.
        """
        if not super().can_authenticate_by_email(login, email):
            return False
        return EmailAddress.objects.filter(email__iexact=email, verified=True).exists()

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
        if is_anchor_provider(account.provider):
            raise ValidationError(
                f"Your {provider_name(account.provider)} account identifies you "
                "on this site and cannot be disconnected. Contact support if it "
                "has to be changed."
            )
        remaining = [other for other in accounts if other.pk != account.pk]
        if remaining or can_sign_in_locally(account.user):
            return
        raise ValidationError(
            "This is the only way you can sign in to your account. Connect "
            "another account, or set a password and confirm your email "
            "address, before disconnecting this one."
        )
