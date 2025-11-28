from django.contrib.auth.models import Group

DEFAULT_GROUP_NAME = "all"


def get_default_group():
    group, created = Group.objects.get_or_create(name=DEFAULT_GROUP_NAME)
    return group
