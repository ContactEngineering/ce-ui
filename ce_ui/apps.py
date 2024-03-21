from topobank.plugins import PluginConfig

from .version import __version__


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
        import ce_ui.signals  # noqa: F401
