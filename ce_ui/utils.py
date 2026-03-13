from django.contrib.auth.models import Group

DEFAULT_GROUP_NAME = "all"


def get_default_group():
    group, created = Group.objects.get_or_create(name=DEFAULT_GROUP_NAME)
    return group

import logging
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.exceptions import SuspiciousFileOperation
from django.urls import reverse

_log = logging.getLogger(__name__)



from watchman.decorators import check as watchman_check

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
