from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseForbidden

from backend.models import Course
from blog.forms import PostForm
from blog.models import Post
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

def manage_blogs(request):
    blogs = Post.objects.all()
    return render(request, 'dashboard/manage_blogs.html', {'blogs': blogs})

def manage_settings(request):
    return render(request, 'dashboard/manage_settings.html')

# Additional views for other dashboard functionalities can be added here  
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# blog/views.py code for reference
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def dashboard_blog_add(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blogs')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PostForm()

    return render(request, 'dashboard/dashboard_blog_add.html', {'form': form})

def dashboard_blog_detail(request,id):
    post=Post.objects.get(id=id)
    return render(request,'dashboard/dashboard_blog_detail.html',{'post':post})

def dashboard_blog_edit(request, id):
    post = get_object_or_404(Post, id=id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blogs')
    else:
        form = PostForm(instance=post)

    return render(request, 'dashboard/dashboard_blog_edit.html', {'form': form, 'post': post})

def dashboard_blog_delete(request, id):
    post = get_object_or_404(Post, id=id)

    if request.method == 'POST':
        post.delete()
        return redirect('blogs')
    
    return render(request, 'dashboard/dashboard_blog_delete.html', {'post': post})


#----------------------------------------------------------------------------------------------------------------------------------------------
# contactenquiry/models.py code for reference
#----------------------------------------------------------------------------------------------------------------------------------------------

def dashboard_contact_detail(request, id):
    contact = get_object_or_404(contactEnquiry, id=id)
    return render(request, 'dashboard/dashboard_contact_detail.html', {'contact': contact})

def dashboard_contact_delete(request, id):
    contact = get_object_or_404(contactEnquiry, id=id)
    if request.method == 'POST':
        contact.delete()
        return redirect('enquiries')
    return render(request, 'dashboard/dashboard_contact_delete.html', {'contact': contact})

def dashboard_contact_change_status(request, id, new_status):
    enquiry = get_object_or_404(contactEnquiry, id=id)

    if new_status not in ['pending', 'approved', 'done']:
        messages.error(request, 'Invalid status.')
        return redirect('enquiries')

    enquiry.status = new_status
    enquiry.save()
    return redirect('dashboard_contact_detail', id=id)