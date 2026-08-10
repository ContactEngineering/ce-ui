"""
What happens when one person ends up with two accounts.

Signing in with ORCID and, on another day, with Google creates two separate
users: nothing links them, because an address handed over by a provider is not
treated as proof that the two identities are the same person. This module pins
what the site does when they then try to bring the two together, since the
answer is not obvious and a change in django-allauth would alter it silently.
"""

import pytest
from allauth.account.models import EmailAddress
from allauth.socialaccount.internal.flows.connect import do_connect
from allauth.socialaccount.models import SocialAccount, SocialLogin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import RequestFactory

from ce_ui.users.adapters import SocialAccountAdapter

ORCID_UID = "0000-0002-1825-0097"
GOOGLE_UID = "108176814012345678901"


@pytest.fixture
def orcid_user(db):
    """Signed up with ORCID. No password, no Google account."""
    user = get_user_model().objects.create(username="orcid-user", name="A Researcher")
    user.set_unusable_password()
    user.save()
    SocialAccount.objects.create(
        user=user,
        provider="orcid",
        uid=ORCID_UID,
        extra_data={
            "orcid-identifier": {
                "uri": f"https://orcid.org/{ORCID_UID}",
                "path": ORCID_UID,
                "host": "orcid.org",
            }
        },
    )
    return user


@pytest.fixture
def google_user(db):
    """The same person, signed up separately with Google. Also no password."""
    user = get_user_model().objects.create(
        username="google-user", name="A Researcher", email="researcher@example.com"
    )
    user.set_unusable_password()
    user.save()
    SocialAccount.objects.create(
        user=user,
        provider="google",
        uid=GOOGLE_UID,
        extra_data={"email": "researcher@example.com"},
    )
    return user


def _connect_attempt(as_user, provider, uid):
    """Drive allauth's connect flow as `as_user`, for an identity at `provider`."""
    request = RequestFactory().get("/accounts/3rdparty/")
    request.user = as_user
    sociallogin = SocialLogin(
        user=get_user_model()(), account=SocialAccount(provider=provider, uid=uid)
    )
    sociallogin.state = {"process": "connect"}
    sociallogin.lookup()
    return do_connect(request, sociallogin)


@pytest.mark.django_db
def test_two_sign_ups_produce_two_unrelated_accounts(orcid_user, google_user):
    assert orcid_user.pk != google_user.pk
    assert orcid_user.has_orcid
    assert not google_user.has_orcid  # ... so this one cannot publish


@pytest.mark.django_db
def test_connecting_an_identity_owned_by_another_account_is_refused(
    orcid_user, google_user
):
    """
    The Google identity already belongs to `google_user`, so the ORCID account
    cannot claim it. django-allauth refuses rather than moving the identity,
    which would leave the other account with no way to sign in.
    """
    with pytest.raises(ValidationError) as exception:
        _connect_attempt(orcid_user, "google", GOOGLE_UID)
    assert "already connected to a different account" in str(exception.value)

    # Nothing moved
    assert SocialAccount.objects.get(provider="google").user_id == google_user.pk
    assert not orcid_user.has_orcid or orcid_user.socialaccount_set.count() == 1


@pytest.mark.django_db
def test_connecting_an_unclaimed_identity_succeeds(orcid_user, google_socialapp):
    """The ordinary case: nobody else holds the identity, so it is connected."""
    _connect_attempt(orcid_user, "google", "an-unclaimed-google-uid")
    assert set(orcid_user.socialaccount_set.values_list("provider", flat=True)) == {
        "orcid",
        "google",
    }


@pytest.mark.django_db
def test_freeing_the_identity_requires_a_password_first(google_user):
    """
    The way out of a duplicate account, and why it is not a dead end.

    To hand the Google identity over to the ORCID account, it has to be
    disconnected from this one first -- but that is the only way into this
    account, so it is refused until another way in exists.
    """
    google_account = google_user.socialaccount_set.get()
    adapter = SocialAccountAdapter()

    with pytest.raises(ValidationError):
        adapter.validate_disconnect(google_account, [google_account])

    # Setting a password is the other way in, and the disconnect then succeeds
    google_user.set_password("a-very-secret-password")
    google_user.save()
    adapter.validate_disconnect(google_account, [google_account])


@pytest.mark.django_db
def test_a_password_alone_does_not_free_the_last_identity(orcid_user, settings):
    """
    A password is only a way back in if it can actually be used.

    Under mandatory verification, allauth refuses the login of an account with
    no verified address, and ORCID does not necessarily release one -- so
    letting the last identity go here would lock the account out for good.
    """
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    orcid_user.set_password("a-very-secret-password")
    orcid_user.save()
    orcid_account = orcid_user.socialaccount_set.get()

    with pytest.raises(ValidationError):
        SocialAccountAdapter().validate_disconnect(orcid_account, [orcid_account])

    EmailAddress.objects.create(
        user=orcid_user, email="researcher@example.org", verified=True, primary=True
    )
    SocialAccountAdapter().validate_disconnect(orcid_account, [orcid_account])
