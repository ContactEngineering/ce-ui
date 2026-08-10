"""
An account is created with an ORCID iD and no other way.

ORCID is what identifies the researcher behind an account, and what publishing
requires, so it is the only provider that may bring one into existence. A
password, further email addresses and other identity providers are things a
user attaches to an account that already exists. This module pins that rule and
the two ways an account can still be reached afterwards.
"""

import pytest
from allauth.account.models import EmailAddress
from allauth.core import context
from allauth.socialaccount.adapter import get_adapter as get_social_adapter
from allauth.socialaccount.models import SocialAccount, SocialLogin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import RequestFactory
from django.urls import reverse

from ce_ui.users.adapters import AccountAdapter, SocialAccountAdapter

ORCID_UID = "0000-0002-1825-0097"


@pytest.fixture
def researcher(db):
    """An account as ORCID sign-up leaves it: no password, no address."""
    user = get_user_model().objects.create(username="researcher", name="A Researcher")
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


def _social_login(provider, uid, email=None, verified=True):
    """A social login as the provider hands it over, before it is processed."""
    sociallogin = SocialLogin(
        user=get_user_model()(), account=SocialAccount(provider=provider, uid=uid)
    )
    if email:
        sociallogin.email_addresses = [
            EmailAddress(email=email, verified=verified, primary=True)
        ]
    return sociallogin


def _authenticate_by_email(provider, uid, email, verified=True):
    """
    Run the address match the way a real request would.

    The per-provider `EMAIL_AUTHENTICATION` setting is read off the resolved
    provider, which in turn needs both its `SocialApp` row and a request in
    scope -- django-allauth keeps the latter in a context variable.
    """
    request = RequestFactory().get("/")
    with context.request_context(request):
        sociallogin = _social_login(provider, uid, email=email, verified=verified)
        sociallogin.provider = get_social_adapter().get_provider(request, provider)
        return SocialAccountAdapter().authenticate_by_email(sociallogin)


#
# Only ORCID creates accounts
#


@pytest.mark.django_db
def test_orcid_may_create_an_account():
    adapter = SocialAccountAdapter()
    assert adapter.is_open_for_signup(
        RequestFactory().get("/"), _social_login("orcid", ORCID_UID)
    )


@pytest.mark.django_db
def test_google_may_not_create_an_account():
    adapter = SocialAccountAdapter()
    assert not adapter.is_open_for_signup(
        RequestFactory().get("/"), _social_login("google", "12345")
    )


@pytest.mark.django_db
def test_local_registration_is_closed(client, orcid_socialapp):
    assert not AccountAdapter().is_open_for_signup(RequestFactory().get("/"))
    html = client.get(reverse("account_signup")).content.decode()
    assert "signup_form" not in html
    assert "ORCID" in html  # ... and the page says how to get an account


@pytest.mark.django_db
def test_lifting_the_restriction_lets_any_provider_sign_up(settings):
    settings.SOCIALACCOUNT_SIGNUP_PROVIDERS = None
    assert SocialAccountAdapter().is_open_for_signup(
        RequestFactory().get("/"), _social_login("google", "12345")
    )


#
# ORCID anchors the account
#


@pytest.mark.django_db
def test_orcid_cannot_be_disconnected(researcher):
    orcid = researcher.socialaccount_set.get(provider="orcid")
    google = SocialAccount.objects.create(
        user=researcher, provider="google", uid="12345"
    )
    with pytest.raises(ValidationError) as exception:
        SocialAccountAdapter().validate_disconnect(orcid, [orcid, google])
    assert "cannot be disconnected" in str(exception.value)


@pytest.mark.django_db
def test_google_can_be_disconnected(researcher):
    orcid = researcher.socialaccount_set.get(provider="orcid")
    google = SocialAccount.objects.create(
        user=researcher, provider="google", uid="12345"
    )
    SocialAccountAdapter().validate_disconnect(google, [orcid, google])


@pytest.mark.django_db
def test_the_page_offers_no_way_to_remove_the_orcid(client, researcher):
    client.force_login(researcher)
    html = client.get(reverse("socialaccount_connections")).content.decode()
    orcid = researcher.socialaccount_set.get(provider="orcid")
    assert f'value="{orcid.id}"' not in html  # no radio button for it
    assert "identifies you" in html


#
# Google finds an existing account by its confirmed address
#


@pytest.mark.django_db
def test_google_matches_an_account_with_that_confirmed_address(researcher, google_socialapp):
    EmailAddress.objects.create(
        user=researcher, email="researcher@example.org", verified=True, primary=True
    )
    match = _authenticate_by_email("google", "12345", email="researcher@example.org")
    assert match is not None
    assert match[0] == researcher


@pytest.mark.django_db
def test_google_does_not_match_an_unconfirmed_address(researcher, google_socialapp):
    """
    Somebody who merely claimed an address must not receive the sign-in of
    whoever really owns it at the provider. django-allauth would fall back to
    an unverified local address; the adapter refuses.
    """
    EmailAddress.objects.create(
        user=researcher, email="researcher@example.org", verified=False, primary=True
    )
    match = _authenticate_by_email("google", "12345", email="researcher@example.org")
    assert match is None


@pytest.mark.django_db
def test_google_does_not_match_when_the_provider_has_not_verified(researcher, google_socialapp):
    EmailAddress.objects.create(
        user=researcher, email="researcher@example.org", verified=True, primary=True
    )
    match = _authenticate_by_email("google", "12345", email="researcher@example.org", verified=False)
    assert match is None


@pytest.mark.django_db
def test_google_matches_nothing_when_no_account_holds_the_address(researcher, google_socialapp):
    match = _authenticate_by_email("google", "12345", email="nobody@example.org")
    assert match is None


#
# ... which is why an address matters
#


@pytest.mark.django_db
def test_an_account_without_a_confirmed_address_is_warned(client, researcher):
    client.force_login(researcher)
    html = client.get(reverse("socialaccount_connections")).content.decode()
    assert "No confirmed email address" in html

    EmailAddress.objects.create(
        user=researcher, email="researcher@example.org", verified=True, primary=True
    )
    html = client.get(reverse("socialaccount_connections")).content.decode()
    assert "No confirmed email address" not in html
