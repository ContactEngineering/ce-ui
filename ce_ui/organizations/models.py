import logging
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.urls import resolve
from django.utils.translation import gettext_lazy as _

_log = logging.getLogger(__name__)

DEFAULT_ORGANIZATION_NAME = "World"
DEFAULT_GROUP_NAME = "all"


class OrganizationManager(models.Manager):
    def for_user(self, user: settings.AUTH_USER_MODEL) -> models.QuerySet:
        """Return queryset with all organizations the given user belongs to."""
        return self.filter(group__in=user.groups.all())


class Organization(models.Model):
    """Represents an organization like a company or a scientific workgroup in a university."""

    name = models.CharField(_("Name of Organization"), max_length=255, unique=True)
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        help_text="Group which corresponds to members of this organization.",
    )

    objects = OrganizationManager()

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if self.pk is None:
            group_name = self.name
            if group_name == DEFAULT_ORGANIZATION_NAME:
                group_name = DEFAULT_GROUP_NAME

            group, group_created = Group.objects.get_or_create(name=group_name)
            if group_created:
                _log.info(
                    f"Created group '{group_name}' for being associated with "
                    f"organization '{self.name}'."
                )
            self.group = group

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

        _log.info(
            f"Deleting group '{self.group.name}' because of deletion of "
            f"organization '{self.name}'."
        )
        self.group.delete()

    def add(self, user: settings.AUTH_USER_MODEL):
        """Add user to this organization."""
        user.groups.add(self.group)

    @classmethod
    def resolve(cls, url):
        """Resolve an organization from a URL or integer ID."""
        try:
            pk = int(url)
            return cls.objects.get(pk=pk)
        except ValueError:
            match = resolve(urlparse(url).path)
            if match.view_name != "organizations:organization-v1-detail":
                raise ValueError("URL does not resolve to an Organization instance")
            return cls.objects.get(**match.kwargs)


def resolve_organization(url):
    """Resolve organization from URL or ID. Prefer Organization.resolve(url)."""
    return Organization.resolve(url)
