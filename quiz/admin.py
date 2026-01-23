from django.contrib import admin
from .models import Quiz, Question, Option, QuizAttempt

class OptionInline(admin.TabularInline):
    model = Option
    extra = 4  # default 4 options per question

class QuestionAdmin(admin.ModelAdmin):
    inlines = [OptionInline]
    list_display = ('question_text', 'quiz', 'marks', 'question_type')
    list_filter = ('quiz', 'question_type')

class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'total_marks', 'time_limit', 'is_active', 'is_paid')
    list_filter = ('subject', 'is_active', 'is_paid')

class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'quiz',
        'score',
        'submitted_at',
    )

    list_filter = (
        'quiz',
        'submitted_at',
    )

    search_fields = (
        'user__username',
        'user__email',
        'quiz__title',
    )

    ordering = (
        '-submitted_at',
    )

    readonly_fields = (
        'submitted_at',
    )

    list_per_page = 25

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuizAttempt,QuizAttemptAdmin)
