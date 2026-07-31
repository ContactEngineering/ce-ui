from django.db import migrations

# `request_profiler` is a third-party app, so its ProfilingRecord model cannot
# declare this index itself. Its `truncate_request_profiler_logs` command filters
# on `start_ts__date__lt`, which Django compiles to a cast over the column:
#
#     (start_ts AT TIME ZONE 'Europe/Berlin')::date < <cutoff>
#
# A plain btree index on start_ts cannot serve that predicate, so we index the
# expression verbatim. The time zone literal must stay in sync with
# settings.TIME_ZONE -- Django interpolates that setting into the SQL, and the
# planner only matches an expression index when the expressions are identical.
INDEX_NAME = "request_profiler_profilingrecord_start_ts_date_idx"
TIME_ZONE = "Europe/Berlin"

CREATE_INDEX = f"""
CREATE INDEX CONCURRENTLY IF NOT EXISTS {INDEX_NAME}
ON request_profiler_profilingrecord
(((start_ts AT TIME ZONE '{TIME_ZONE}')::date));
"""

DROP_INDEX = f"DROP INDEX CONCURRENTLY IF EXISTS {INDEX_NAME};"


class Migration(migrations.Migration):
    # CREATE/DROP INDEX CONCURRENTLY cannot run inside a transaction block. The
    # profiler inserts a row per profiled request, so a non-concurrent build
    # would hold ACCESS EXCLUSIVE on a table that is ~1 GB in production and
    # stall every profiled request for the duration.
    atomic = False

    dependencies = [
        ("request_profiler", "0005_alter_profilingrecord_id_alter_ruleset_id"),
    ]

    operations = [
        # No state_operations: this is a database-only index on a model owned by
        # another app, so Django's migration state must stay untouched to avoid
        # makemigrations detecting phantom changes.
        migrations.RunSQL(sql=CREATE_INDEX, reverse_sql=DROP_INDEX),
    ]
