from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
import requests

# Import custom recommendation algorithms
from analytics.recommendation.tfidf import compute_tfidf
from analytics.recommendation.cosine import similarity_matrix

# Import recommendation model
from analytics.models import SimilarCourse


class Command(BaseCommand):
    """
    Build content-based course recommendations using
    TF-IDF Vectorization and Cosine Similarity.
    """

    help = "Build content-based recommendations using TF-IDF + Cosine Similarity"

    def add_arguments(self, parser):
        # Number of similar courses to store for each course
        parser.add_argument("--topk", type=int, default=10)

    def handle(self, *args, **opts):

        topk = opts["topk"]

        # --------------------------------------------------------
        # Step 1: Fetch course data from the backend API
        # --------------------------------------------------------

        base = getattr(settings, "BACKEND_BASE_URL", "http://127.0.0.1:8000")
        url = f"{base}/backend/course-list/"

        token = getattr(settings, "RECO_SERVICE_TOKEN", "")

        if not token:
            self.stdout.write(
                self.style.ERROR("RECO_SERVICE_TOKEN not set in settings.py")
            )
            return

        headers = {
            "Authorization": f"Token {token}"
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            self.stdout.write(
                self.style.ERROR(
                    f"Failed to fetch courses: {response.status_code}"
                )
            )
            self.stdout.write(response.text[:300])
            return

        courses = response.json()

        self.stdout.write(f"Fetched {len(courses)} courses.")

        if len(courses) < 2:
            self.stdout.write(
                self.style.ERROR(
                    "Not enough courses available to build recommendations."
                )
            )
            return

        # --------------------------------------------------------
        # Step 2: Prepare course IDs and text documents
        # --------------------------------------------------------

        ids = []
        texts = []

        for course in courses:

            course_id = course.get("id")
            name = (course.get("name") or "").strip()
            description = (course.get("description") or "").strip()

            # Skip courses without an ID
            if not course_id:
                continue

            # Use course title if description is empty
            if not description:
                description = name

            ids.append(course_id)

            # Combine title and description into one document
            texts.append(f"{name}. {description}")

        self.stdout.write(f"Valid courses processed: {len(ids)}")

        if len(texts) < 2:
            self.stdout.write(
                self.style.ERROR(
                    "At least two valid courses are required."
                )
            )
            return

        # --------------------------------------------------------
        # Step 3: Generate TF-IDF vectors
        # Each course description is converted into a numerical
        # vector based on term importance.
        # --------------------------------------------------------

        vectors = compute_tfidf(texts)

        # --------------------------------------------------------
        # Step 4: Calculate Cosine Similarity
        # Compare every course vector with every other course
        # to measure content similarity.
        # --------------------------------------------------------

        sim = similarity_matrix(vectors)

        self.stdout.write(
            f"Similarity Matrix Size: {len(sim)} x {len(sim[0])}"
        )

        if len(sim) != len(ids):
            self.stdout.write(
                self.style.ERROR(
                    f"Mismatch: similarity rows={len(sim)}, course ids={len(ids)}"
                )
            )
            return

        # --------------------------------------------------------
        # Step 5: Store the most similar courses
        # --------------------------------------------------------

        with transaction.atomic():

            # Remove previous recommendations
            SimilarCourse.objects.all().delete()

            recommendations = []

            # Process every course
            for i, course_id in enumerate(ids):

                # Rank courses by similarity score
                ranked = sorted(
                    range(len(sim[i])),
                    key=lambda j: sim[i][j],
                    reverse=True
                )

                count = 0

                for j in ranked:

                    # Skip comparing a course with itself
                    if ids[j] == course_id:
                        continue

                    recommendations.append(

                        SimilarCourse(
                            course_id=course_id,
                            similar_course_id=ids[j],
                            score=round(float(sim[i][j]), 6)
                        )

                    )

                    count += 1

                    # Save only Top-K recommendations
                    if count >= topk:
                        break

            # Store recommendations efficiently
            SimilarCourse.objects.bulk_create(
                recommendations,
                batch_size=500
            )

        # --------------------------------------------------------
        # Step 6: Display completion message
        # --------------------------------------------------------

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully generated recommendations for {len(ids)} courses."
            )
        )

#Run
#python manage.py build_content_reco