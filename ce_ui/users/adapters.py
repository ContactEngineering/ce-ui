from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.core.exceptions import ValidationError


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
        Signing in through an identity provider always creates an account.

        The default implementation defers to the account adapter, which speaks
        for local registration only.
        """
        return True

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
        Refuse to remove the last way a user could sign back in.

        Accounts can otherwise be connected and disconnected freely: a user who
        registered with an email address can add their ORCID iD later, and one
        who signed up through Google can drop it again once another identity is
        in place.
        """
        remaining = [other for other in accounts if other.pk != account.pk]
        if remaining or account.user.has_usable_password():
            return
        raise ValidationError(
            "This is the only way you can sign in to your account. Set a "
            "password or connect another account before disconnecting this one."
        )
