import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from topobank.authorization import get_permission_model

from ce_ui.authorization.models import PermissionSet


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(username="alice", password="password", name="Alice")


@pytest.fixture
def other_user(db):
    User = get_user_model()
    return User.objects.create_user(username="bob", password="password", name="Bob")


@pytest.fixture
def permission_set(user):
    return PermissionSet.objects.create(user=user, allow="full")


@pytest.mark.django_db
def test_permission_set_creation(permission_set, user):
    assert permission_set.user_has_permission(user, "view")
    assert permission_set.user_has_permission(user, "edit")
    assert permission_set.user_has_permission(user, "full")


@pytest.mark.django_db
def test_grant_and_revoke_user(permission_set, other_user):
    permission_set.grant_for_user(other_user, "view")
    assert permission_set.user_has_permission(other_user, "view")
    assert not permission_set.user_has_permission(other_user, "edit")

    permission_set.revoke_from_user(other_user)
    assert not permission_set.user_has_permission(other_user, "view")


@pytest.mark.django_db
def test_authorize_user_raises_on_insufficient(permission_set, other_user):
    permission_set.grant_for_user(other_user, "view")
    with pytest.raises(PermissionDenied):
        permission_set.authorize_user(other_user, "full")


@pytest.mark.django_db
def test_authorize_user_raises_not_found_when_no_permission(permission_set, other_user):
    from django.http import Http404
    with pytest.raises(Http404):
        permission_set.authorize_user(other_user, "view")


@pytest.mark.django_db
def test_filter_queryset(user, other_user):
    ps1 = PermissionSet.objects.create(user=user, allow="view")
    ps2 = PermissionSet.objects.create(user=other_user, allow="view")

    visible = PermissionSet.objects.for_user(user, "view")
    assert ps1 in visible
    assert ps2 not in visible


@pytest.mark.django_db
def test_get_permission_model():
    assert get_permission_model() is PermissionSet
