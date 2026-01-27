from collections import defaultdict
from itertools import combinations

from django.core.management.base import BaseCommand
from django.db import transaction

from analytics.models import UserEvent, AlsoViewedCourse

class Command(BaseCommand):
    help = "Build 'students also viewed' recommendations from UserEvent view logs"

    def add_arguments(self, parser):
        parser.add_argument("--topk", type=int, default=6)

    def handle(self, *args, **opts):
        topk = opts["topk"]

        # user_id -> set(course_ids)
        user_courses = defaultdict(set)

        qs = UserEvent.objects.filter(
            item_type="course",
            action=UserEvent.VIEW,
            user__isnull=False
        ).values_list("user_id", "item_id")

        for user_id, course_id in qs:
            user_courses[user_id].add(course_id)

        if not user_courses:
            self.stdout.write(self.style.ERROR("No user view data found yet."))
            return

        # pair (a,b) -> count
        pair_counts = defaultdict(int)

        for _, courses in user_courses.items():
            # only pairs if user viewed 2+ courses
            if len(courses) < 2:
                continue
            for a, b in combinations(sorted(courses), 2):
                pair_counts[(a, b)] += 1

        if not pair_counts:
            self.stdout.write(self.style.ERROR("Not enough multi-course views to build pairs."))
            return

        # Build per-course recommendations
        per_course = defaultdict(list)
        for (a, b), count in pair_counts.items():
            per_course[a].append((b, count))
            per_course[b].append((a, count))

        with transaction.atomic():
            AlsoViewedCourse.objects.all().delete()

            bulk = []
            for course_id, neighbors in per_course.items():
                neighbors.sort(key=lambda x: x[1], reverse=True)
                for also_id, count in neighbors[:topk]:
                    bulk.append(AlsoViewedCourse(
                        course_id=course_id,
                        also_viewed_course_id=also_id,
                        score=float(count)  # score = co-view count
                    ))

            AlsoViewedCourse.objects.bulk_create(bulk, batch_size=500)

        self.stdout.write(self.style.SUCCESS("✅ Built 'also viewed' recommendations successfully."))
