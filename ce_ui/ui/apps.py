import logging
from importlib.metadata import version

__version__ = version("ce-ui")

try:
    from topobank.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use topobank 0.92.0 or above to use this plugin!")

_log = logging.Logger(__file__)


class CEUIPluginConfig(PluginConfig):
    name = 'ce_ui'
    verbose_name = "contact.engineering"

    class TopobankPluginMeta:
        name = "contact.engineering"
        version = __version__
        description = """
        The contact.engineering user interface
        """
        logo = "ce_ui/static/images/ce_logo.svg"
        restricted = False  # Accessible for all users, without permissions

    def ready(self):
        pass
