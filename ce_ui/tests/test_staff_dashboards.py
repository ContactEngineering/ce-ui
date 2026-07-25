"""
Tests for the staff dashboards against the real (ORCID-backed) user model.

The REST API tests in `topobank-rest-api` run against the mock user model,
which carries `orcid_id` as a plain column. Here the ORCID iD really does live
in the allauth social account, so these tests cover the JSON annotation path
end to end, along with the staff gate on the HTML pages.
"""

import pytest
from django.urls import reverse
from topobank.testing.factories import (SurfaceFactory, Topography1DFactory,
                                        UserFactory)


@pytest.fixture
def staff_user(db):
    return UserFactory(username="dashboard-staff", name="Dash Board", is_staff=True)


@pytest.mark.django_db
@pytest.mark.parametrize("url_name", ["ce_ui:staff-users", "ce_ui:staff-tasks"])
def test_dashboard_pages_require_staff(client, url_name, user_alice, staff_user,
                                       orcid_socialapp):
    url = reverse(url_name)

    # Anonymous visitors are bounced to the admin login.
    response = client.get(url)
    assert response.status_code == 302
    assert "/login" in response.url

    # So are signed-in users without the staff flag.
    client.force_login(user_alice)
    response = client.get(url)
    assert response.status_code == 302

    client.force_login(staff_user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_dashboard_pages_mount_the_right_component(client, staff_user,
                                                   orcid_socialapp):
    client.force_login(staff_user)

    response = client.get(reverse("ce_ui:staff-users"))
    assert response.context["vue_component"] == "StaffUserDashboard"

    response = client.get(reverse("ce_ui:staff-tasks"))
    assert response.context["vue_component"] == "StaffTaskDashboard"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url_name", ["staff:user-list", "staff:task-list", "staff:worker"]
)
def test_api_requires_staff(client, url_name, user_alice, staff_user):
    url = reverse(url_name)

    assert client.get(url).status_code == 403

    client.force_login(user_alice)
    assert client.get(url).status_code == 403

    client.force_login(staff_user)
    assert client.get(url).status_code == 200


@pytest.mark.django_db
def test_user_list_resolves_orcid_from_social_account(client, staff_user, user_alice):
    """
    On the production model `orcid_id` is a property backed by a SocialAccount
    lookup; the dashboard must produce the same value from a single query.
    """
    surface = SurfaceFactory(created_by=user_alice)
    Topography1DFactory(surface=surface, created_by=user_alice)

    client.force_login(staff_user)
    response = client.get(reverse("staff:user-list"), {"search": "alice"})
    assert response.status_code == 200

    results = response.json()["results"]
    assert len(results) == 1
    row = results[0]

    assert row["orcid"] == user_alice.orcid_id
    assert row["orcid"] is not None
    assert row["name"] == user_alice.name
    assert row["num_surfaces"] == 1
    assert row["num_topographies"] == 1
    assert row["date_joined"] is not None


@pytest.mark.django_db
def test_user_list_search_by_orcid(client, staff_user, user_alice):
    client.force_login(staff_user)
    response = client.get(
        reverse("staff:user-list"), {"search": user_alice.orcid_id}
    )

    usernames = {row["username"] for row in response.json()["results"]}
    assert user_alice.username in usernames


@pytest.mark.django_db
def test_user_list_query_count_is_constant(client, staff_user,
                                           django_assert_num_queries):
    for i in range(3):
        UserFactory(username=f"warmup-{i}")

    client.force_login(staff_user)
    url = reverse("staff:user-list")

    # Warm up caches (active terms, session, content types) first.
    assert client.get(url, {"limit": 2}).status_code == 200

    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    with CaptureQueriesContext(connection) as captured:
        assert client.get(url, {"limit": 2}).status_code == 200
    baseline = len(captured)

    for i in range(10):
        UserFactory(username=f"extra-{i}")

    # Resolving 13 ORCID iDs through the model property would add 13 queries.
    with django_assert_num_queries(baseline):
        assert client.get(url, {"limit": 100}).status_code == 200


@pytest.mark.django_db
def test_worker_endpoint_survives_an_unreachable_broker(client, staff_user,
                                                        monkeypatch):
    from topobank_rest_api.staff import celery_inspect

    monkeypatch.setattr(
        celery_inspect.app.control,
        "inspect",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("no broker here")),
    )
    celery_inspect.cache.delete(celery_inspect.CACHE_KEY)

    client.force_login(staff_user)
    response = client.get(reverse("staff:worker"))

    assert response.status_code == 200
    data = response.json()
    assert data["available"] is False
    assert data["num_workers"] == 0
