from django.apps import AppConfig


class OCLettingsSiteConfig(AppConfig):
    """
    Configuration class for the 'oc_lettings_site' application.
    """
    name = 'oc_lettings_site'

    def ready(self):
        import oc_lettings_site.signals  # noqa: F401
