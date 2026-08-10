import pytest
from django.contrib.auth import get_user_model
from topobank.authorization import get_anonymous_user

from ce_ui.users.anonymous import ANONYMOUS_USER_NAME


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(username="alice", password="password", name="Alice")


@pytest.fixture
def anonymous_user(db):
    return get_anonymous_user()


@pytest.mark.django_db
def test_user_creation(user):
    assert user.username == "alice"
    assert user.name == "Alice"


@pytest.mark.django_db
def test_anonymous_user_exists(anonymous_user):
    User = get_user_model()
    assert User.objects.filter(username=ANONYMOUS_USER_NAME).exists()


@pytest.mark.django_db
def test_is_anonymous(user, anonymous_user):
    assert not user.is_anonymous
    assert anonymous_user.is_anonymous


@pytest.mark.django_db
def test_is_authenticated(user, anonymous_user):
    assert user.is_authenticated
    assert not anonymous_user.is_authenticated


@pytest.mark.django_db
def test_resolve_by_id(user):
    User = get_user_model()
    resolved = User.resolve(str(user.pk))
    assert resolved == user
