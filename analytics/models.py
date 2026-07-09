from django.conf import settings
from django.db import models

from backend.models import Course   # Adjust import if your Course model is elsewhere


class UserEvent(models.Model):
    """
    Stores user interactions with learning resources.
    Used for analytics and recommendation generation.
    """

    VIEW = "view"
    ENROLL = "enroll"
    DOWNLOAD = "download"
    CLICK_RECOMMENDATION = "click_recommendation"

    ACTION_CHOICES = [
        (VIEW, "View"),
        (ENROLL, "Enroll"),
        (DOWNLOAD, "Download"),
        (CLICK_RECOMMENDATION, "Click Recommendation"),
    ]

    ITEM_CHOICES = [
        ("course", "Course"),
        ("subject", "Subject"),
        ("note", "Note"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_events",
    )

    item_type = models.CharField(
        max_length=20,
        choices=ITEM_CHOICES
    )

    item_id = models.PositiveIntegerField()

    action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES
    )

    created_at = models.DateTimeField(auto_now_add=True)

    session_key = models.CharField(
        max_length=64,
        blank=True
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    user_agent = models.CharField(
        max_length=255,
        blank=True
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["user", "action"]),
            models.Index(fields=["item_type", "item_id"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"{username} - {self.action} ({self.item_type})"


class SimilarCourse(models.Model):
    """
    Stores content-based recommendations generated
    using TF-IDF and Cosine Similarity.
    """

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="similar_courses"
    )

    similar_course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="recommended_for"
    )

    score = models.FloatField()

    class Meta:
        unique_together = ("course", "similar_course")

        ordering = ["-score"]

        indexes = [
            models.Index(fields=["course"]),
        ]

    def __str__(self):
        return f"{self.course.name} → {self.similar_course.name} ({self.score:.3f})"


class AlsoViewedCourse(models.Model):
    """
    Stores collaborative filtering recommendations
    based on user viewing behaviour.
    """

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="also_viewed"
    )

    also_viewed_course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="viewed_with"
    )

    score = models.FloatField(default=0.0)

    class Meta:
        unique_together = ("course", "also_viewed_course")

        ordering = ["-score"]

        indexes = [
            models.Index(fields=["course"]),
        ]

    def __str__(self):
        return f"{self.course.name} → {self.also_viewed_course.name} ({self.score})"