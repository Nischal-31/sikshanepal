from django.shortcuts import render
from django.http import HttpResponseForbidden

from backend.models import Course
from contactenquiry.models import contactEnquiry
from user.signals import User
# Create your views here.

def dashboard_home(request):
    if not request.user.is_authenticated or not request.user.is_admin_user:
        return HttpResponseForbidden("You do not have permission to access this page.")
    
    context = {
        'total_users': 1234,
        'total_courses': 56,
        'new_enquiries': 78,
        'revenue': 12345,
        'recent_activities': [
            "User John Doe signed up",
            "New course 'Python Basics' added",
            "Enquiry from student: nischal123@gmail.com",
            "Revenue of $200 received from course purchase",
        ]
    }
    return render(request, 'dashboard/home.html', context)


def manage_courses(request):
    courses = Course.objects.all()
    return render(request, 'dashboard/manage_courses.html',{'courses':courses})

def manage_users(request):
    users = User.objects.all()
    return render(request, 'dashboard/manage_users.html', {'users': users})

def manage_enquiries(request):
    enquiries = contactEnquiry.objects.all()
    return render(request, 'dashboard/manage_enquiries.html', {'enquiries': enquiries})

def manage_reports(request):
    return render(request, 'dashboard/manage_reports.html')

def manage_settings(request):
    return render(request, 'dashboard/manage_settings.html')

# Additional views for other dashboard functionalities can be added here    