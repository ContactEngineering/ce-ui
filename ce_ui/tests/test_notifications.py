"""
Notifications that refer to a model which no longer exists.

Deleting a model leaves its content type and every notification referring to
it in the database. django-notifications resolves the actor, target and action
object of each notification it lists, and a content type without a model class
raises "'NoneType' object has no attribute '_base_manager'". Old notifications
of the removed AnalysisCollection model broke the unread list of the users who
had them in production.
"""

import importlib

import pytest
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from notifications.models import Notification
from notifications.signals import notify
from topobank.testing.factories import UserFactory

from ce_ui.utils import delete_notifications_of_removed_models

UNREAD_LIST_URL = "/inbox/notifications/api/unread_list/"


@pytest.fixture
def removed_model():
    """Content type of a model that once existed, like AnalysisCollection."""
    return ContentType.objects.create(app_label="analysis", model="analysiscollection")


def _notification(recipient, **content_types):
    """A notification whose generic relations point to the given content types."""
    fields = {"actor_content_type": ContentType.objects.get_for_model(recipient),
              "actor_object_id": str(recipient.pk)}
    for relation, content_type in content_types.items():
        fields[f"{relation}_content_type"] = content_type
        fields[f"{relation}_object_id"] = "1"
    return Notification.objects.create(recipient=recipient, verb="finished", **fields)


@pytest.mark.django_db
@pytest.mark.parametrize("relation", ["actor", "target", "action_object"])
def test_removes_notifications_of_removed_models(client, removed_model, relation):
    user = UserFactory()
    broken = _notification(user, **{relation: removed_model})
    notify.send(sender=user, recipient=user, verb="imported")
    client.force_login(user)

    # This is the production traceback
    with pytest.raises(AttributeError, match="_base_manager"):
        client.get(UNREAD_LIST_URL)

    assert delete_notifications_of_removed_models() == 1

    assert not Notification.objects.filter(pk=broken.pk).exists()
    response = client.get(UNREAD_LIST_URL)
    assert response.status_code == 200
    assert response.json()["unread_count"] == 1
    assert [n["verb"] for n in response.json()["unread_list"]] == ["imported"]


@pytest.mark.django_db
def test_keeps_notifications_whose_object_was_merely_deleted(client):
    # A deleted object of an existing model resolves to None and does no harm
    user = UserFactory()
    other = UserFactory()
    notify.send(sender=other, recipient=user, verb="shared")
    other.delete()

    assert delete_notifications_of_removed_models() == 0
    assert Notification.objects.filter(recipient=user).count() == 1


@pytest.mark.django_db
def test_keeps_content_types_and_unrelated_rows(removed_model):
    user = UserFactory()
    notify.send(sender=user, recipient=user, verb="imported")

    assert delete_notifications_of_removed_models() == 0

    assert ContentType.objects.filter(pk=removed_model.pk).exists()
    assert Notification.objects.count() == 1


@pytest.mark.django_db
def test_migration_removes_notifications_of_removed_models(removed_model):
    user = UserFactory()
    broken = _notification(user, actor=removed_model)
    migration = importlib.import_module(
        "ce_ui.migrations.0002_delete_notifications_of_removed_models"
    )

    migration.delete_notifications(apps, None)

    assert not Notification.objects.filter(pk=broken.pk).exists()
