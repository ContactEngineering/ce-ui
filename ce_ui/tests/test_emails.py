"""
The mails the site sends.

django-allauth sends `*_message.txt` as the body and attaches `*_message.html`
as an alternative, so a missing HTML template degrades silently to a plain
default-looking mail. These tests pin that both halves are rendered, that they
carry the link the mail exists for, and that nothing in them is left as an
unrendered placeholder.
"""

import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.urls import reverse


@pytest.fixture(autouse=True)
def _no_carried_over_rate_limits():
    """
    django-allauth refuses to re-send a confirmation for the same address
    within a cooldown, and records that in the cache -- which, unlike the
    database, is not rolled back between tests. Without this, a second test
    asking for the same mail silently gets none.
    """
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def user(db):
    user = get_user_model().objects.create(
        username="researcher", name="A Researcher", email="researcher@example.org"
    )
    user.set_password("a-very-secret-password")
    user.save()
    return user


def _sent():
    assert len(mail.outbox) == 1, f"expected one mail, got {len(mail.outbox)}"
    message = mail.outbox[0]
    html = dict(
        (content_type, body)
        for body, content_type in message.alternatives
    ).get("text/html")
    return message, message.body, html


def _assert_well_formed(subject, text, html):
    assert subject.startswith("[contact.engineering] ")
    # Both halves present, and the HTML one is actually a document
    assert html is not None, "no HTML alternative was attached"
    assert html.lstrip().startswith("<!doctype html>")
    assert "contact.engineering" in text
    assert "contact.engineering" in html
    # A template that failed to resolve a variable leaves the string empty, and
    # a block left unfilled leaves the heading blank
    for body in (text, html):
        assert "{{" not in body and "{%" not in body
    assert "None" not in text
    # A variable that is not in the context renders as nothing at all, which no
    # exception reports and no eye catches in a template. It shows up in the
    # output as a gap mid-line, or one in front of punctuation. Leading
    # whitespace is left out of it, being deliberate indentation.
    for line in text.splitlines():
        assert "  " not in line.lstrip(), f"gap left by an empty variable: {line!r}"
    assert " ." not in text and " ," not in text


@pytest.mark.django_db
def test_email_confirmation(client, user, settings):
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    client.force_login(user)
    mail.outbox = []
    client.post(
        reverse("account_email"),
        {"email": "second@example.org", "action_add": ""},
        follow=True,
    )

    message, text, html = _sent()
    _assert_well_formed(message.subject, text, html)
    assert "Confirm your email address" in message.subject
    assert "second@example.org" in text and "second@example.org" in html
    # The link the mail exists for, in both halves
    assert "/accounts/confirm-email/" in text
    assert "/accounts/confirm-email/" in html


@pytest.mark.django_db
def test_password_reset(client, user):
    EmailAddress.objects.create(
        user=user, email="researcher@example.org", verified=True, primary=True
    )
    mail.outbox = []
    client.post(
        reverse("account_reset_password"),
        {"email": "researcher@example.org"},
        follow=True,
    )

    message, text, html = _sent()
    _assert_well_formed(message.subject, text, html)
    assert "Reset your password" in message.subject
    assert "/accounts/password/reset/key/" in text
    assert "/accounts/password/reset/key/" in html
    # Says the account is still reachable another way
    assert "ORCID" in text and "ORCID" in html


@pytest.mark.django_db
def test_password_reset_for_an_address_we_do_not_know(client, db):
    """
    Sent instead of silence, so the address is not a way to probe who has an
    account here. It has to explain how accounts are made, since the reader
    cannot simply register.
    """
    mail.outbox = []
    client.post(
        reverse("account_reset_password"),
        {"email": "stranger@example.org"},
        follow=True,
    )

    message, text, html = _sent()
    _assert_well_formed(message.subject, text, html)
    assert "No account at this address" in message.subject
    assert "stranger@example.org" in text
    assert "ORCID" in text and "ORCID" in html


@pytest.mark.django_db
def test_the_html_half_carries_no_remote_content(client, user, settings):
    """
    Mail clients block remote images by default, so a mail that leans on one
    arrives with a hole in it. Everything here is type and table cells.
    """
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    client.force_login(user)
    mail.outbox = []
    client.post(
        reverse("account_email"),
        {"email": "second@example.org", "action_add": ""},
        follow=True,
    )

    _, _, html = _sent()
    assert "<img" not in html
    assert "<link" not in html  # no external stylesheet
    assert "<script" not in html
