import json

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from user.models import CustomUser


class Command(BaseCommand):
    """
    Seed the CustomUser table from a JSON file.
    """

    help = "Seed users from a JSON file"

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file",
            type=str,
            help="Path to users JSON file"
        )

    def handle(self, *args, **options):

        path = options["json_file"]

        with open(path, encoding="utf-8") as file:
            data = json.load(file)

        users = data.get("users", [])

        if not users:
            self.stdout.write(
                self.style.WARNING("No users found in JSON.")
            )
            return

        for user_data in users:

            username = user_data["username"]

            user, created = CustomUser.objects.get_or_create(

                username=username,

                defaults={

                    "email": user_data["email"],
                    "first_name": user_data.get("first_name", ""),
                    "last_name": user_data.get("last_name", ""),
                    "phone_no": user_data.get("phone_no", ""),
                    "user_type": user_data.get("user_type", "student"),
                    "terms_agree": user_data.get("terms_agree", True),
                    "remember_me": user_data.get("remember_me", False),
                    "password": make_password(
                        user_data.get("password", "password123")
                    ),
                },
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created User: {user.username}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"User already exists: {user.username}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "✅ User seeding completed successfully."
            )
        )

#Run 
# python manage.py seed_users data/seedusers.json