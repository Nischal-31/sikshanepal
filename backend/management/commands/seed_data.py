# backend/management/commands/seed_data.py
import json
from django.core.management.base import BaseCommand
from backend.models import (
    Course, Semester, Subject, Lab, PastQuestion, Syllabus, Chapter, Note
)


class Command(BaseCommand):
    help = "Seed database from a nested JSON file"

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file",
            type=str,
            help="Path to the JSON seed file"
        )

    def handle(self, *args, **options):
        path = options["json_file"]
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        for c in data.get("courses", []):
            semesters = c.pop("semesters", [])
            course, created = Course.objects.get_or_create(
                name=c["name"],
                defaults={"description": c.get("description", "")}
            )
            self.stdout.write(self.style.SUCCESS(f"{'Created' if created else 'Found'} Course: {course}"))

            for s in semesters:
                subjects = s.pop("subjects", [])
                semester, created = Semester.objects.get_or_create(
                    course=course,
                    number=s["number"],
                    defaults={"description": s.get("description", "")}
                )
                self.stdout.write(f"  {'Created' if created else 'Found'} Semester: {semester}")

                for sub in subjects:
                    chapters = sub.pop("chapters", [])
                    labs = sub.pop("labs", [])
                    past_questions = sub.pop("past_questions", [])
                    syllabus_data = sub.pop("syllabus", None)

                    subject, created = Subject.objects.get_or_create(
                        semester=semester,
                        code=sub["code"],
                        defaults={
                            "name": sub["name"],
                            "credits": sub.get("credits", 3),
                            "description": sub.get("description", "")
                        }
                    )
                    self.stdout.write(f"    {'Created' if created else 'Found'} Subject: {subject}")

                    if syllabus_data:
                        Syllabus.objects.get_or_create(
                            subject=subject,
                            defaults={"objectives": syllabus_data.get("objectives", "")}
                        )

                    for lab in labs:
                        Lab.objects.get_or_create(
                            subject=subject,
                            title=lab["title"],
                            defaults={"description": lab.get("description", "")}
                        )

                    for pq in past_questions:
                        PastQuestion.objects.get_or_create(
                            subject=subject,
                            year=pq["year"],
                            defaults={
                                "title": pq["title"],
                                "description": pq.get("description", "")
                            }
                        )

                    for ch in chapters:
                        notes = ch.pop("notes", [])
                        chapter, created = Chapter.objects.get_or_create(
                            subject=subject,
                            order=ch["order"],
                            defaults={
                                "title": ch["title"],
                                "description": ch.get("description", "")
                            }
                        )
                        self.stdout.write(f"      {'Created' if created else 'Found'} Chapter: {chapter}")

                        for note in notes:
                            Note.objects.get_or_create(
                                chapter=chapter,
                                title=note["title"],
                                defaults={
                                    "description": note.get("description", ""),
                                    "file": ""  # required field, no blank=True — empty string is safe at DB level
                                }
                            )

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))

#Running it 
# python manage.py seed_data data/seed.json