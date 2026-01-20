# quiz/urls.py
from django.urls import path
from . import views

app_name = "quiz"

urlpatterns = [
    path("subject/<int:subject_id>/", views.subject_quizzes, name="subject_quizzes"),
    path("quiz/<int:quiz_id>/attempt/", views.attempt_quiz, name="attempt_quiz"),
    path("quiz/<int:quiz_id>/result/", views.quiz_result, name="quiz_result"),
    path("subject/<int:subject_id>/create/", views.quiz_create, name="quiz_create"), 
    path("quiz/<int:quiz_id>/add-question/", views.add_question, name="add_question"),
    path("quiz/<int:quiz_id>/edit/", views.quiz_edit, name="quiz_edit"),
    path("quiz/<int:quiz_id>/delete/", views.quiz_delete, name="quiz_delete"),


]
