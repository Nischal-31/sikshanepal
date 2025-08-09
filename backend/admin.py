from django.contrib import admin
from .models import Course, Semester, Subject, PastQuestion, Syllabus, Chapter, Note

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)
    ordering = ('id',)

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'number', 'description')
    list_filter = ('course', 'number')
    search_fields = ('course__name', 'number')
    ordering = ('id',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'credits', 'semester')
    list_filter = ('semester',)
    search_fields = ('name', 'code')
    ordering = ('id',)

@admin.register(PastQuestion)
class PastQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'year', 'subject')
    list_filter = ('year', 'subject')
    search_fields = ('title', 'subject__name')
    ordering = ('id',)

@admin.register(Syllabus)
class SyllabusAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject')
    search_fields = ('subject__name',)
    ordering = ('id',)

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'subject', 'order')
    list_filter = ('subject',)
    search_fields = ('title', 'subject__name')
    ordering = ('order',)

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'chapter')
    list_filter = ('chapter',)
    search_fields = ('title', 'chapter__title')
    ordering = ('id',)
