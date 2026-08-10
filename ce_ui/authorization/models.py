"""
Concrete permission implementation for this site.

This module provides PermissionSet backed by User permission rows. It fills
topobank's `TOPOBANK_PERMISSION_MODEL` seam; `topobank.testing.mock_auth` is
the other implementation of it.
"""
import logging

from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import Q, QuerySet
from django.http import Http404 as NotFound
from notifications.signals import notify
from topobank.authorization import get_anonymous_user
from topobank.authorization.models import (ACCESS_LEVELS, PERMISSION_CHOICES,
                                           AbstractPermissionSet, ViewEditFull,
                                           ViewEditFullNone,
                                           levels_with_access)

_log = logging.getLogger(__name__)


def _filter_for_user(
    queryset: QuerySet,
    user,
    permission: ViewEditFull,
    prefix: str = ""
) -> QuerySet:
    """
    Shared implementation for filtering querysets by user permission.

    Args:
        queryset: The queryset to filter
        user: The user to check permissions for
        permission: The permission level to check
        prefix: Field prefix for permission lookups (e.g., "permissions__" or "")

    Note: This implementation uses UNION queries to optimize performance.
    """
    # Build field names with prefix
    user_perm_user = f"{prefix}user_permissions__user"
    user_perm_allow = f"{prefix}user_permissions__allow__in"

    if permission == "view":
        qs_user = queryset.filter(**{user_perm_user: user})
        union_parts = [qs_user]

        anonymous_user = get_anonymous_user()
        if anonymous_user is not None:
            union_parts.append(
                queryset.filter(**{user_perm_user: anonymous_user})
            )

        if len(union_parts) == 1:
            return union_parts[0]

        union_qs = union_parts[0].union(*union_parts[1:])
        accessible_ids = list(union_qs.values_list('id', flat=True))
        return queryset.filter(id__in=accessible_ids)
    else:
        allowed_levels = levels_with_access(permission)

        return queryset.filter(
            **{user_perm_user: user, user_perm_allow: allowed_levels}
        )


class PermissionSetManager(models.Manager):
    def create(self, user=None, allow: ViewEditFullNone = None, **kwargs):
        if user is not None or allow is not None:
            if user is None or allow is None:
                raise RuntimeError(
                    "You need to provide both user and permission when creating a "
                    "PermissionSet."
                )
            permission_set = super().create(**kwargs)
            permission_set.grant_for_user(user, allow)
            return permission_set
        else:
            return super().create(**kwargs)

    def for_user(self, user, permission: ViewEditFull = "view") -> QuerySet:
        """Return all PermissionSets where user has at least the given permission level"""
        return _filter_for_user(self.get_queryset(), user, permission, prefix="")


class PermissionSet(AbstractPermissionSet):
    """Concrete permission set backed by User permission rows."""

    objects = PermissionSetManager()

    @classmethod
    def filter_queryset(cls, queryset, user, permission):
        """Filter domain-object queryset to items accessible to user."""
        return _filter_for_user(queryset, user, permission, prefix="permissions__")

    def get_for_user(self, user):
        """Return permissions of a specific user.

        Falls back to the anonymous user's permission when one is
        configured — authenticated users inherit anonymous view access.
        """
        anonymous_user = get_anonymous_user()

        # Separately hold the target user's own permission row (at most one,
        # enforced by unique_together) and the anonymous user's row. The
        # anonymous row is expected and must not trigger the >1 guard below.
        if 'user_permissions' in getattr(self, '_prefetched_objects_cache', {}):
            own_permissions = [
                p for p in self.user_permissions.all() if p.user == user
            ]
            anonymous_permissions = [
                p for p in self.user_permissions.all()
                if anonymous_user is not None
                and p.user == anonymous_user
                and p.user != user
            ]
        else:
            own_permissions = list(self.user_permissions.filter(user=user))
            if anonymous_user is None or anonymous_user == user:
                anonymous_permissions = []
            else:
                anonymous_permissions = list(
                    self.user_permissions.filter(user=anonymous_user)
                )

        nb_user_permissions = len(own_permissions)

        # Only the target user's own rows are constrained to be unique; the
        # anonymous row is a legitimate additional row and is excluded here.
        if nb_user_permissions > 1:
            raise RuntimeError(
                f"More than one user permission found for user {user}. "
                "This should not happen."
            )

        max_access_level = 0
        if nb_user_permissions > 0:
            # The user's own row keeps its full permission level.
            max_access_level = max(
                max_access_level,
                max(ACCESS_LEVELS[perm.allow] for perm in own_permissions),
            )
        if len(anonymous_permissions) > 0:
            # Authenticated users inherit anonymous access, but the anonymous
            # row can never grant more than "view" (consistent with
            # _filter_for_user, which excludes anonymous rows for non-view
            # permissions).
            anonymous_access_level = max(
                ACCESS_LEVELS[perm.allow] for perm in anonymous_permissions
            )
            anonymous_access_level = min(
                anonymous_access_level, ACCESS_LEVELS["view"]
            )
            max_access_level = max(max_access_level, anonymous_access_level)
        if max_access_level == 0:
            return None
        else:
            return PERMISSION_CHOICES[max_access_level - 1][0]

    def grant_for_user(self, user, allow: ViewEditFull):
        """Grant permission to user"""
        UserPermission.objects.update_or_create(
            parent=self, user=user,
            defaults={"allow": allow},
        )

    def revoke_from_user(self, user):
        """Revoke all permissions from user"""
        self.user_permissions.filter(user=user).delete()

    def grant(self, principal, allow: ViewEditFull):
        """Grant permission to a user"""
        return self.grant_for_user(principal, allow)

    def revoke(self, principal):
        """Revoke permission from a user"""
        return self.revoke_from_user(principal)

    def user_has_permission(self, user, access_level: ViewEditFull) -> bool:
        """Check if user has permission for access level given by `allow`"""
        perm = self.get_for_user(user)
        if perm:
            return ACCESS_LEVELS[perm] >= ACCESS_LEVELS[access_level]
        else:
            return False

    def authorize_user(self, user, access_level: ViewEditFull):
        """Authorize user; raise PermissionDenied or NotFound if insufficient."""
        perm = self.get_for_user(user)
        if perm is None:
            raise NotFound()
        elif ACCESS_LEVELS[perm] < ACCESS_LEVELS[access_level]:
            raise PermissionDenied(
                f"User '{user}' has permission '{perm}', cannot elevate to "
                f"permission '{access_level}'."
            )

    def notify_users(self, sender, verb, description):
        """Notify all users with permissions except sender (and anonymous, if any)"""
        anonymous_user = get_anonymous_user()
        exclude_q = Q(user=sender)
        if anonymous_user is not None:
            exclude_q |= Q(user=anonymous_user)
        for permission in self.user_permissions.exclude(exclude_q):
            notify.send(
                sender=sender,
                recipient=permission.user,
                verb=verb,
                description=description,
            )

    def get_users(self):
        """Return all users with their permissions"""
        return [(perm.user, perm.allow) for perm in self.user_permissions.all()]


class UserPermission(models.Model):
    """Single permission for a specific user"""

    class Meta:
        unique_together = ("parent", "user")
        indexes = [
            models.Index(fields=['user', 'parent'], name='userperm_user_parent_idx'),
            models.Index(fields=['parent'], name='userperm_parent_idx'),
        ]

    parent = models.ForeignKey(
        PermissionSet, on_delete=models.CASCADE, related_name="user_permissions"
    )

    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE
    )

    allow = models.CharField(max_length=4, choices=PERMISSION_CHOICES)
