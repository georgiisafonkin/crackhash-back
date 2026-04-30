from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    # def ready(self):
    #     from .services import requeue_unfinished_requests

    #     requeue_unfinished_requests()