# quiz/urls.py
from django.urls import path
from . import views

app_name = "quiz"

urlpatterns = [
    path("subject/<int:subject_id>/", views.subject_quizzes, name="subject_quizzes"),
    path("quiz/<int:quiz_id>/attempt/", views.attempt_quiz, name="attempt_quiz"),
    path("quiz/<int:quiz_id>/result/", views.quiz_result, name="quiz_result"),
    path("subject/<int:subject_id>/create/", views.quiz_create, name="quiz_create"), 
    path("quiz/<int:quiz_id>/edit/", views.quiz_edit, name="quiz_edit"),
    path("quiz/<int:quiz_id>/delete/", views.quiz_delete, name="quiz_delete"),

    path("quiz/<int:quiz_id>/add-question/", views.add_question, name="add_question"),
    path("question/<int:question_id>/edit/", views.edit_question, name="edit_question"),
    path("question/<int:question_id>/delete/", views.delete_question, name="delete_question"),

    # Option
    path("option/<int:option_id>/edit/", views.edit_option, name="edit_option"),
    path("option/<int:option_id>/delete/", views.delete_option, name="delete_option"),
    
]
