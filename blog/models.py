from django.db import models
from django.utils.text import slugify
from user.models import CustomUser

class Post(models.Model):
    CATEGORY_CHOICES = [
        ("tech", "Technology"),
        ("sports", "Sports"),
        ("education", "Education"),
        ("lifestyle", "Lifestyle"),
        ("news", "News"),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES,default='tech')
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    extra_details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"