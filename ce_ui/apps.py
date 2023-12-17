import logging
from importlib.metadata import version

from topobank.plugins import PluginConfig

__version__ = version("ce-ui")

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
        # make sure the functions are registered now

        # noinspection PyUnresolvedReferences
        import ce_ui.signals
