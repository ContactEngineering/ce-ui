"""
Keeping email addresses in step with the identities connected to an account.

django-allauth stores the addresses a provider hands over when it *creates* an
account, but not when one is connected to an account that already exists -- see
the ``if connect: pass`` branch of ``SocialLogin.save``, where it is left as an
open question. For this site the answer is yes: an address is how a Google
sign-in finds its account, how a password sign-in is permitted at all, and how
an account is recovered, so an address the provider has already verified should
land rather than be dropped on the floor.
"""

import logging

from allauth.account.models import EmailAddress
from allauth.socialaccount.signals import social_account_added
from django.dispatch import receiver

_log = logging.getLogger(__name__)


@receiver(social_account_added)
def store_verified_provider_addresses(request, sociallogin, **kwargs):
    """
    Record the addresses a newly connected provider has verified itself.

    Only verified ones: an address the provider has not confirmed is a claim,
    not evidence; confirming it is what the connected identities page is for.

    An address held by *another* account is left alone -- addresses are unique
    across accounts (`ACCOUNT_UNIQUE_EMAIL`), and taking one would hand over
    its sign-in. One this user already holds unconfirmed is confirmed instead
    of skipped: the provider has just vouched for it, which is exactly the
    evidence the confirmation mail would have produced, and leaving it
    unconfirmed would keep the account without a way back in.
    """
    user = getattr(sociallogin, "user", None)
    if user is None or not getattr(user, "pk", None):
        return

    has_address = EmailAddress.objects.filter(user=user).exists()

    for address in sociallogin.email_addresses:
        if not address.verified:
            continue

        existing = EmailAddress.objects.filter(email__iexact=address.email).first()
        if existing is not None:
            if existing.user_id != user.pk or existing.verified:
                continue
            # Ours, and the provider has just vouched for it.
            existing.verified = True
            existing.save(update_fields=["verified"])
            stored = existing
        else:
            stored = EmailAddress.objects.create(
                user=user, email=address.email, verified=True
            )

        if not has_address:
            # The account had none, so this one becomes the address it is
            # reached at; `set_as_primary` keeps `User.email` in step.
            stored.set_as_primary()
            has_address = True

        _log.info(
            "Stored the verified address of the %s account connected to user %s.",
            sociallogin.account.provider,
            user.pk,
        )
