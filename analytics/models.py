# analytics/models.py
from django.conf import settings
from django.db import models

class UserEvent(models.Model):
    VIEW = "view"
    ENROLL = "enroll"
    DOWNLOAD = "download"
    CLICK_REC = "click_recommendation"

    ACTION_CHOICES = [
        (VIEW, "View"),
        (ENROLL, "Enroll"),
        (DOWNLOAD, "Download"),
        (CLICK_REC, "Click Recommendation"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )

    # Generic target (course/subject/note) without complex generic relations:
    item_type = models.CharField(max_length=30)   # "course" / "subject" / "note"
    item_id = models.PositiveIntegerField()

    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    # useful metadata
    session_key = models.CharField(max_length=64, blank=True, default="")
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        indexes = [
            models.Index(fields=["item_type", "item_id", "action"]),
            models.Index(fields=["user", "action", "created_at"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.user_id} {self.action} {self.item_type}:{self.item_id}"
    
class SimilarCourse(models.Model):
    course_id = models.PositiveIntegerField(db_index=True)
    similar_course_id = models.PositiveIntegerField(db_index=True)
    score = models.FloatField()

    class Meta:
        unique_together = ("course_id", "similar_course_id")
        indexes = [
            models.Index(fields=["course_id", "-score"]),
        ]
