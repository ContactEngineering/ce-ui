"""Tests for the analysis pages and the subject handling they rely on.

Two behaviours matter here beyond the pages rendering at all:

* which extra breadcrumb tabs open for a given selection, which is what lets a
  user get back to the dataset they came from, and
* that a `subjects` parameter which cannot be decoded is ignored rather than
  raising, since the parameter travels in URLs that get shared and edited.
"""

import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse
from topobank.analysis.models import Workflow
from topobank.manager.utils import subjects_to_base64
from topobank.testing.factories import SurfaceFactory, Topography1DFactory

from ce_ui.views import (_safe_subjects_from_request,
                         extra_tabs_if_single_item_selected)

#: Registered by the repository's `conftest.py`.
WORKFLOW = "topobank.testing.test"

PASSWORD = "abcd$1234"


@pytest.fixture
def analyst(db, client, django_user_model):
    """A logged-in user, past the terms-and-conditions gate."""
    user = django_user_model.objects.create_user(
        username="analyst", password=PASSWORD
    )
    user.user_permissions.add(Permission.objects.get(codename="can_skip_terms"))
    assert client.login(username="analyst", password=PASSWORD)
    return user


def tab_titles(context):
    return [tab["title"] for tab in context["extra_tabs"]]


#
# Which tabs open for a selection
#


@pytest.mark.django_db
def test_a_single_measurement_opens_its_dataset_and_itself():
    surface = SurfaceFactory()
    topography = Topography1DFactory(surface=surface)
    context = {}

    extra_tabs_if_single_item_selected(context, [topography])

    assert tab_titles(context) == [surface.label, topography.name]
    assert [tab["href"] for tab in context["extra_tabs"]] == [
        reverse("ce_ui:surface-detail", kwargs={"pk": surface.pk}),
        reverse("ce_ui:topography-detail", kwargs={"pk": topography.pk}),
    ]
    # Neither is the current page; the analysis tab added afterwards is
    assert not any(tab["active"] for tab in context["extra_tabs"])


@pytest.mark.django_db
def test_a_single_dataset_opens_only_the_dataset():
    surface = SurfaceFactory()
    context = {}

    extra_tabs_if_single_item_selected(context, [surface])

    assert tab_titles(context) == [surface.label]


@pytest.mark.django_db
def test_a_dataset_with_its_own_measurements_opens_the_dataset():
    surface = SurfaceFactory()
    topographies = [Topography1DFactory(surface=surface) for _ in range(2)]
    context = {}

    extra_tabs_if_single_item_selected(context, [surface, *topographies])

    # The measurements belong to the selected dataset, so it is still a single
    # subject as far as the breadcrumbs are concerned
    assert tab_titles(context) == [surface.label]


@pytest.mark.django_db
def test_a_measurement_from_another_dataset_opens_nothing():
    surface = SurfaceFactory()
    foreign = Topography1DFactory(surface=SurfaceFactory())
    context = {}

    extra_tabs_if_single_item_selected(context, [surface, foreign])

    # The selection spans two datasets, so there is no single one to link to
    assert context.get("extra_tabs", []) == []


@pytest.mark.django_db
def test_several_datasets_open_nothing():
    context = {}

    extra_tabs_if_single_item_selected(
        context, [SurfaceFactory(), SurfaceFactory()]
    )

    assert context.get("extra_tabs", []) == []


def test_an_empty_selection_opens_nothing():
    context = {}

    extra_tabs_if_single_item_selected(context, [])

    assert context.get("extra_tabs", []) == []


#
# Decoding the `subjects` parameter
#


@pytest.mark.django_db
def test_subjects_are_decoded_from_the_parameter(rf, analyst):
    topography = Topography1DFactory(surface=SurfaceFactory(created_by=analyst))
    request = rf.get(
        "/ui/analysis-list/", {"subjects": subjects_to_base64([topography])}
    )
    request.user = analyst

    subjects = _safe_subjects_from_request(request)

    assert [subject.pk for subject in subjects] == [topography.pk]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "value",
    ["", "not base64 at all!!", "aGVsbG8=", "e30="],
    ids=["empty", "not-base64", "base64-but-not-json", "json-but-not-subjects"],
)
def test_an_undecodable_parameter_selects_nothing(rf, analyst, value):
    request = rf.get("/ui/analysis-list/", {"subjects": value})
    request.user = analyst

    # These URLs get shared and hand-edited, so a broken one must not be a 500
    assert _safe_subjects_from_request(request) == []


@pytest.mark.django_db
def test_a_missing_parameter_selects_nothing(rf, analyst):
    request = rf.get("/ui/analysis-list/")
    request.user = analyst

    assert _safe_subjects_from_request(request) == []


#
# The pages
#


@pytest.mark.django_db
def test_analysis_list_page_offers_the_analyze_tab(client, analyst):
    response = client.get(reverse("ce_ui:results-list"))

    assert response.status_code == 200
    current = response.context["extra_tabs"][-1]
    assert current["title"] == "Analyze"
    assert current["active"] is True
    # The basket lets the selection be changed from this page
    assert current["show_basket"] is True


@pytest.mark.django_db
def test_analysis_list_page_opens_tabs_for_the_selected_measurement(client, analyst):
    surface = SurfaceFactory(created_by=analyst)
    topography = Topography1DFactory(surface=surface)

    response = client.get(
        reverse("ce_ui:results-list"),
        {"subjects": subjects_to_base64([topography])},
    )

    assert response.status_code == 200
    assert tab_titles(response.context) == [
        surface.label,
        topography.name,
        "Analyze",
    ]


@pytest.mark.django_db
def test_analysis_list_page_ignores_a_broken_selection(client, analyst):
    response = client.get(
        reverse("ce_ui:results-list"), {"subjects": "not base64 at all!!"}
    )

    assert response.status_code == 200
    assert tab_titles(response.context) == ["Analyze"]


@pytest.mark.django_db
def test_workflow_page_names_the_workflow(client, analyst):
    response = client.get(
        reverse("ce_ui:results-detail", kwargs={"slug": WORKFLOW})
    )

    assert response.status_code == 200
    tabs = response.context["extra_tabs"]
    # Back to all results, then the workflow being looked at
    assert tabs[-2]["title"] == "Analyze"
    assert tabs[-1]["title"] == Workflow(name=WORKFLOW).display_name
    assert tabs[-1]["active"] is True


@pytest.mark.django_db
def test_workflow_page_opens_tabs_for_the_selected_measurement(client, analyst):
    surface = SurfaceFactory(created_by=analyst)
    topography = Topography1DFactory(surface=surface)

    response = client.get(
        reverse("ce_ui:results-detail", kwargs={"slug": WORKFLOW}),
        {"subjects": subjects_to_base64([topography])},
    )

    assert response.status_code == 200
    assert tab_titles(response.context)[:2] == [surface.label, topography.name]


@pytest.mark.django_db
def test_an_unknown_workflow_is_not_found(client, analyst):
    response = client.get(
        reverse("ce_ui:results-detail", kwargs={"slug": "nosuch.workflow"})
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_a_workflow_the_user_may_not_run_is_forbidden(client, analyst, monkeypatch):
    monkeypatch.setattr("ce_ui.views.get_workflow_names", lambda user=None: [])

    response = client.get(
        reverse("ce_ui:results-detail", kwargs={"slug": WORKFLOW})
    )

    assert response.status_code == 403
