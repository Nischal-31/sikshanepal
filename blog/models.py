from django.db import models
from django.utils.text import slugify
from user.models import CustomUser

class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)  # For clean URLs
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    extra_details = models.TextField(blank=True, null=True)  # Only for Paid Users
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE,null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
