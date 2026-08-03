"""
Server-rendered metadata for the landing page of a published dataset.

The dataset page is rendered by Vue, so a client that does not execute
JavaScript sees the app shell and nothing else. For a published dataset that is
a problem: its DOI resolves to that page, and it is where FAIR assessment tools,
search engines and reference managers come looking for the metadata. They do not
run JavaScript, so whatever they are supposed to find has to be in the HTML that
the server sends.

This module collects what the template needs. Only published datasets are
described: an unpublished one is not public and has nothing to advertise.
"""

import json
import logging

from django.conf import settings
from django.urls import NoReverseMatch, reverse
from django.utils.safestring import mark_safe

_log = logging.getLogger(__name__)

# Longest description we put into a meta tag. Search engines cut descriptions off
# at a few hundred characters anyway, and dataset descriptions can be long.
MAX_DESCRIPTION_LENGTH = 300


def _jsonld(publication, request):
    """Render the schema.org description of a publication as embeddable JSON.

    Returns None if the installed publication plugin cannot produce one. The
    plugin only gained this ability in the release that added `schema_org`, and
    an older one must not break the page.
    """
    try:
        from topobank_publication.schema_org import schema_org_dataset
    except ImportError:
        _log.debug(
            "Installed topobank-publication provides no schema.org description."
        )
        return None

    document = json.dumps(schema_org_dataset(publication, request))
    # The document is embedded in a <script> element, so the characters that
    # could end it early have to be escaped. This is what Django's `json_script`
    # filter does; it cannot be used here because it hardcodes the script type.
    document = (
        document.replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )
    return mark_safe(document)  # noqa: S308 - escaped just above


def _reverse_absolute(request, view_name, **kwargs):
    """Absolute URL of a route, or None if the route does not exist."""
    try:
        return request.build_absolute_uri(reverse(view_name, kwargs=kwargs))
    except NoReverseMatch:
        return None


def _description(surface):
    """Single-line, length-limited description of a dataset."""
    description = " ".join((surface.description or "").split())
    if len(description) > MAX_DESCRIPTION_LENGTH:
        description = description[: MAX_DESCRIPTION_LENGTH - 1].rstrip() + "…"
    return description


def publication_metadata(surface, request):
    """
    Collect the metadata of a published dataset for its landing page.

    Parameters
    ----------
    surface : Surface
        The dataset the page is about.
    request : HttpRequest
        Request used to turn routes into absolute URLs.

    Returns
    -------
    dict
        Template context. `publication` is None for a dataset that is not
        published, which is what the template keys off.
    """
    # The related name only exists while the publication plugin is installed,
    # and only published datasets have one.
    publication = getattr(surface, "publication", None)
    if publication is None:
        return {"publication": None}

    return {
        "publication": publication,
        "dataset_name": surface.name,
        "dataset_description": _description(surface),
        "dataset_authors": publication.get_authors_string(),
        "landing_page_url": request.build_absolute_uri(
            publication.get_absolute_url()
        ),
        "container_url": _reverse_absolute(
            request,
            "publication:download-container",
            short_url=publication.short_url,
        ),
        "metadata_url": _reverse_absolute(
            request, "publication:metadata", short_url=publication.short_url
        ),
        "license_url": settings.CC_LICENSE_INFOS[publication.license][
            "legal_code_url"
        ],
        "schema_org_jsonld": _jsonld(publication, request),
    }
