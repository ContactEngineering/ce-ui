from django.db import migrations

from ce_ui.utils import delete_notifications_of_removed_models


def delete_notifications(apps, schema_editor):
    # Notifications sent by the AnalysisCollection model, removed in topobank's
    # analysis migration 0029, made the notification list crash for the users
    # who still had them (see delete_notifications_of_removed_models).
    using = schema_editor.connection.alias if schema_editor else "default"
    delete_notifications_of_removed_models(apps, using=using)


class Migration(migrations.Migration):
    dependencies = [
        ("ce_ui", "0001_profilingrecord_start_ts_date_idx"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("notifications", "0010_rename_notification_recipient_unread_notificatio_recipie_8bedf2_idx"),
    ]

    operations = [
        migrations.RunPython(delete_notifications, migrations.RunPython.noop),
    ]
