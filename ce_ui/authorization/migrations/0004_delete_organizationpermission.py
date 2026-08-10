from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0003_add_permission_performance_indexes'),
    ]

    operations = [
        migrations.DeleteModel(
            name='OrganizationPermission',
        ),
    ]
