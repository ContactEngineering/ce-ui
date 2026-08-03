"""Tests for the BokehJS version rendered into the page.

`app.html` loads BokehJS from the CDN while webpack compiles the app against the
`@bokeh/bokehjs` package (as an external), so the two versions have to agree. They
drifted apart once — 3.9.1 served, 3.9.2 compiled against — which is why the
version is now read from `package.json` instead of written out in the template.
"""

import json
import re
from pathlib import Path

import pytest

from ce_ui import bokehjs
from ce_ui.checks import check_bokehjs_version

PACKAGE_JSON = Path(__file__).parent.parent.parent / "package.json"


@pytest.fixture
def pinned_version():
    """The BokehJS version pinned in the repository's `package.json`."""
    if not PACKAGE_JSON.is_file():
        pytest.skip("not running from a source checkout")
    dependencies = json.loads(PACKAGE_JSON.read_text())["dependencies"]
    return dependencies[bokehjs.PACKAGE]


def test_version_is_the_pinned_one(pinned_version):
    assert bokehjs.VERSION == pinned_version


def test_fallback_names_the_pinned_version(pinned_version):
    """The fallback only applies when `package.json` is unreadable, but it should
    still name the version actually in use — the system check reports it
    otherwise."""
    assert bokehjs.FALLBACK_VERSION == pinned_version
    assert check_bokehjs_version(None) == []


def test_range_specifiers_are_stripped(monkeypatch, tmp_path):
    """The CDN serves specific releases, not ranges."""
    manifest = tmp_path / "package.json"
    manifest.write_text(json.dumps({"dependencies": {bokehjs.PACKAGE: "^4.1.2"}}))
    monkeypatch.setattr(bokehjs, "_CANDIDATE_PATHS", (manifest,))
    assert bokehjs.read_declared_version() == "4.1.2"


def test_no_version_without_a_readable_manifest(monkeypatch, tmp_path):
    monkeypatch.setattr(bokehjs, "_CANDIDATE_PATHS", (tmp_path / "missing.json",))
    assert bokehjs.read_declared_version() is None


def test_check_warns_when_the_manifest_cannot_be_read(monkeypatch, tmp_path):
    monkeypatch.setattr(bokehjs, "_CANDIDATE_PATHS", (tmp_path / "missing.json",))
    (warning,) = check_bokehjs_version(None)
    assert warning.id == "ce_ui.W001"


def test_check_warns_when_the_fallback_is_stale(monkeypatch, tmp_path):
    manifest = tmp_path / "package.json"
    manifest.write_text(json.dumps({"dependencies": {bokehjs.PACKAGE: "9.9.9"}}))
    monkeypatch.setattr(bokehjs, "_CANDIDATE_PATHS", (manifest,))
    (warning,) = check_bokehjs_version(None)
    assert warning.id == "ce_ui.W002"
    assert "9.9.9" in warning.msg


def test_page_loads_the_pinned_bokehjs(db, client, orcid_socialapp, pinned_version):
    """Both script tags on a rendered page name the pinned version."""
    response = client.get("/")
    assert response.status_code == 200
    urls = re.findall(
        r"https://cdn\.bokeh\.org/bokeh/release/(bokeh(?:-api)?)-([^\"]+)\.min\.js",
        response.content.decode(),
    )
    assert urls == [("bokeh", pinned_version), ("bokeh-api", pinned_version)]
