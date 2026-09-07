"""
One way in always remains.

Three things can take a way of signing in away -- disconnecting a provider,
removing the password, removing an email address -- and each is guarded
separately, in a different place, by a different rule. What matters is the
invariant they add up to, so it is checked here against the states an account
can be in rather than rule by rule: build an account, try every removal it
offers, and assert that something is still able to sign in afterwards.

`can_sign_in` below is deliberately written from what the *login* accepts
rather than from the guards, so that a guard drifting away from the rule it
protects shows up as a failure here.
"""

import pytest
from allauth.account import app_settings as account_settings
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.urls import reverse


def can_sign_in(user):
    """Whether any route into this account still works."""
    if SocialAccount.objects.filter(user=user).exists():
        return True
    if not user.has_usable_password():
        return False
    if (
        account_settings.EMAIL_VERIFICATION
        == account_settings.EmailVerificationMethod.MANDATORY
    ):
        # allauth refuses the login and sends a confirmation instead
        return EmailAddress.objects.filter(user=user, verified=True).exists()
    return True


def build(providers, password, emails):
    User = get_user_model()
    User.objects.filter(username="subject").delete()
    user = User.objects.create(username="subject", name="Subject")
    if password:
        user.set_password("a-very-secret-password")
    else:
        user.set_unusable_password()
    user.save()
    for provider in providers:
        SocialAccount.objects.create(
            user=user, provider=provider, uid=f"uid-{provider}", extra_data={}
        )
    for position, (address, verified) in enumerate(emails):
        EmailAddress.objects.create(
            user=user, email=address, verified=verified, primary=(position == 0)
        )
    return user


PROVIDERS = [(), ("orcid",), ("orcid", "google")]
EMAILS = [
    (),
    (("a@example.org", True),),
    (("a@example.org", False),),
    (("a@example.org", True), ("b@example.org", True)),
]


@pytest.mark.django_db
@pytest.mark.parametrize("providers", PROVIDERS, ids=lambda p: "+".join(p) or "none")
@pytest.mark.parametrize("password", [True, False], ids=["password", "nopassword"])
@pytest.mark.parametrize("emails", EMAILS, ids=lambda e: f"{len(e)}mail")
def test_no_removal_can_lock_the_account_out(
    client, settings, orcid_socialapp, google_socialapp, providers, password, emails
):
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    if not can_sign_in(build(providers, password, emails)):
        pytest.skip("this state has no way in to begin with")

    removals = (
        [("disconnect", provider) for provider in providers]
        + ([("password", None)] if password else [])
        + [("address", address) for address, _ in emails]
    )

    for kind, target in removals:
        # A fresh account each time: the question is whether any *one* removal
        # can strand it, not what a particular order happens to leave behind.
        user = build(providers, password, emails)
        client.force_login(user)

        if kind == "disconnect":
            account = SocialAccount.objects.get(user=user, provider=target)
            client.post(
                reverse("socialaccount_connections"),
                {"account": account.pk},
                follow=True,
            )
        elif kind == "password":
            client.post(reverse("account_remove_password"), follow=True)
        else:
            client.post(
                reverse("account_email"),
                {"email": target, "action_remove": ""},
                follow=True,
            )

        user.refresh_from_db()
        assert can_sign_in(user), (
            f"removing {kind} {target!r} left no way in "
            f"(providers={providers}, password={password}, emails={emails})"
        )


@pytest.mark.django_db
def test_the_last_address_of_a_password_only_account_stays(client, settings):
    """
    The case the probe above found, pinned on its own.

    django-allauth guards the last address only when email is the sole login
    method; this site also accepts a username, so its guard never fires. An
    account with a password and no provider would be left unable to sign in
    (mandatory verification needs a confirmed address) and unable to recover
    (no address for the reset to reach).
    """
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    user = build((), password=True, emails=(("only@example.org", True),))
    client.force_login(user)

    html = client.get(reverse("socialaccount_connections")).content.decode()
    assert "action_remove" not in html  # not even offered

    client.post(
        reverse("account_email"),
        {"email": "only@example.org", "action_remove": ""},
        follow=True,
    )
    assert EmailAddress.objects.filter(user=user).exists()

    # Connect a provider and the address is released: it is no longer the only
    # thing standing between the account and its owner.
    SocialAccount.objects.create(user=user, provider="orcid", uid="u", extra_data={})
    client.post(
        reverse("account_email"),
        {"email": "only@example.org", "action_remove": ""},
        follow=True,
    )
    assert not EmailAddress.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_no_sequence_of_removals_can_strand_an_account(
    client, settings, orcid_socialapp, google_socialapp
):
    """
    Salami test: keep removing until nothing more can be removed.

    Each guard reads the account as it stands, so a single safe step implies a
    safe sequence -- but only if that is actually how they are written. This
    walks an account all the way down and checks the invariant at every step,
    so a guard that looks at a stale or partial picture is caught.
    """
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    user = build(
        ("orcid", "google"),
        password=True,
        emails=(("a@example.org", True), ("b@example.org", True)),
    )
    client.force_login(user)

    def attempt_all():
        """Try every removal once; report whether anything actually went."""
        changed = False
        for account in list(SocialAccount.objects.filter(user=user)):
            before = SocialAccount.objects.filter(user=user).count()
            client.post(
                reverse("socialaccount_connections"),
                {"account": account.pk},
                follow=True,
            )
            changed |= SocialAccount.objects.filter(user=user).count() < before
            user.refresh_from_db()
            assert can_sign_in(user), "disconnect left no way in"

        if user.has_usable_password():
            client.post(reverse("account_remove_password"), follow=True)
            user.refresh_from_db()
            changed |= not user.has_usable_password()
            assert can_sign_in(user), "removing the password left no way in"

        for address in list(EmailAddress.objects.filter(user=user)):
            before = EmailAddress.objects.filter(user=user).count()
            client.post(
                reverse("account_email"),
                {"email": address.email, "action_remove": ""},
                follow=True,
            )
            changed |= EmailAddress.objects.filter(user=user).count() < before
            user.refresh_from_db()
            assert can_sign_in(user), f"removing {address.email} left no way in"
        return changed

    for _ in range(10):
        if not attempt_all():
            break
    else:
        pytest.fail("removals never settled; the walk is not converging")

    # Whatever survived, it is still enough to get in.
    assert can_sign_in(user)
