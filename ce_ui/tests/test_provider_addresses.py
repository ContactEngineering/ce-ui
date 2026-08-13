"""
Addresses that arrive with a connected identity provider.

django-allauth stores them when a provider creates an account, but not when one
is connected to an existing account. Here it does both: an address is how a
Google sign-in finds its account, and how the account is recovered.
"""

import pytest
from allauth.account.models import EmailAddress
from allauth.core import context
from allauth.socialaccount.models import SocialAccount, SocialLogin
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.urls import reverse


@pytest.fixture(autouse=True)
def _google_is_configured(google_socialapp):
    """
    Connecting an account sends a notification mail, and rendering it resolves
    the provider -- which needs its `SocialApp` row.
    """
    return google_socialapp


@pytest.fixture
def researcher(db):
    """An account as ORCID sign-up leaves it: no password, no address."""
    user = get_user_model().objects.create(username="researcher", name="A Researcher")
    user.set_unusable_password()
    user.save()
    SocialAccount.objects.create(user=user, provider="orcid", uid="0000-0002-1825-0097")
    return user


def connect_google(user, email=None, verified=True, uid="12345"):
    """Connect a Google account the way the connect flow does."""
    request = RequestFactory().get("/")
    request.session = {}
    # Connecting sends a notification mail, and rendering it runs the context
    # processors, which read the request's user
    request.user = user
    addresses = (
        [EmailAddress(email=email, verified=verified, primary=True)] if email else []
    )
    with context.request_context(request):
        sociallogin = SocialLogin(
            user=user,
            account=SocialAccount(provider="google", uid=uid),
            email_addresses=addresses,
        )
        sociallogin.connect(request, user)


def _addresses(user):
    return set(
        EmailAddress.objects.filter(user=user).values_list("email", "verified")
    )


@pytest.mark.django_db
def test_a_verified_address_is_stored(researcher):
    connect_google(researcher, email="researcher@gmail.com")
    assert _addresses(researcher) == {("researcher@gmail.com", True)}


@pytest.mark.django_db
def test_the_first_address_becomes_the_primary_one(researcher):
    connect_google(researcher, email="researcher@gmail.com")
    stored = EmailAddress.objects.get(user=researcher)
    assert stored.primary
    researcher.refresh_from_db()
    assert researcher.email == "researcher@gmail.com"


@pytest.mark.django_db
def test_an_existing_primary_address_is_left_alone(researcher):
    EmailAddress.objects.create(
        user=researcher, email="work@example.org", verified=True, primary=True
    )
    connect_google(researcher, email="researcher@gmail.com")
    assert _addresses(researcher) == {
        ("work@example.org", True),
        ("researcher@gmail.com", True),
    }
    assert EmailAddress.objects.get(user=researcher, primary=True).email == (
        "work@example.org"
    )


@pytest.mark.django_db
def test_an_unverified_address_is_not_stored(researcher):
    """A provider that has not confirmed an address is making a claim."""
    connect_google(researcher, email="researcher@gmail.com", verified=False)
    assert _addresses(researcher) == set()


@pytest.mark.django_db
def test_an_address_held_by_another_account_is_not_taken(researcher):
    """
    Addresses are unique across accounts, and taking one would hand over the
    sign-in of whoever holds it.
    """
    other = get_user_model().objects.create(username="other", name="Other")
    EmailAddress.objects.create(
        user=other, email="researcher@gmail.com", verified=True, primary=True
    )
    connect_google(researcher, email="researcher@gmail.com")

    assert _addresses(researcher) == set()
    assert EmailAddress.objects.get(email="researcher@gmail.com").user_id == other.pk


@pytest.mark.django_db
def test_reconnecting_does_not_duplicate(researcher):
    connect_google(researcher, email="researcher@gmail.com")
    connect_google(researcher, email="researcher@gmail.com", uid="67890")
    assert EmailAddress.objects.filter(user=researcher).count() == 1


#
# Removing the last address is allowed, but says what it costs
#


@pytest.mark.django_db
def test_the_only_address_is_flagged_before_it_is_removed(client, researcher):
    EmailAddress.objects.create(
        user=researcher, email="only@example.org", verified=True, primary=True
    )
    client.force_login(researcher)
    html = client.get(reverse("account_email")).content.decode()
    assert "This is your only email address" in html

    EmailAddress.objects.create(
        user=researcher, email="second@example.org", verified=False, primary=False
    )
    html = client.get(reverse("account_email")).content.decode()
    assert "This is your only email address" not in html


@pytest.mark.django_db
def test_the_last_address_can_still_be_removed(client, researcher):
    EmailAddress.objects.create(
        user=researcher, email="only@example.org", verified=True, primary=True
    )
    researcher.set_password("a-very-secret-password")
    researcher.save()
    client.force_login(researcher)

    client.post(
        reverse("account_email"),
        {"email": "only@example.org", "action_remove": ""},
        follow=True,
    )
    assert not EmailAddress.objects.filter(user=researcher).exists()
    # The ORCID account is untouched, so the user can still sign in
    assert researcher.has_orcid
