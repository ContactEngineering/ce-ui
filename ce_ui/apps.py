from django.apps import AppConfig

from .version import __version__


class CEUIAppConfig(AppConfig):
    name = 'ce_ui'
    verbose_name = "contact.engineering"

    def ready(self):
        # make sure the functions are registered now

        # noinspection PyUnresolvedReferences
        import ce_ui.signals  # noqa: F401
