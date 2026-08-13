from django.apps import AppConfig


def _create_anonymous_user(sender, **kwargs):
    """Create the anonymous user after migrations if it doesn't exist."""
    from django.contrib.auth import get_user_model

    from .anonymous import ANONYMOUS_USER_NAME

    User = get_user_model()
    User.objects.get_or_create(**{User.USERNAME_FIELD: ANONYMOUS_USER_NAME})


class UsersAppConfig(AppConfig):
    name = "ce_ui.users"
    label = "users"

    def ready(self):
        from django.db.models.signals import post_migrate

        # Registers the receivers that keep email addresses in step with the
        # identity providers connected to an account
        from . import signals  # noqa: F401

        post_migrate.connect(_create_anonymous_user, sender=self)
