from django.apps import AppConfig


class AuthorizationAppConfig(AppConfig):
    name = 'ce_ui.authorization'
    label = 'authorization'

    def ready(self):
        pass
