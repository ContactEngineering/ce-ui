import logging

from django.apps import apps as global_apps
from django.conf import settings
from django.contrib.auth.models import Group
from django.db.models import Q
from watchman.decorators import check as watchman_check

_log = logging.getLogger(__name__)

DEFAULT_GROUP_NAME = "all"


def get_default_group():
    group, created = Group.objects.get_or_create(name=DEFAULT_GROUP_NAME)
    return group


def celery_worker_check():
    return {
        "celery": _celery_worker_check(),
    }


@watchman_check
def _celery_worker_check():
    """Used with watchman in order to check whether celery workers are available."""
    # See https://github.com/mwarkentin/django-watchman/issues/8
    from topobank.taskapp.celeryapp import app

    MIN_NUM_WORKERS_EXPECTED = 1
    d = app.control.broadcast(
        "ping", reply=True, timeout=0.1, limit=MIN_NUM_WORKERS_EXPECTED
    )
    return {
        "num_workers_available": len(d),
        "min_num_workers_expected": MIN_NUM_WORKERS_EXPECTED,
        "ok": len(d) >= MIN_NUM_WORKERS_EXPECTED,
    }


def delete_notifications_of_removed_models(apps=global_apps, using="default") -> int:
    """
    Delete notifications whose actor, target or action object is of a model
    that no longer exists, and return how many were deleted.

    Deleting a model leaves its content type and the notifications referring
    to it behind. django-notifications resolves these relations when it lists
    notifications and crashes on a content type without a model class.

    Which models exist is decided by the code that is running, not by `apps`,
    which in a migration is the historical state: models of apps whose
    migrations have not been applied yet would look removed there.
    """
    ContentType = apps.get_model("contenttypes", "ContentType")
    Notification = apps.get_model(
        *getattr(
            settings, "NOTIFICATIONS_NOTIFICATION_MODEL", "notifications.Notification"
        ).split(".")
    )

    removed = []
    for content_type in ContentType.objects.using(using).all():
        try:
            global_apps.get_model(content_type.app_label, content_type.model)
        except LookupError:
            removed.append(content_type.pk)
    if not removed:
        return 0

    nb_deleted, _ = (
        Notification.objects.using(using)
        .filter(
            Q(actor_content_type__in=removed)
            | Q(target_content_type__in=removed)
            | Q(action_object_content_type__in=removed)
        )
        .delete()
    )
    if nb_deleted:
        _log.info(f"Deleted {nb_deleted} notification(s) referring to removed models.")
    return nb_deleted
