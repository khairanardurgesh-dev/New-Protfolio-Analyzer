from django.apps import AppConfig


class AnalyzerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analyzer'

    # Remove ready() method to avoid import issues during deployment
    # def ready(self):
    #     import analyzer.signals
