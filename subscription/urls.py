from django.urls import path
from . import views

app_name = "subscription"

urlpatterns = [
    path('plans/', views.plans_list, name='plans_list'),
    path('checkout/<str:plan_name>/', views.checkout, name='checkout'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-failure/', views.payment_failure, name='payment_failure'),
]
