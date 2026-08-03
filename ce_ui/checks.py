"""System checks for this app, reported by `manage.py check`."""

from django.core.checks import Warning, register

from . import bokehjs


@register()
def check_bokehjs_version(app_configs, **kwargs):
    """Report when the BokehJS version cannot be determined from `package.json`.

    The version served from the CDN has to match the one the app was compiled
    against. Both problems below leave the site working, but on a version nobody
    chose, so they are worth surfacing on deployment rather than in a plot that
    silently misbehaves.
    """
    declared = bokehjs.read_declared_version()
    if declared is None:
        return [
            Warning(
                f"Cannot read the pinned {bokehjs.PACKAGE} version: no readable "
                f"package.json was found next to the ce_ui package or in its "
                f"parent directory.",
                hint=(
                    f"The wheel is expected to ship package.json alongside the "
                    f"package; check the `force-include` entry in pyproject.toml. "
                    f"Templates fall back to BokehJS "
                    f"{bokehjs.FALLBACK_VERSION} in the meantime."
                ),
                id="ce_ui.W001",
            )
        ]
    if declared != bokehjs.FALLBACK_VERSION:
        return [
            Warning(
                f"ce_ui.bokehjs.FALLBACK_VERSION ({bokehjs.FALLBACK_VERSION}) is "
                f"stale: package.json pins {bokehjs.PACKAGE} "
                f"{declared}.",
                hint=(
                    "The fallback only applies when package.json cannot be read, "
                    "but it should still name the version that is actually in "
                    "use. Update FALLBACK_VERSION in ce_ui/bokehjs.py."
                ),
                id="ce_ui.W002",
            )
        ]
    return []
