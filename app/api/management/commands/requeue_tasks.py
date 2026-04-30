from django.core.management.base import BaseCommand

from api.services import requeue_unfinished_requests


class Command(BaseCommand):
    help = "Requeue unfinished crack tasks"

    def handle(self, *args, **options):
        requeue_unfinished_requests()
        self.stdout.write(
            self.style.SUCCESS("Unfinished tasks requeued")
        )