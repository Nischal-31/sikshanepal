from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render,get_object_or_404
from backend.models import Subject
from quiz.forms import QuizForm
from quiz.models import Option, Question, Quiz, QuizAttempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django import forms

def is_admin(user):
    return getattr(user, "user_type", None) == "admin"

#-------------------------------------------------------------------------------------------------------------------------------------------------------------
# Quiz Logic
#-------------------------------------------------------------------------------------------------------------------------------------------------------------

def subject_quizzes(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    quizzes = subject.quizzes.filter(is_active=True)
    return render(request, "quiz/subject_quizzes.html", {
        "subject": subject,
        "quizzes": quizzes
    })

def attempt_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if request.method == "POST":
        score = 0
        for question in quiz.questions.all():
            selected_option_id = request.POST.get(str(question.id))
            if selected_option_id and question.options.filter(id=selected_option_id, is_correct=True).exists():
                score += question.marks

        QuizAttempt.objects.update_or_create(
            user=request.user,
            quiz=quiz,
            defaults={"score": score}
        )
        return redirect("quiz:quiz_result", quiz_id=quiz.id)

    return render(request, "quiz/attempt_quiz.html", {"quiz": quiz})

def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempt = get_object_or_404(QuizAttempt, user=request.user, quiz=quiz)
    
    # Calculate percentage safely
    if quiz.total_marks > 0:
        percentage = round((attempt.score / quiz.total_marks) * 100, 2)
        passed = attempt.score >= (quiz.total_marks / 2)  # Pass if >= 50%
    else:
        percentage = 0
        passed = False

    return render(request, "quiz/quiz_result.html", {
        "quiz": quiz,
        "attempt": attempt,
        "percentage": percentage,
        "passed": passed
    })

#--------------------------------------------------------------------------------------------------------------------------
# Quiz CRUD
#-----------------------------------------------------------------------------------------------------------------------------------

@login_required
@user_passes_test(is_admin)
def quiz_create(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)

    if request.method == "POST":
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.subject = subject   # IMPORTANT
            quiz.save()
            return redirect("quiz:subject_quizzes", subject_id=subject.id)
    else:
        form = QuizForm()

    return render(request, "quiz/quiz_create.html", {
        "form": form,
        "subject": subject
    })


@login_required
@user_passes_test(is_admin)
def quiz_edit(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == "POST":
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            return redirect("quiz:subject_quizzes", subject_id=quiz.subject.id)
    else:
        form = QuizForm(instance=quiz)

    return render(request, "quiz/quiz_edit.html", {"form": form, "quiz": quiz})


@login_required
@user_passes_test(is_admin)
def quiz_delete(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    subject_id = quiz.subject.id
    if request.method == "POST":
        quiz.delete()
        return redirect("quiz:subject_quizzes", subject_id=subject_id)

    return render(request, "quiz/quiz_delete_confirm.html", {"quiz": quiz})

#--------------------------------------------------------------------------------------------------------------------------------------------------------------
# Question CRUD
#--------------------------------------------------------------------------------------------------------------------------------------------------------------

def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == "POST":
        question_text = request.POST.get("question_text")
        marks = int(request.POST.get("marks") or 1)
        question = Question.objects.create(quiz=quiz, question_text=question_text, marks=marks)

        # Handle options dynamically (MCQs)
        options = request.POST.getlist("option_text[]")
        correct_index = int(request.POST.get("correct_option"))  # which option is correct

        for idx, text in enumerate(options):
            Option.objects.create(question=question, option_text=text, is_correct=(idx == correct_index))

        return redirect("quiz:add_question", quiz_id=quiz.id)

    return render(request, "quiz/add_question.html", {"quiz": quiz})

@login_required
@user_passes_test(is_admin)
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    quiz = question.quiz
    options = question.options.all()

    if request.method == "POST":
        # Update question text and marks
        question.question_text = request.POST.get("question_text")
        question.marks = int(request.POST.get("marks") or 1)
        question.save()

        # Update options
        option_texts = request.POST.getlist("option_text[]")
        correct_index = int(request.POST.get("correct_option"))

        # Delete old options and recreate
        question.options.all().delete()
        for idx, text in enumerate(option_texts):
            Option.objects.create(
                question=question,
                option_text=text,
                is_correct=(idx == correct_index)
            )

        return redirect("quiz:add_question", quiz_id=quiz.id)  # Redirect to quiz question page

    return render(request, "quiz/edit_question.html", {
        "quiz": quiz,
        "question": question,
        "options": options
    })

@login_required
@user_passes_test(is_admin)
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    quiz_id = question.quiz.id

    if request.method == "POST":
        question.delete()
        return redirect("quiz:add_question", quiz_id=quiz_id)

    return render(request, "quiz/delete_question.html", {
        "question": question
    })


def edit_option(request, option_id):
    option = get_object_or_404(Option, id=option_id)
    if request.method == "POST":
        option.option_text = request.POST.get("option_text")
        option.is_correct = "is_correct" in request.POST
        option.save()
        return redirect("quiz:add_question", quiz_id=option.question.quiz.id)
    return render(request, "quiz/edit_option.html", {"option": option})

def delete_option(request, option_id):
    option = get_object_or_404(Option, id=option_id)
    quiz_id = option.question.quiz.id
    option.delete()
    return redirect("quiz:add_question", quiz_id=quiz_id)
