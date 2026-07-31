import logging

from django.core.management import call_command
from topobank.taskapp.celeryapp import app

_log = logging.getLogger(__name__)


@app.task
def truncate_request_profiler_logs():
    """
    Delete profiler records older than REQUEST_PROFILER_LOG_TRUNCATION_DAYS.

    Celery beat cannot invoke a management command directly, so this wraps the
    one shipped by `request_profiler`. Note that the command only reports what it
    would delete unless `--commit` is passed, hence passing it explicitly here.
    """
    _log.info("Truncating request profiler logs.")
    call_command("truncate_request_profiler_logs", "--commit")
