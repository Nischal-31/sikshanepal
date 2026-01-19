from django.urls import path
from .views import dashboard_home
from . import views
from user import views as user_views

urlpatterns=[
    path('',views.dashboard_home,name='home'),

    ## Course Management URLs
    path('courses/',views.manage_courses,name='courses'),
    path('course-detail/<str:course_id>/', views.dashboard_course_detail_view, name='dashboard_course_detail'),
    path('course-create/', views.dashboard_course_create_view, name='dashboard_course_create'),
    path('course-update/<str:course_id>/', views.dashboard_course_update_view, name='dashboard_course_update'),
    path('course-delete/<str:course_id>/', views.dashboard_course_delete_view, name='dashboard_course_delete'),

    ## Semester Management URLs
    path('course/<str:course_id>/semesters/', views.dashboard_semester_list_view, name='dashboard_manage_semesters'),
    path('semester-detail/<str:semester_id>/', views.dashboard_semester_detail_view, name='dashboard_semester_detail'),
    path('semester-create/<int:course_id>', views.dashboard_semester_create_view, name='dashboard_semester_create'),
    path('semester-update/<str:semester_id>/', views.dashboard_semester_update_view, name='dashboard_semester_update'),
    path('semester-delete/<str:semester_id>/', views.dashboard_semester_delete_view, name='dashboard_semester_delete'),

    ## Subject Management URLs
    path('semester/<str:semester_id>/subjects/', views.dashboard_subject_list_view, name='dashboard_manage_subjects'),
    path('subject-detail/<str:subject_id>/', views.dashboard_subject_detail_view, name='dashboard_subject_detail'),

    ## User Management URLs
    path('users/',views.manage_users,name='users'),
    path('users/<int:user_id>/profile/', user_views.admin_view_user_profile, name='admin_view_user_profile'),
    path('users/<int:user_id>/edit/', user_views.edit_user, name='edit_user'),
    path('users/<int:user_id>/delete/', user_views.delete_user, name='delete_user'),
    path('users/add/', user_views.add_user, name='add_user'),

    ## Contact Enquiry Management URLs
    path('enquiries/',views.manage_enquiries,name='enquiries'),
    path('enquiries/<int:id>/detail/', views.dashboard_contact_detail, name='dashboard_contact_detail'),
    path('enquiries/<int:id>/delete/', views.dashboard_contact_delete, name='dashboard_contact_delete'),
    path('enquiries/<int:id>/change_status/<str:new_status>/', views.dashboard_contact_change_status, name='dashboard_contact_change_status'),

    # Blog Management URLs
    path('blogs/',views.manage_blogs,name='blogs'),
    path('blogs/<int:id>/', views.dashboard_blog_detail, name='dashboard_blog_detail'),
    path('blogs/add/', views.dashboard_blog_add, name='dashboard_blog_add'),
    path('blogs/<int:id>/edit/', views.dashboard_blog_edit, name='dashboard_blog_edit'),
    path('blogs/<int:id>/delete/', views.dashboard_blog_delete, name='dashboard_blog_delete'),

    path('settings/',views.manage_settings,name='settings'),
]