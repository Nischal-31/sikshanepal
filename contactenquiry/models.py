from django.db import models

# Create your models here.
class contactEnquiry(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('done', 'Done'),
    ]

    name=models.CharField(max_length=20)
    email=models.CharField(max_length=40)
    subject=models.CharField(max_length=40)
    message=models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
