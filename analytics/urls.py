# analytics/urls.py
from django.urls import path

from .views import analytics_dashboard
from .api import most_viewed_courses, daily_course_views

urlpatterns = [
    # page
    path("analytics-dashboard/", analytics_dashboard, name="analytics-dashboard"),

    #APIs
    path("api/analytics/most-viewed-courses/", most_viewed_courses),
    path("api/analytics/daily-course-views/", daily_course_views),
]