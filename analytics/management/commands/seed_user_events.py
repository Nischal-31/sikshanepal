import json

from django.core.management.base import BaseCommand

from analytics.models import UserEvent
from user.models import CustomUser


class Command(BaseCommand):
    help = "Seed User Events from JSON"

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file",
            type=str,
            help="Path to user_events.json"
        )

    def handle(self, *args, **options):

        with open(options["json_file"], encoding="utf-8") as f:
            data = json.load(f)

        created_count = 0

        for event in data["events"]:

            try:
                user = CustomUser.objects.get(
    id=event["user_id"]
)
            except CustomUser.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"User {event['username']} not found."
                    )
                )
                continue

            UserEvent.objects.create(
                user=user,
                item_type=event["item_type"],
                item_id=event["item_id"],
                action=event["action"],
                session_key="seed_data",
                ip_address="127.0.0.1",
                user_agent="Seeder"
            )

            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created_count} User Events."
            )
        )

#Run
# python manage.py seed_user_events data/seeduserevents.json