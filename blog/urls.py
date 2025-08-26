from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('blog-detail/<int:id>/', views.blog_detail, name='blog_detail'),
    path('blog-update/<int:id>/', views.blog_update, name='blog_update'),
    path('blog-delete/<int:id>/', views.blog_delete, name='blog_delete'),

]
