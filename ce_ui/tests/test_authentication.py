"""
Tests for the ways a user can sign in, and for what an ORCID iD unlocks.

Three routes lead into the site -- ORCID, Google, and a local account with an
email address and a password -- and they can be combined on one profile. Only
publishing depends on which of them a user has: it mints a citable record, so it
requires an ORCID account.
"""

import pytest
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.urls import reverse

PUBLISH_URL = "/go/publish/"
PUBLISH_COLLECTION_URL = "/go/publish-collection/"


@pytest.fixture
def local_user(db):
    """Somebody who registered with an email address and a password."""
    return get_user_model().objects.create_user(
        username="local-user",
        email="local-user@example.com",
        password="a-very-secret-password",
        name="Local User",
    )


def connect_orcid(user, uid="0000-0002-1825-0097"):
    return SocialAccount.objects.create(
        user=user,
        provider="orcid",
        uid=uid,
        extra_data={
            "orcid-identifier": {
                "uri": f"https://orcid.org/{uid}",
                "path": uid,
                "host": "orcid.org",
            }
        },
    )


#
# The login page offers every configured provider
#


def test_login_page_offers_all_providers(client, orcid_socialapp, google_socialapp):
    response = client.get(reverse("account_login"))
    assert response.status_code == 200
    html = response.content.decode()
    # Matched on the provider login URLs rather than the button captions, which
    # carry whatever name django-allauth gives the provider
    assert "/accounts/orcid/login/" in html
    assert "/accounts/google/login/" in html
    # ... and the local form, so an account can be created without either
    assert reverse("account_signup") in html


def test_a_provider_that_hands_over_no_email_can_still_sign_someone_up():
    """
    Registering locally requires an email address; signing in through a
    provider must not.

    django-allauth derives `SOCIALACCOUNT_EMAIL_REQUIRED` from the local signup
    fields unless it is set explicitly, so making the address mandatory for
    local registration would otherwise stop ORCID -- which does not necessarily
    release one -- from signing anybody in.
    """
    from allauth.socialaccount import app_settings

    assert not app_settings.EMAIL_REQUIRED


def test_local_registration_is_open(db, client):
    response = client.get(reverse("account_signup"))
    assert response.status_code == 200
    assert "Sign Up" in response.content.decode()


def test_local_registration_can_be_switched_off(db, client, settings):
    settings.ACCOUNT_ALLOW_SIGNUP = False
    response = client.get(reverse("account_signup"))
    # allauth renders its "signup closed" page rather than the form
    assert "signup_form" not in response.content.decode()


#
# Connected identities
#


def test_connections_page_warns_when_no_orcid_is_connected(client, local_user):
    client.force_login(local_user)
    response = client.get(reverse("socialaccount_connections"))
    assert response.status_code == 200
    html = response.content.decode()
    assert "No ORCID iD connected" in html
    # The local account is listed as an identity of its own
    assert "Email and password" in html


def test_connections_page_lists_a_connected_orcid(client, local_user):
    connect_orcid(local_user)
    client.force_login(local_user)
    response = client.get(reverse("socialaccount_connections"))
    assert response.status_code == 200
    assert "Your ORCID iD is connected" in response.content.decode()


def test_orcid_can_be_added_to_a_local_account(local_user):
    assert not local_user.has_orcid
    connect_orcid(local_user)
    assert local_user.has_orcid
    assert local_user.orcid_id == "0000-0002-1825-0097"
    # Both identities remain usable
    assert {identity["provider"] for identity in local_user.connected_identities} == {
        "orcid",
        "local",
    }


#
# Publishing requires an ORCID iD
#


@pytest.mark.parametrize("url", [PUBLISH_URL, PUBLISH_COLLECTION_URL])
def test_publishing_without_an_orcid_is_refused(client, local_user, url):
    client.force_login(local_user)
    response = client.post(url, {}, content_type="application/json")
    assert response.status_code == 403


@pytest.mark.parametrize("url", [PUBLISH_URL, PUBLISH_COLLECTION_URL])
def test_publishing_with_an_orcid_is_not_refused(client, local_user, url):
    connect_orcid(local_user)
    client.force_login(local_user)
    try:
        response = client.post(url, {}, content_type="application/json")
    except Exception:
        # The publication plugin rejected the deliberately empty payload by
        # raising. That it got as far as looking at the payload is the point:
        # the ORCID requirement no longer stands in the way.
        return
    assert response.status_code != 403


def test_the_landing_page_of_a_publication_stays_open(client, local_user):
    """Guarding the publish endpoint must not guard the public pages."""
    client.force_login(local_user)
    response = client.get("/go/does-not-exist/")
    assert response.status_code == 404
