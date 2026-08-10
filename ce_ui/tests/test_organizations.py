import pytest
from django.contrib.auth import get_user_model
from topobank.authorization import get_organization_model


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(username="alice", password="password", name="Alice")


@pytest.fixture
def organization(db):
    Organization = get_organization_model()
    return Organization.objects.create(name="Test Organization")


@pytest.mark.django_db
def test_organization_creation(organization):
    assert organization.name == "Test Organization"
    assert organization.group is not None


@pytest.mark.django_db
def test_organization_str(organization):
    assert str(organization) == "Test Organization"


@pytest.mark.django_db
def test_add_user_to_organization(user, organization):
    organization.add(user)
    assert organization in get_organization_model().objects.for_user(user)


@pytest.mark.django_db
def test_resolve_by_id(organization):
    Organization = get_organization_model()
    resolved = Organization.resolve(str(organization.pk))
    assert resolved == organization


@pytest.mark.django_db
def test_organization_delete_removes_group(organization):
    from django.contrib.auth.models import Group
    group_name = organization.group.name
    organization.delete()
    assert not Group.objects.filter(name=group_name).exists()
