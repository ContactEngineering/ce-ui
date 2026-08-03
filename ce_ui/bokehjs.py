"""The version of BokehJS that the frontend is written against.

`app.html` loads BokehJS from the CDN and webpack treats `@bokeh/bokehjs` as an
external (see `webpack.config.js`), so the version pinned in `package.json` and
the version in those script tags describe the same thing and have to agree. With
the version written out in the template they drifted apart: the app was compiled
against 3.9.2 and served 3.9.1.

`package.json` is therefore the single source of truth — it is the file Renovate
updates — and the template renders what is read from it.
"""

import json
from pathlib import Path

#: The npm package whose version the CDN URLs use.
PACKAGE = "@bokeh/bokehjs"

#: Used when `package.json` cannot be read at all, so that a packaging mistake
#: costs a possibly outdated BokehJS rather than every plot on the site. A system
#: check reports it when this has gone stale, see `checks.py`.
FALLBACK_VERSION = "3.9.2"

#: Where to look for `package.json`: next to the package, which is where the
#: wheel ships it (see `force-include` in `pyproject.toml`), then the repository
#: root, which is where it lives in a source checkout or an editable install.
_CANDIDATE_PATHS = (
    Path(__file__).parent / "package.json",
    Path(__file__).parent.parent / "package.json",
)


def read_declared_version():
    """Read the pinned BokehJS version from `package.json`.

    Returns
    -------
    str or None
        The version, or None if no readable `package.json` declares the package.
    """
    for path in _CANDIDATE_PATHS:
        try:
            with path.open() as stream:
                manifest = json.load(stream)
        except (OSError, json.JSONDecodeError):
            continue
        version = manifest.get("dependencies", {}).get(PACKAGE)
        if version is not None:
            # The CDN serves specific releases, so strip any range specifier a
            # future edit of `package.json` might introduce.
            return version.lstrip("^~=v ")
    return None


#: The version the templates render into the CDN URLs.
VERSION = read_declared_version() or FALLBACK_VERSION
