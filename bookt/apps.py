from django.apps import AppConfig


class BooktConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bookt'
    def ready(self):
        import bookt.signals

