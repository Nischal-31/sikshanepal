from django.contrib import admin
from .models import UserEvent, SimilarCourse

@admin.register(UserEvent)
class UserEventAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "action", "item_type", "item_id", "created_at")
    list_filter = ("action", "item_type", "created_at")
    search_fields = ("user__username", "item_type", "item_id", "session_key")
    ordering = ("-created_at",)

@admin.register(SimilarCourse)
class SimilarCourseAdmin(admin.ModelAdmin):
    list_display = ("course_id", "similar_course_id", "score")
    list_filter = ("course_id",)
    ordering = ("-score",)

    @admin.display(description="Score")
    def score_4dp(self, obj):
        return f"{obj.score:.4f}"
