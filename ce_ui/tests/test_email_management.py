"""
Managing the addresses on an account, from the connected identities page.

There is no page of its own for this any more: the addresses sit beside the
providers they arrive with, an address is added through a modal and removed
with a button on its row. `ce_ui.users.views.EmailView` keeps django-allauth's
POST handling behind that, so what is pinned here is the policy and the page,
not allauth's own validation.
"""

import pytest
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.urls import reverse

CONNECTIONS = "socialaccount_connections"


@pytest.fixture
def researcher(db):
    """An ORCID account with one confirmed address."""
    user = get_user_model().objects.create(username="researcher", name="A Researcher")
    user.set_unusable_password()
    user.save()
    SocialAccount.objects.create(user=user, provider="orcid", uid="0000-0002-1825-0097")
    EmailAddress.objects.create(
        user=user, email="work@example.org", verified=True, primary=True
    )
    return user


def connect_google(user, email="researcher@gmail.com", uid="g-1"):
    return SocialAccount.objects.create(
        user=user, provider="google", uid=uid, extra_data={"email": email}
    )


def addresses(user):
    return set(EmailAddress.objects.filter(user=user).values_list("email", flat=True))


#
# The separate page is gone
#


@pytest.mark.django_db
def test_the_email_page_now_lands_on_the_identities_page(client, researcher):
    client.force_login(researcher)
    response = client.get(reverse("account_email"))
    assert response.status_code == 302
    assert response.url == reverse(CONNECTIONS)


@pytest.mark.django_db
def test_the_identities_page_lists_the_addresses_itself(client, researcher):
    EmailAddress.objects.create(
        user=researcher, email="second@example.org", verified=False
    )
    client.force_login(researcher)
    html = client.get(reverse(CONNECTIONS)).content.decode()
    assert "work@example.org" in html
    assert "second@example.org" in html
    # ... and offers the modal rather than a link to somewhere else
    assert 'id="add-email"' in html
    assert "action_add" in html


#
# Adding
#


@pytest.mark.django_db
def test_an_address_can_be_added(client, researcher):
    client.force_login(researcher)
    response = client.post(
        reverse("account_email"),
        {"email": "new@example.org", "action_add": ""},
        follow=True,
    )
    assert response.status_code == 200
    assert "new@example.org" in addresses(researcher)
    # It arrives unconfirmed; the confirmation mail is what verifies it
    assert not EmailAddress.objects.get(email="new@example.org").verified


@pytest.mark.django_db
def test_a_rejected_address_is_reported_on_the_page(client, researcher):
    """
    The add form has no page of its own to re-render, so allauth's validation
    errors are carried over as messages instead of being swallowed.
    """
    client.force_login(researcher)
    response = client.post(
        reverse("account_email"),
        {"email": "work@example.org", "action_add": ""},  # already on the account
        follow=True,
    )
    assert response.redirect_chain[-1][0] == reverse(CONNECTIONS)
    assert addresses(researcher) == {"work@example.org"}
    assert [str(m) for m in response.context["messages"]]


#
# Removing
#


@pytest.mark.django_db
def test_a_spare_address_can_be_removed(client, researcher):
    EmailAddress.objects.create(
        user=researcher, email="old@example.org", verified=True, primary=False
    )
    client.force_login(researcher)
    html = client.get(reverse(CONNECTIONS)).content.decode()
    assert "action_remove" in html

    client.post(
        reverse("account_email"),
        {"email": "old@example.org", "action_remove": ""},
        follow=True,
    )
    assert addresses(researcher) == {"work@example.org"}


@pytest.mark.django_db
def test_an_address_a_connected_provider_vouches_for_is_kept(client, researcher):
    """
    The heart of it: a Google sign-in finds this account by address, so letting
    the address go while Google is connected would quietly break a way in that
    the page above still lists as working.
    """
    connect_google(researcher, email="researcher@gmail.com")
    EmailAddress.objects.create(
        user=researcher, email="researcher@gmail.com", verified=True, primary=False
    )
    client.force_login(researcher)

    client.post(
        reverse("account_email"),
        {"email": "researcher@gmail.com", "action_remove": ""},
        follow=True,
    )
    assert "researcher@gmail.com" in addresses(researcher)


@pytest.mark.django_db
def test_the_page_offers_no_remove_button_for_such_an_address(client, researcher):
    connect_google(researcher, email="researcher@gmail.com")
    EmailAddress.objects.create(
        user=researcher, email="researcher@gmail.com", verified=True, primary=False
    )
    client.force_login(researcher)
    html = client.get(reverse(CONNECTIONS)).content.decode()
    # It is named as the provider's rather than offered for removal
    assert "from Google" in html


