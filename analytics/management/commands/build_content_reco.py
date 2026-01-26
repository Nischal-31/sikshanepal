from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
import requests

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from analytics.models import SimilarCourse

class Command(BaseCommand):
    help = "Build content-based recommendations using TF-IDF + Cosine Similarity"

    def add_arguments(self, parser):
        parser.add_argument("--topk", type=int, default=10)

    def handle(self, *args, **opts):
        topk = opts["topk"]

        # ✅ your backend API endpoint
        base = getattr(settings, "BACKEND_BASE_URL", "http://127.0.0.1:8000")
        url = f"{base}/backend/course-list/"

        token = getattr(settings, "RECO_SERVICE_TOKEN", "")
        if not token:
            self.stdout.write(self.style.ERROR("RECO_SERVICE_TOKEN not set in settings.py"))
            return

        headers = {"Authorization": f"Token {token}"}
        r = requests.get(url, headers=headers)

        if r.status_code != 200:
            self.stdout.write(self.style.ERROR(f"Failed to fetch courses: {r.status_code}"))
            self.stdout.write(r.text[:300])
            return

        courses = r.json()
        self.stdout.write(f"type(courses) = {type(courses)}")
        try:
            self.stdout.write(f"len(courses) = {len(courses)}")
        except Exception:
            pass
        self.stdout.write(str(courses)[:300])

        if len(courses) < 2:
            self.stdout.write("Not enough courses to build recommendations.")
            return

        # ✅ your fields: name + description
        # ✅ build ids + texts safely
        ids = []
        texts = []

        for c in courses:
            cid = c.get("id")
            name = (c.get("name") or "").strip()
            desc = (c.get("description") or "").strip()

            if not cid:
                continue

            if not desc:
                desc = name

            ids.append(cid)
            texts.append(f"{name}. {desc}")

        self.stdout.write(f"ids={len(ids)} texts={len(texts)}")
        if len(texts) < 2:
            self.stdout.write(self.style.ERROR("Need at least 2 courses with text to compute similarity."))
            return

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            token_pattern=r"(?u)\b[a-zA-Z0-9][a-zA-Z0-9\-\_]+\b"
        )

        X = vectorizer.fit_transform(texts)
        sim = cosine_similarity(X)

        self.stdout.write(f"sim shape = {sim.shape}")
        if sim.shape[0] != len(ids):
            self.stdout.write(self.style.ERROR(f"Mismatch: sim rows={sim.shape[0]} ids={len(ids)}"))
            return

        with transaction.atomic():
            SimilarCourse.objects.all().delete()

            bulk = []
            for i, course_id in enumerate(ids):
                best = sim[i].argsort()[::-1]
                added = 0
                for j in best:
                    if ids[j] == course_id:
                        continue
                    bulk.append(SimilarCourse(
                        course_id=course_id,
                        similar_course_id=ids[j],
                        score=float(sim[i][j]),
                    ))
                    added += 1
                    if added >= topk:
                        break

            SimilarCourse.objects.bulk_create(bulk, batch_size=500)

        self.stdout.write(self.style.SUCCESS(f"✅ Built TF-IDF recommendations for {len(ids)} courses."))
