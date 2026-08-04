"""Tests for the breadcrumb navigation tabs.

The interesting part is `add_topography`, which links to the previous and next
measurement of the *same* dataset so that they can be stepped through from the
detail page.
"""

import pytest
from django.urls import reverse
from topobank.testing.factories import SurfaceFactory, Topography1DFactory

from ce_ui import breadcrumb


def titles(context):
    return [tab["title"] for tab in context["extra_tabs"]]


def test_context_without_tabs_gets_a_tab_list():
    context = {}

    breadcrumb.prepare_context(context)

    assert context["extra_tabs"] == []


def test_adding_a_tab_deactivates_the_ones_before_it():
    context = {"extra_tabs": [{"title": "Datasets", "active": True}]}

    breadcrumb.add_generic(context, {"title": "Analyze", "active": True})

    # Only the tab added last is the current one
    assert [tab["active"] for tab in context["extra_tabs"]] == [False, True]
    assert titles(context) == ["Datasets", "Analyze"]


@pytest.mark.django_db
def test_dataset_tab_points_at_the_dataset():
    surface = SurfaceFactory()
    context = {}

    breadcrumb.add_surface(context, surface)

    (tab,) = context["extra_tabs"]
    assert tab["title"] == surface.label
    assert tab["href"] == reverse("ce_ui:surface-detail", kwargs={"pk": surface.pk})
    assert tab["active"] is True
    assert tab["login_required"] is False


@pytest.mark.django_db
def test_measurement_tab_links_to_both_neighbours():
    surface = SurfaceFactory()
    first, middle, last = (Topography1DFactory(surface=surface) for _ in range(3))
    context = {}

    breadcrumb.add_topography(context, middle)

    (tab,) = context["extra_tabs"]
    assert tab["title"] == middle.name
    assert tab["href"] == reverse(
        "ce_ui:topography-detail", kwargs={"pk": middle.pk}
    )
    assert tab["href_previous"] == reverse(
        "ce_ui:topography-detail", kwargs={"pk": first.pk}
    )
    assert tab["href_next"] == reverse(
        "ce_ui:topography-detail", kwargs={"pk": last.pk}
    )


@pytest.mark.django_db
def test_first_measurement_has_no_previous_and_last_has_no_next():
    surface = SurfaceFactory()
    first, _, last = (Topography1DFactory(surface=surface) for _ in range(3))

    first_context = {}
    breadcrumb.add_topography(first_context, first)
    last_context = {}
    breadcrumb.add_topography(last_context, last)

    (first_tab,) = first_context["extra_tabs"]
    (last_tab,) = last_context["extra_tabs"]
    assert "href_previous" not in first_tab
    assert "href_next" in first_tab
    assert "href_next" not in last_tab
    assert "href_previous" in last_tab


@pytest.mark.django_db
def test_a_lone_measurement_has_no_neighbours():
    topography = Topography1DFactory(surface=SurfaceFactory())
    context = {}

    breadcrumb.add_topography(context, topography)

    (tab,) = context["extra_tabs"]
    assert "href_next" not in tab
    assert "href_previous" not in tab


@pytest.mark.django_db
def test_neighbours_never_come_from_another_dataset():
    surface = SurfaceFactory()
    other_surface = SurfaceFactory()
    first = Topography1DFactory(surface=surface)
    # Created in between, so its primary key falls between the two measurements
    # of `surface`: stepping through must skip it regardless.
    Topography1DFactory(surface=other_surface)
    second = Topography1DFactory(surface=surface)

    context = {}
    breadcrumb.add_topography(context, first)

    (tab,) = context["extra_tabs"]
    assert tab["href_next"] == reverse(
        "ce_ui:topography-detail", kwargs={"pk": second.pk}
    )
