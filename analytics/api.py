# analytics/api.py
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response

from backend.models import Course

from .models import UserEvent

@api_view(["GET"])
def most_viewed_courses(request):
    # /api/analytics/most-viewed-courses/?days=30&limit=10
    days = int(request.GET.get("days", 30))
    limit = int(request.GET.get("limit", 10))
    since = timezone.now() - timedelta(days=days)

    qs = (
        UserEvent.objects.filter(
            item_type="course",
            action=UserEvent.VIEW,
            created_at__gte=since
        )
        .values("item_id")
        .annotate(views=Count("id"))
        .order_by("-views")[:limit]
    )

    # map course_id -> title
    ids = [row["item_id"] for row in qs]
    course_map = {c.id: c.name for c in Course.objects.filter(id__in=ids).only("id", "name")}

    data = []
    for row in qs:
        cid = row["item_id"]
        data.append({
            "course_id": cid,
            "name": course_map.get(cid, f"Course #{cid}"),
            "views": row["views"],
        })
    return Response(data)


@api_view(["GET"])
def daily_course_views(request):
    # /api/analytics/daily-course-views/?days=30
    days = int(request.GET.get("days", 30))
    since = timezone.now() - timedelta(days=days)

    events = UserEvent.objects.filter(
        item_type="course",
        action=UserEvent.VIEW,
        created_at__gte=since
    ).only("created_at")

    buckets = {}
    for e in events:
        d = e.created_at.date().isoformat()
        buckets[d] = buckets.get(d, 0) + 1

    data = [{"date": k, "views": buckets[k]} for k in sorted(buckets.keys())]
    return Response(data)
