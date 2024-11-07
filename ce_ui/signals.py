import logging

from allauth.account.signals import user_logged_in
from django.dispatch import receiver

from .views import DEFAULT_SELECT_TAB_STATE

_log = logging.getLogger(__name__)


@receiver(user_logged_in)
def set_default_select_tab_state(request, user, **kwargs):
    """At each login, the state of the select tab should be reset.
    """
    request.session['select_tab_state'] = DEFAULT_SELECT_TAB_STATE
