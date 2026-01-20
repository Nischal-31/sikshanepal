from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render,get_object_or_404
from backend.models import Subject
from quiz.models import Option, Question, Quiz, QuizAttempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django import forms

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


def is_admin(user):
    return getattr(user, "user_type", None) == "admin"

@login_required
@user_passes_test(is_admin)
def quiz_create(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)

    if request.method == "POST":
        title = request.POST.get("title")
        total_marks = request.POST.get("total_marks") or 0
        time_limit = request.POST.get("time_limit") or None
        is_active = request.POST.get("is_active") == "on"
        quiz = Quiz.objects.create(
            subject=subject,
            title=title,
            total_marks=total_marks,
            time_limit=time_limit,
            is_active=is_active
        )
        return redirect("quiz:subject_quizzes", subject_id=subject.id)

    return render(request, "quiz/quiz_create.html", {"subject": subject})

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

# ---------------- Edit Quiz ----------------
class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'total_marks', 'time_limit', 'is_active']

@login_required
@user_passes_test(is_admin)
def quiz_edit(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == "POST":
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            return redirect("quiz:subject-quizzes", subject_id=quiz.subject.id)
    else:
        form = QuizForm(instance=quiz)

    return render(request, "quiz/quiz_edit.html", {"form": form, "quiz": quiz})

# ---------------- Delete Quiz ----------------
@login_required
@user_passes_test(is_admin)
def quiz_delete(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    subject_id = quiz.subject.id
    if request.method == "POST":
        quiz.delete()
        return redirect("quiz:subject-quizzes", subject_id=subject_id)

    return render(request, "quiz/quiz_delete_confirm.html", {"quiz": quiz})