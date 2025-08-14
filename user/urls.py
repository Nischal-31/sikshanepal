from django.urls import path, include
from django.conf import settings
from . import views
from django.conf.urls.static import static
from .views import profile_view

urlpatterns = [
    path('login/', views.Login, name ='login'),
    path('logout/', views.logout_view, name='logout'),
	path('register/', views.register, name ='register'),
    path('profile/', profile_view, name='user-profile'),
    path('password-reset/', views.password_reset_form, name='password_reset_form'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm_form'),
]
