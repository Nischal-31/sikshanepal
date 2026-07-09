import json

from django.core.management.base import BaseCommand

from backend.models import Subject
from quiz.models import Quiz, Question, Option


class Command(BaseCommand):
    help = "Seed quizzes from a JSON file"

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file",
            type=str,
            help="Path to quiz seed JSON file"
        )

    def handle(self, *args, **options):

        path = options["json_file"]

        with open(path, encoding="utf-8") as file:
            data = json.load(file)

        quizzes = data.get("quizzes", [])

        for quiz_data in quizzes:

            try:
                subject = Subject.objects.get(
                    code=quiz_data["subject_code"]
                )

            except Subject.DoesNotExist:

                self.stdout.write(
                    self.style.ERROR(
                        f"Subject '{quiz_data['subject_code']}' not found."
                    )
                )
                continue

            questions = quiz_data.pop("questions", [])

            quiz, created = Quiz.objects.get_or_create(
                subject=subject,
                title=quiz_data["title"],
                defaults={
                    "description": quiz_data.get("description", ""),
                    "total_marks": quiz_data.get("total_marks", 0),
                    "time_limit": quiz_data.get("time_limit"),
                    "is_active": quiz_data.get("is_active", True),
                    "is_paid": quiz_data.get("is_paid", False),
                }
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"{'Created' if created else 'Found'} Quiz: {quiz.title}"
                )
            )

            for question_data in questions:

                options = question_data.pop("options", [])

                question, created = Question.objects.get_or_create(
                    quiz=quiz,
                    question_text=question_data["question_text"],
                    defaults={
                        "marks": question_data.get("marks", 1),
                        "question_type": question_data.get(
                            "question_type",
                            "single"
                        ),
                    }
                )

                self.stdout.write(
                    f"   {'Created' if created else 'Found'} Question"
                )

                for option_data in options:

                    option, created = Option.objects.get_or_create(
                        question=question,
                        option_text=option_data["option_text"],
                        defaults={
                            "is_correct": option_data.get(
                                "is_correct",
                                False
                            )
                        }
                    )

                    self.stdout.write(
                        f"      {'Created' if created else 'Found'} Option"
                    )

        self.stdout.write(
            self.style.SUCCESS(
                "\nQuiz seeding completed successfully."
            )
        )

# Run
# python manage.py seed_quiz data/seedquiz.json