from django.core.management.base import BaseCommand
from django.db import transaction

from analytics.models import UserEvent, AlsoViewedCourse


class Command(BaseCommand):
    help = "Build 'Students Also Viewed' recommendations using user interaction data"

    def add_arguments(self, parser):
        parser.add_argument("--topk", type=int, default=6)

    def handle(self, *args, **opts):
        topk = opts["topk"]

        # -------------------------------
        # Step 1: Collect user interactions
        # -------------------------------
        user_courses = {}

        events = UserEvent.objects.filter(
            item_type="course",
            action=UserEvent.VIEW,
            user__isnull=False
        ).values_list("user_id", "item_id")

        for user_id, course_id in events:

            if user_id not in user_courses:
                user_courses[user_id] = []

            if course_id not in user_courses[user_id]:
                user_courses[user_id].append(course_id)

        if not user_courses:
            self.stdout.write(self.style.ERROR("No user interaction data found."))
            return

        # -------------------------------
        # Step 2: Count co-viewed courses
        # -------------------------------
        pair_counts = {}

        for courses in user_courses.values():

            n = len(courses)

            if n < 2:
                continue

            for i in range(n):

                for j in range(i + 1, n):

                    a = courses[i]
                    b = courses[j]

                    # keep order consistent
                    if a > b:
                        a, b = b, a

                    pair = (a, b)

                    if pair not in pair_counts:
                        pair_counts[pair] = 0

                    pair_counts[pair] += 1

        if not pair_counts:
            self.stdout.write(
                self.style.ERROR("Not enough user interactions to build recommendations.")
            )
            return

        # -------------------------------
        # Step 3: Build recommendation list
        # -------------------------------
        recommendations = {}

        for (course_a, course_b), score in pair_counts.items():

            if course_a not in recommendations:
                recommendations[course_a] = []

            if course_b not in recommendations:
                recommendations[course_b] = []

            recommendations[course_a].append((course_b, score))
            recommendations[course_b].append((course_a, score))

        # -------------------------------
        # Step 4: Save recommendations
        # -------------------------------
        with transaction.atomic():

            AlsoViewedCourse.objects.all().delete()

            bulk = []

            for course_id, neighbors in recommendations.items():

                neighbors.sort(
                    key=lambda item: item[1],
                    reverse=True
                )

                for neighbor_id, score in neighbors[:topk]:

                    bulk.append(
                        AlsoViewedCourse(
                            course_id=course_id,
                            also_viewed_course_id=neighbor_id,
                            score=float(score)
                        )
                    )

            AlsoViewedCourse.objects.bulk_create(
                bulk,
                batch_size=500
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully generated 'Also Viewed' recommendations for {len(recommendations)} courses."
            )
        )

#Run
#python manage.py build_also_viewed