@pytest.mark.django_db
def test_disconnecting_the_provider_releases_its_address(client, researcher):
    """The rule is about the connection, so it lifts when the account goes."""
    google = connect_google(researcher, email="researcher@gmail.com")
    EmailAddress.objects.create(
        user=researcher, email="researcher@gmail.com", verified=True, primary=False
    )
    google.delete()
    client.force_login(researcher)

    client.post(
        reverse("account_email"),
        {"email": "researcher@gmail.com", "action_remove": ""},
        follow=True,
    )
    assert addresses(researcher) == {"work@example.org"}


@pytest.mark.django_db
def test_the_primary_address_is_kept_while_another_one_exists(client, researcher):
    """
    django-allauth's own rule, which the page has to keep working with: the
    primary address goes only once another one has taken its place, which is
    what the "Make primary" action on the other rows is for.
    """
    EmailAddress.objects.create(
        user=researcher, email="other@example.org", verified=True, primary=False
    )
    client.force_login(researcher)

    client.post(
        reverse("account_email"),
        {"email": "work@example.org", "action_remove": ""},
        follow=True,
    )
    assert "work@example.org" in addresses(researcher)

    # Hand primary over, and it can go
    client.post(
        reverse("account_email"),
        {"email": "other@example.org", "action_primary": ""},
        follow=True,
    )
    client.post(
        reverse("account_email"),
        {"email": "work@example.org", "action_remove": ""},
        follow=True,
    )
    assert addresses(researcher) == {"other@example.org"}


#
# The password is a section of its own, with its own warning
#


@pytest.mark.django_db
def test_the_password_section_warns_about_going_around_the_providers(
    client, researcher
):
    """
    A password is a way in that the providers never see, so whatever second
    factor they enforce does not cover it. Somebody setting one should be told.
    """
    client.force_login(researcher)
    html = client.get(reverse(CONNECTIONS)).content.decode()
    assert "Password authentication" in html
    assert "goes around your providers" in html


@pytest.mark.django_db
def test_setting_a_password_is_offered_outside_the_connect_section(
    client, researcher, orcid_socialapp, google_socialapp
):
    """
    It is not a provider, so it no longer sits among the connect buttons.
    """
    client.force_login(researcher)
    html = client.get(reverse(CONNECTIONS)).content.decode()
    connect_section = html.split("Add another way to sign in")[1].split(
        "Email addresses"
    )[0]
    assert "Set a password" not in connect_section
    assert reverse("account_set_password") in html


@pytest.mark.django_db
def test_the_connect_section_is_hidden_once_every_provider_is_connected(
    client, researcher, orcid_socialapp, google_socialapp
):
    client.force_login(researcher)
    assert "Add another way to sign in" in client.get(
        reverse(CONNECTIONS)
    ).content.decode()

    connect_google(researcher)
    html = client.get(reverse(CONNECTIONS)).content.decode()
    assert "Add another way to sign in" not in html
    # ... while the password section stays, being nobody's provider
    assert "Password authentication" in html


#
# Removing the password
#


@pytest.mark.django_db
def test_the_password_can_be_removed(client, researcher, mailoutbox):
    researcher.set_password("a-very-secret-password")
    researcher.save()
    client.force_login(researcher)

    html = client.get(reverse(CONNECTIONS)).content.decode()
    assert reverse("account_remove_password") in html

    client.post(reverse("account_remove_password"), follow=True)
    researcher.refresh_from_db()
    assert not researcher.has_usable_password()
    # The ORCID account still signs them in
    assert researcher.socialaccount_set.exists()


@pytest.mark.django_db
def test_removing_the_password_is_announced(client, researcher, mailoutbox):
    """Losing a way in is exactly what the notification mails exist for."""
    researcher.set_password("a-very-secret-password")
    researcher.save()
    client.force_login(researcher)
    mailoutbox.clear()

    client.post(reverse("account_remove_password"), follow=True)
    assert len(mailoutbox) == 1
    assert "password was removed" in mailoutbox[0].subject


@pytest.mark.django_db
def test_the_last_way_in_cannot_be_removed(client, db):
    """
    An account with a password and no provider would be locked out for good.
    """
    user = get_user_model().objects.create(username="local", name="Local")
    user.set_password("a-very-secret-password")
    user.save()
    EmailAddress.objects.create(
        user=user, email="local@example.org", verified=True, primary=True
    )
    assert not user.can_remove_password

    client.force_login(user)
    html = client.get(reverse(CONNECTIONS)).content.decode()
    assert reverse("account_remove_password") not in html

    client.post(reverse("account_remove_password"), follow=True)
    user.refresh_from_db()
    assert user.has_usable_password()


@pytest.mark.django_db
def test_removing_a_password_needs_a_post(client, researcher):
    """It changes a credential, so a followed link must not do it."""
    researcher.set_password("a-very-secret-password")
    researcher.save()
    client.force_login(researcher)

    response = client.get(reverse("account_remove_password"))
    assert response.status_code == 405
    researcher.refresh_from_db()
    assert researcher.has_usable_password()
