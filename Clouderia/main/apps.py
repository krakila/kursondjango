from django.apps import AppConfig
def ready(self):
    import accounts.signals

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
