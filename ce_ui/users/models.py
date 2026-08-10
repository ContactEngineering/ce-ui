from urllib.parse import urlparse

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.utils import ProgrammingError
from django.urls import resolve
from django.utils.translation import gettext_lazy as _
from topobank.authorization import get_anonymous_user

from .identity import connected_identities, has_orcid

_ANONYMOUS_USER_UNSET = object()


class ORCIDException(Exception):
    pass


class User(AbstractUser):
    # First name and last name (of the default `AbstractUser` model) do not cover name
    # patterns around the globe.
    name = models.CharField(_("Name of User"), max_length=255)

    # Cached anonymous user lookup. Sentinel distinguishes "not yet
    # loaded" from a legitimate ``None`` (no anonymous user configured).
    anonymous_user = _ANONYMOUS_USER_UNSET

    @property
    def display_name(self):
        """
        Name to show for this user, never empty.

        `name` can be blank: it is not validated as non-blank, and `save`
        derives it from first/last name, which are themselves optional. Falling
        back to the username keeps every human-readable rendering of a user
        (`str`, API payloads, staff dashboards) from collapsing to an empty
        string, which reads as a missing user rather than a nameless one.
        """
        return (self.name or "").strip() or self.get_username()

    def __str__(self):
        orcid_id = self.orcid_id
        if orcid_id:
            return "{} ({})".format(self.display_name, orcid_id)
        else:
            return self.display_name

    def save(self, *args, **kwargs):
        # Ensure the full name field is set. `strip()` matters on both sides:
        # a whitespace-only `name` is falsy for humans but truthy for Python,
        # and joining two empty names yields exactly that, which would then
        # stick forever because subsequent saves see a non-empty value.
        if not (self.name or "").strip():
            self.name = f"{self.first_name} {self.last_name}".strip()
        super().save(*args, **kwargs)

    def _get_anonymous_user(self):
        if self.anonymous_user is _ANONYMOUS_USER_UNSET:
            self.anonymous_user = get_anonymous_user()
        return self.anonymous_user

    def _orcid_info(self):  # TODO use local cache
        try:
            from allauth.socialaccount.models import SocialAccount
        except:  # noqa: E722
            raise ORCIDException("ORCID authentication not configured.")

        try:
            social_account = SocialAccount.objects.get(user_id=self.id, provider="orcid")
        except SocialAccount.DoesNotExist as exc:
            raise ORCIDException("No ORCID account existing for this user.") from exc
        except SocialAccount.MultipleObjectsReturned as exc:
            raise ORCIDException(
                "Cannot retrieve ORCID: Multiple social accounts returned."
            ) from exc

        try:
            orcid_info = social_account.extra_data["orcid-identifier"]
        except Exception as exc:
            raise ORCIDException(
                "Cannot retrieve ORCID info from local database."
            ) from exc

        return orcid_info

    @property
    def orcid_id(self) -> str:
        """
        Return ORCID iD, a unique 16-digit identifier for researchers.
        """
        try:
            return self._orcid_info()["path"]
        except ORCIDException:
            return None

    def orcid_uri(self):
        """
        Return the URI to the user's ORCID account, if available.
        """
        try:
            return self._orcid_info()["uri"]
        except ORCIDException:  # noqa: E722
            return None

    @property
    def has_orcid(self) -> bool:
        """
        Whether an ORCID account is connected to this user.

        Users can also sign in through Google or with an email address and a
        password, so an account does not necessarily carry an ORCID iD. Things
        that require one -- publishing, above all -- ask here.
        """
        return has_orcid(self)

    @property
    def connected_identities(self) -> list:
        """
        The identities this user can sign in with, for display.

        See `ce_ui.users.identity.connected_identities`.
        """
        return connected_identities(self)

    @property
    def is_anonymous(self):
        """
        Return whether user is anonymous.
        """
        try:
            anonymous_user = self._get_anonymous_user()
        except (ProgrammingError, self.DoesNotExist):
            return super().is_anonymous
        if anonymous_user is None:
            return False
        return self.id == anonymous_user.id

    @property
    def is_authenticated(self):
        """Return whether user is authenticated (not anonymous)."""
        try:
            anonymous_user = self._get_anonymous_user()
        except (ProgrammingError, self.DoesNotExist):
            return super().is_authenticated
        if anonymous_user is None:
            return True
        return self.id != anonymous_user.id

    class Meta:
        permissions = (
            ("can_skip_terms", "Can skip all checkings for terms and conditions."),
        )

    @classmethod
    def resolve(cls, url):
        """Resolve a user from a URL or integer ID."""
        try:
            pk = int(url)
            return cls.objects.get(pk=pk)
        except ValueError:
            match = resolve(urlparse(url).path)
            if match.view_name != "users:user-v1-detail":
                raise ValueError("URL does not resolve to a User instance")
            return cls.objects.get(**match.kwargs)


def resolve_user(url):
    """Resolve user from URL or ID. Prefer User.resolve(url)."""
    return User.resolve(url)
