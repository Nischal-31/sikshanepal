from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    # API Overview
    path('', views.apiOverview, name="api-overview"),
    
    # User URLs
    path('user-list/', views.userList, name="user-list-api"),
    path('user-detail/<str:pk>/', views.userDetail, name="user-detail-api"),
    path('user-create/', views.userCreate, name="user-create-api"),
    path('user-update/<str:pk>/', views.userUpdate, name="user-update-api"),
    path('user-delete/<str:pk>/', views.userDelete, name="user-delete-api"),
    path('profile/', views.userProfile, name='user-profile-api'),
    path('api/token/', obtain_auth_token, name='api_token_auth'),

    path('password-reset/', views.password_reset_request, name='password_reset_api'),
    path('password-reset-confirm/', views.password_reset_confirm, name='password_reset_confirm_api'),
    path('change-password/', views.change_password, name='change_password_api'),

    # Course URLs
    path('course-list/', views.courseList, name="course-list-api"),
    path('course-detail/<int:pk>/', views.courseDetail, name="course-detail-api"),
    path('course-create/', views.courseCreate, name="course-create-api"),
    path('course-update/<int:pk>/', views.courseUpdate, name="course-update-api"),
    path('course-delete/<int:pk>/', views.courseDelete, name="course-delete-api"),
    
    # Semester URLs
    path('semester-list/', views.semesterList, name="semester-list-api"),
    path('semester-list/<int:course_id>/', views.semesterListByCourse, name="semester-list-by-course-api"),  # List semesters by course ID
    path('semester-detail/<int:pk>/', views.semesterDetail, name="semester-detail-api"),
    path('semester-create/<int:course_id>/', views.semesterCreate, name="semester-create-api"),
    path('semester-update/<int:pk>/', views.semesterUpdate, name="semester-update-api"),
    path('semester-delete/<int:pk>/', views.semesterDelete, name="semester-delete-api"),

    # Subject URLs
    path('subject-list/', views.subjectList, name="subject-list-api"),
    path('subject-list/<int:semester_id>/', views.subjectListBySemester, name="subject-list-by-semester-api"),  # List subjects by semester ID
    path('subject-detail/<int:pk>/', views.subjectDetail, name="subject-detail-api"),
    path('subject-create/<int:semester_id>/', views.subjectCreate, name="subject-create-api"),
    path('subject-update/<int:pk>/', views.subjectUpdate, name="subject-update-api"),
    path('subject-delete/<int:pk>/', views.subjectDelete, name="subject-delete-api"),
    
     # PastQuestions URLs
    path('pastQuestion-list/', views.pastQuestionList, name="pastQuestion-list-api"),
    path('pastQuestion-list/<int:subject_id>/', views.pastQuestionListBySubject, name="pastQuestion-list-by-subject-api"),  # List oldQuestions by subject ID
    path('pastQuestion-detail/<int:pk>/', views.pastQuestionDetail, name="pastQuestion-detail-api"),
    path('pastQuestion-create/<int:subject_id>/', views.pastQuestionCreate, name="pastQuestion-create-api"),
    path('pastQuestion-update/<int:pk>/', views.pastQuestionUpdate, name="pastQuestion-update-api"),
    path('pastQuestion-delete/<int:pk>/', views.pastQuestionDelete, name="pastQuestion-delete-api"),
    

    # Syllabus URLs
    path('syllabus-list/', views.syllabusList, name="syllabus-list-api"),
    path('syllabus-list/<int:subject_id>/', views.syllabusListBySubject, name="syllabus-list-by-subject-api"),  # List syllabus by subject ID
    path('syllabus-detail/<int:pk>/', views.syllabusDetail, name="syllabus-detail-api"),
    path('syllabus-create/<int:subject_id>/', views.syllabusCreate, name="syllabus-create-api"),
    path('syllabus-update/<int:pk>/', views.syllabusUpdate, name="syllabus-update-api"),
    path('syllabus-delete/<int:pk>/', views.syllabusDelete, name="syllabus-delete-api"),

    # Chapter URLs
    path('chapter-list/', views.chapterList, name="chapter-list-api"),
    path('chapter-list/<int:subject_id>/', views.chapterListBySubject, name="chapter-list-by-subject-api"),  # List chapter by subject ID
    path('chapter-detail/<int:pk>/', views.chapterDetail, name="chapter-detail-api"),
    path('chapter-create/<int:subject_id>/', views.chapterCreate, name="chapter-create-api"),
    path('chapter-update/<int:pk>/', views.chapterUpdate, name="chapter-update-api"),
    path('chapter-delete/<int:pk>/', views.chapterDelete, name="chapter-delete-api"),
    
    # Notes URLs
    path('note-list/', views.noteList, name="note-list-api"),
    path('note-list/<int:chapter_id>/', views.noteListByChapter, name="note-list-by-chapter-api"),  # List note by chapter ID
    path('note-detail/<int:pk>/', views.noteDetail, name="note-detail-api"),
    path('note-create/<int:chapter_id>/', views.noteCreate, name="note-create-api"),
    path('note-update/<int:pk>/', views.noteUpdate, name="note-update-api"),
    path('note-delete/<int:pk>/', views.noteDelete, name="note-delete-api"),
    
]
