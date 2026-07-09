from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_no = models.CharField(max_length=20)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    terms_agree = models.BooleanField(default=False)
    remember_me = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    # Define the roles for users
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('student', 'Student'),
        ('instructor', 'Instructor'),
    ]
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    
    def __str__(self):
        return self.username
    
    # Methods to check user type
    @property
    def is_admin_user(self):
        return self.user_type == 'admin'

    @property
    def is_student_user(self):
        return self.user_type == 'student'
    
    @property
    def is_instructor_user(self):
        return self.user_type == 'instructor'

    def save(self, *args, **kwargs):
        # If the user is a superuser, set user_type to 'admin'
        if self.is_superuser and self.user_type != 'admin':
            self.user_type = 'admin'
        super().save(*args, **kwargs)
    
