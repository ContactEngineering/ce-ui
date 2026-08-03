"""Tests for the server-rendered metadata on a dataset landing page.

The page is rendered by Vue, so anything a harvester is supposed to find has to
be in the HTML the server sends. A published dataset's DOI resolves here, see
https://github.com/ContactEngineering/topobank-publication/issues/21.
"""

import json
import re

import pytest
from django.urls import NoReverseMatch, reverse
from topobank.testing.factories import (SurfaceFactory, Topography1DFactory,
                                        UserFactory)
from topobank_publication.models import Publication


def _has_schema_org_support():
    """Whether the installed publication plugin can describe a dataset.

    The schema.org description and the endpoint serving it arrived together in
    one release of topobank-publication; an older one renders the rest of the
    metadata and simply omits those parts.
    """
    try:
        import topobank_publication.schema_org  # noqa: F401

        reverse("publication:metadata", kwargs={"short_url": "abcde"})
    except (ImportError, NoReverseMatch):
        return False
    return True


requires_schema_org = pytest.mark.skipif(
    not _has_schema_org_support(),
    reason="installed topobank-publication has no schema.org description",
)

AUTHORS = [
    {
        "first_name": "Harry",
        "last_name": "Potter",
        "orcid_id": "9999-9999-9999-9999",
        "affiliations": [{"name": "Hogwarts", "ror_id": ""}],
    },
    {
        "first_name": "Hermione",
        "last_name": "Granger",
        "orcid_id": "",
        "affiliations": [{"name": "Hogwarts", "ror_id": ""}],
    },
]


@pytest.fixture
def published(db, settings, orcid_socialapp):
    """A published dataset with a DOI."""
    settings.PUBLICATION_DOI_MANDATORY = False
    user = UserFactory()
    surface = SurfaceFactory(
        created_by=user,
        name="Microcrystalline Diamond",
        description="MCD surface topography measured using TEM, AFM and Stylus.",
    )
    Topography1DFactory(surface=surface)
    publication = Publication.publish(surface, "ccby-4.0", user, AUTHORS)
    publication.doi_name = "10.12345/ce-abcde"
    publication.doi_state = Publication.DOI_STATE_FINDABLE
    publication.save()
    return publication


@pytest.fixture
def unpublished(db, orcid_socialapp):
    user = UserFactory()
    surface = SurfaceFactory(created_by=user, name="Work in progress")
    Topography1DFactory(surface=surface)
    return surface


def _get(client, surface):
    response = client.get(
        reverse("ce_ui:surface-detail", kwargs={"pk": surface.pk})
    )
    assert response.status_code == 200
    return response.content.decode()


def _meta(html, name):
    """Attribute values of the meta tags with this name, order preserved."""
    return re.findall(rf'<meta name="{name}"\s+content="([^"]*)"', html)


def _links(html, relation):
    """Targets of the link elements with this relation, order preserved."""
    return re.findall(rf'<link rel="{relation}"\s+href="([^"]*)"', html)


def _jsonld(html):
    match = re.search(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.S
    )
    return json.loads(match.group(1)) if match else None


@pytest.mark.django_db
def test_title_names_the_dataset(client, published):
    html = _get(client, published.surface)

    assert "<title>" in html
    assert "Microcrystalline Diamond - contact.engineering" in html


@pytest.mark.django_db
def test_description_and_authors_are_rendered(client, published):
    html = _get(client, published.surface)

    assert _meta(html, "description") == [
        "MCD surface topography measured using TEM, AFM and Stylus."
    ]
    assert _meta(html, "author") == ["Harry Potter, Hermione Granger"]


@requires_schema_org
@pytest.mark.django_db
def test_schema_org_description_is_embedded(client, published):
    """This is what a harvester that does not run JavaScript reads."""
    described = _jsonld(_get(client, published.surface))

    assert described["@type"] == "Dataset"
    assert described["name"] == "Microcrystalline Diamond"
    assert described["identifier"] == "https://doi.org/10.12345/ce-abcde"
    assert described["distribution"][0]["@type"] == "DataDownload"


@pytest.mark.django_db
def test_citation_metadata_is_rendered(client, published):
    html = _get(client, published.surface)

    assert _meta(html, "citation_title") == ["Microcrystalline Diamond"]
    assert _meta(html, "citation_author") == ["Potter, Harry", "Granger, Hermione"]
    assert _meta(html, "citation_doi") == ["10.12345/ce-abcde"]
    assert _meta(html, "citation_publication_date") == [
        published.datetime.strftime("%Y/%m/%d")
    ]


@pytest.mark.django_db
def test_typed_links_are_rendered(client, published):
    html = _get(client, published.surface)

    assert _links(html, "cite-as") == ["https://doi.org/10.12345/ce-abcde"]
    assert _links(html, "license") == [
        "https://creativecommons.org/licenses/by/4.0/legalcode"
    ]
    assert _links(html, "item")[0].endswith(
        reverse(
            "publication:download-container",
            kwargs={"short_url": published.short_url},
        )
    )


@requires_schema_org
@pytest.mark.django_db
def test_description_of_the_dataset_is_linked(client, published):
    html = _get(client, published.surface)

    assert _links(html, "describedby")[0].endswith(
        reverse("publication:metadata", kwargs={"short_url": published.short_url})
    )


@pytest.mark.django_db
def test_only_authors_with_an_orcid_are_linked(client, published):
    html = _get(client, published.surface)

    assert _links(html, "author") == ["https://orcid.org/9999-9999-9999-9999"]


@pytest.mark.django_db
def test_unpublished_dataset_keeps_the_generic_head(client, unpublished):
    """An unpublished dataset is not public and has nothing to advertise."""
    unpublished.grant_permission(unpublished.created_by, "view")
    client.force_login(unpublished.created_by)

    html = _get(client, unpublished)

    assert "contact.engineering - A surface topography cloud database" in html
    assert _jsonld(html) is None
    assert _meta(html, "citation_title") == []
    assert _links(html, "cite-as") == []


@requires_schema_org
@pytest.mark.django_db
def test_script_terminator_in_metadata_cannot_break_out(client, published):
    """A description is user input and ends up inside a <script> element."""
    published.surface.description = "Trouble: </script><script>alert(1)</script>"
    published.surface.save()

    html = _get(client, published.surface)

    assert "<script>alert(1)</script>" not in html
    assert _jsonld(html)["description"].startswith("Trouble:")
