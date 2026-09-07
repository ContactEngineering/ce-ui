"""Views for the addresses and the password on an account."""

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.views import EmailView as AllauthEmailView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import View

from .identity import can_remove_password


class EmailView(AllauthEmailView):
    """
    django-allauth's email management, without a page of its own.

    Addresses are managed from the connected identities page, which already
    lists them next to the providers they arrive with and explains what a
    confirmed address is for; a second page listing the same addresses only
    split the subject in two. So this keeps allauth's POST handling -- the
    validation, the confirmation mail, the notification mails, the signals and
    the `can_delete_email` rules all come with it -- and sends every outcome
    back to that page.

    The form posts here rather than to a view of our own precisely so none of
    that has to be reimplemented; `action_add`, `action_remove`, `action_send`
    and `action_primary` are allauth's own field names.
    """

    success_url = reverse_lazy("socialaccount_connections")

    def get(self, request, *args, **kwargs):
        """No page to show: everything it would list is on the target page."""
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return str(self.success_url)

    def form_invalid(self, form):
        """
        Report a rejected address on the page the form was submitted from.

        The base class re-renders its own template with the bound form, which
        no longer exists here, so the errors are carried over as messages
        instead -- "this address is already on your account" and the like,
        which is the whole of what that template would have shown.
        """
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return HttpResponseRedirect(self.get_success_url())


class RemovePasswordView(LoginRequiredMixin, View):
    """
    Take the password off an account, leaving the connected providers.

    django-allauth can set and change a password but not remove one, so this
    fills the gap. It is the counterpart to disconnecting a provider: both take
    away a way in, and both are refused when they would take away the last one.

    POST only -- it changes a credential, so it must not sit behind a link that
    something can follow.
    """

    def post(self, request, *args, **kwargs):
        user = request.user
        redirect_to = HttpResponseRedirect(reverse("socialaccount_connections"))

        if not user.has_usable_password():
            return redirect_to

        if not can_remove_password(user):
            messages.error(
                request,
                _(
                    "Your password is the only way you can sign in. Connect an "
                    "identity provider before removing it."
                ),
            )
            return redirect_to

        user.set_unusable_password()
        user.save(update_fields=["password"])

        # Losing a way in is exactly the event somebody should hear about, the
        # same as setting or changing the password; see ACCOUNT_EMAIL_NOTIFICATIONS.
        get_account_adapter(request).send_notification_mail(
            "account/email/password_removed", user
        )
        messages.success(
            request,
            _(
                "Your password was removed. You can still sign in with your "
                "connected accounts, and you can set a new password at any time."
            ),
        )
        return redirect_to
