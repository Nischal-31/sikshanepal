from django.db import models

from backend.models import Subject
from user.models import CustomUser

class Quiz(models.Model):
    subject=models.ForeignKey(Subject,on_delete=models.CASCADE,related_name="quizzes")
    title=models.CharField(max_length=200)
    description=models.TextField(blank=True)
    total_marks=models.IntegerField(default=0)
    time_limit=models.IntegerField(null=True,blank=True,help_text="Minutes")
    is_active=models.BooleanField(default=True)
    is_paid=models.BooleanField(default=False)#For premium quizzes

    def __str__(self):
        return f"{self.subject.name} - {self.title}"
    
class Question(models.Model):
    QUESTION_TYPES=[
        ('single','Single Choice'),
        ('multiple','Multiple Choice'),
        ('tf','True/False'),
    ]
    quiz=models.ForeignKey(Quiz,on_delete=models.CASCADE,related_name="questions")
    question_text=models.TextField()
    marks=models.IntegerField(default=1)
    question_type=models.CharField(max_length=10,choices=QUESTION_TYPES,default='single')

    def __str__(self):
        return self.question_text[:50]

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    option_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.option_text
    
class QuizAttempt(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'quiz')