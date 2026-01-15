from django.urls import path
from .views import dashboard_home
from . import views
from user import views as user_views

urlpatterns=[
    path('',views.dashboard_home,name='home'),
    path('courses/',views.manage_courses,name='courses'),

    ## User Management URLs
    path('users/',views.manage_users,name='users'),
    path('users/<int:user_id>/profile/', user_views.admin_view_user_profile, name='admin_view_user_profile'),
    path('users/<int:user_id>/edit/', user_views.edit_user, name='edit_user'),
    #path('users/<int:user_id>/delete/', user_views.delete_user, name='delete_user'),
    #path('users/<int:user_id>/change_role/', user_views.change_role, name='change_role'),


    path('enquiries/',views.manage_enquiries,name='enquiries'),
    path('reports/',views.manage_reports,name='reports'),
    path('settings/',views.manage_settings,name='settings'),
]