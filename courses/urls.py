# courses/urls.py
from django.urls import path
from . import views

urlpatterns = [

# Course URLs

    path('course-list/', views.course_list_view, name='course-list'),
    path('course-detail/<str:course_id>/', views.course_detail_view, name='course-detail'),
    path('course-create/', views.course_create_view, name='course-create'),
    path('course-update/<str:course_id>/', views.course_update_view, name='course-update'),
    path('course-delete/<str:course_id>/', views.course_delete_view, name='course-delete'),
    
# Semester URLs

    path('semester-list/<int:course_id>', views.semester_list_view, name='semester-list'),
    path('semester-detail/<str:semester_id>/', views.semester_detail_view, name='semester-detail'),
    path('semester-create/<int:course_id>', views.semester_create_view, name='semester-create'),
    path('semester-update/<str:semester_id>/', views.semester_update_view, name='semester-update'),
    path('semester-delete/<str:semester_id>/', views.semester_delete_view, name='semester-delete'),
    
# Subject URLs

    path('subject-list/<int:semester_id>', views.subject_list_view, name='subject-list'),
    path('subject-detail/<str:subject_id>/', views.subject_detail_view, name='subject-detail'),
    path('subject-create/<int:semester_id>', views.subject_create_view, name='subject-create'),
    path('subject-update/<str:subject_id>/', views.subject_update_view, name='subject-update'),
    path('subject-delete/<str:subject_id>/', views.subject_delete_view, name='subject-delete'),

# Past Question URLs

    path('pastQuestion-list/<int:subject_id>/', views.pastQuestion_list_view, name='pastQuestion-list'),
    path('pastQuestion-detail/<str:pastQuestion_id>/', views.pastQuestion_detail_view, name='pastQuestion-detail'),
    path('pastQuestion-create/<int:subject_id>/', views.pastQuestion_create_view, name='pastQuestion-create'),
    path('pastQuestion-update/<str:pastQuestion_id>/', views.pastQuestion_update_view, name='pastQuestion-update'),
    path('pastQuestion-delete/<str:pastQuestion_id>/', views.pastQuestion_delete_view, name='pastQuestion-delete'),

# Syllabus URLs

    path('syllabus-list/<int:subject_id>', views.syllabus_list_view, name='syllabus-list'),
    path('syllabus-detail/<str:syllabus_id>/', views.syllabus_detail_view, name='syllabus-detail'),
    path('syllabus-create/<int:subject_id>', views.syllabus_create_view, name='syllabus-create'),
    path('syllabus-update/<str:syllabus_id>/', views.syllabus_update_view, name='syllabus-update'),
    path('syllabus-delete/<str:syllabus_id>/', views.syllabus_delete_view, name='syllabus-delete'),

# Chapter URLs   

    path('chapter-list/<int:subject_id>', views.chapter_list_view, name='chapter-list'),
    path('chapter-detail/<str:chapter_id>/', views.chapter_detail_view, name='chapter-detail'),
    path('chapter-create/<int:subject_id>', views.chapter_create_view, name='chapter-create'),
    path('chapter-update/<str:chapter_id>/', views.chapter_update_view, name='chapter-update'),
    path('chapter-delete/<str:chapter_id>/', views.chapter_delete_view, name='chapter-delete'),

# Note URLs

    path('note-list/<int:chapter_id>', views.note_list_view, name='note-list'),
    path('note-detail/<str:note_id>/', views.note_detail_view, name='note-detail'),
    path('note-create/<int:chapter_id>', views.note_create_view, name='note-create'),
    path('note-update/<str:note_id>/', views.note_update_view, name='note-update'),
    path('note-delete/<str:note_id>/', views.note_delete_view, name='note-delete'),

]
