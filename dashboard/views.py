from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseForbidden, HttpResponseNotFound, JsonResponse
import requests

from backend.models import Chapter, Course, Semester, Subject
from blog.forms import PostForm
from blog.models import Post
from contactenquiry.models import contactEnquiry
from courses.views import is_admin, is_instructor
from quiz.forms import QuizForm
from quiz.models import Quiz
from user.models import CustomUser
from user.signals import User
# Create your views here.

from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.utils import timezone

from analytics.models import UserEvent
from backend.models import Course  # adjust if your Course model is elsewhere


def dashboard_home(request):
    if not request.user.is_authenticated or not (
        request.user.is_admin_user or request.user.is_instructor_user
    ):
        return HttpResponseForbidden("You do not have permission to access this page.")

    # ✅ Users dynamic (your CustomUser roles)
    total_users = CustomUser.objects.count()
    total_paid_users = CustomUser.objects.filter(user_type="paid").count()
    total_normal_users = CustomUser.objects.filter(user_type="normal").count()
    total_admin_users = CustomUser.objects.filter(user_type="admin").count()

    # ✅ Courses dynamic
    total_courses = Course.objects.count()

    # ✅ Enquiries dynamic (today)
    today = timezone.localdate()
    new_enquiries = contactEnquiry.objects.filter(created_at__date=today).count()

    # ✅ Revenue dynamic (needs your payment/order model)
    revenue = 0  # placeholder until you tell me your payment model

    # ✅ Recent activities dynamic from UserEvent
    events = UserEvent.objects.select_related("user").order_by("-created_at")[:15]

    course_ids = [e.item_id for e in events if e.item_type == "course"]
    course_map = {c.id: c.name for c in Course.objects.filter(id__in=course_ids).only("id", "name")}

    recent_activities = []
    for e in events:
        uname = e.user.username if e.user else "Guest"

        if e.item_type == "course":
            item_label = course_map.get(e.item_id, f"Course #{e.item_id}")
        else:
            item_label = f"{e.item_type} #{e.item_id}"

        action_text = {
            "view": "viewed",
            "enroll": "enrolled in",
            "download": "downloaded",
            "click_recommendation": "clicked recommendation for",
        }.get(e.action, e.action)

        recent_activities.append({
            "message": f"{uname} {action_text} {item_label}",
            "time": e.created_at,
        })

    context = {
        "total_users": total_users,
        "total_courses": total_courses,
        "new_enquiries": new_enquiries,
        "revenue": revenue,

        # extra role breakdown (optional to show)
        "total_paid_users": total_paid_users,
        "total_normal_users": total_normal_users,
        "total_admin_users": total_admin_users,

        "recent_activities": recent_activities,
    }
    return render(request, "dashboard/home.html", context)


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

def manage_quizzes(request):
    quizzes = Quiz.objects.all()
    return render(request,'dashboard/manage_quizzes.html',{'quizzes': quizzes})


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

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Quizzes/views.py code for reference
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def dashboard_quiz_edit(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == "POST":
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            return redirect("quizzes")
    else:
        form = QuizForm(instance=quiz)

    return render(request, "dashboard/dashboard_quiz_edit.html", {"form": form, "quiz": quiz})

def dashboard_quiz_delete(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    subject_id = quiz.subject.id
    if request.method == "POST":
        quiz.delete()
        return redirect("quizzes")

    return render(request, "dashboard/dashboard_quiz_delete.html", {"quiz": quiz})




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

#----------------------------------------------------------------------------------------------------------------------------------------------
# cOUrse/models.py code for reference
#----------------------------------------------------------------------------------------------------------------------------------------------

def dashboard_course_list_view(request):
    # Retrieve token from session
    token = request.session.get('auth_token')  # Check the correct key here
    if not token:
        print("No token found in session.")
        return JsonResponse({'error': 'Authentication required, please login first.'}, status=401)

    headers = {
        'Authorization': f'Token {token}'  # Include token in headers
    }

    print(f"Sending request with headers: {headers}")  # Debugging
    
    # Make the API request with the token
    api_url = 'http://127.0.0.1:8000/backend/course-list/'
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        courses = response.json()  # API response with courses
        print("API Response:", courses)  # Debugging
    elif response.status_code == 401:
        print("Unauthorized access, check your token.")
        courses = []
    else:
        print(f"Error fetching courses: {response.status_code}, {response.text}")  # Debugging
        courses = []

    return render(request, 'dashboard/manage_courses.html', {'courses': courses})

def dashboard_course_detail_view(request, course_id):
    token = request.user.auth_token.key  # if using DRF token auth

    headers = {
        'Authorization': f'Token {token}',
    }

    course_api_url = f"http://127.0.0.1:8000/backend/course-detail/{course_id}/"
    course_response = requests.get(course_api_url, headers=headers)
    course = course_response.json() if course_response.status_code == 200 else None

    semester_api_url = "http://127.0.0.1:8000/backend/semester-list/"
    semester_response = requests.get(semester_api_url, headers=headers)
    semesters = semester_response.json() if semester_response.status_code == 200 else []
    filtered_semesters = [s for s in semesters if s['course'] == course_id]

    # Fix image URLs as before
    if course and course.get('image'):
        course['image'] = request.build_absolute_uri(course['image'])
    if course and course.get('instructor') and course['instructor'].get('image'):
        course['instructor']['image'] = request.build_absolute_uri(course['instructor']['image'])

    return render(request, 'dashboard/dashboard_course_detail.html', {'course': course, 'semesters': filtered_semesters})

def dashboard_course_create_view(request):
    if not is_admin(request) and not is_instructor(request):
        return HttpResponseForbidden("You do not have permission to create courses.")
    if request.method == "POST":
        # Make sure to include token for authentication if your API requires it
        token = request.session.get('auth_token')
        if not token:
            return HttpResponseForbidden("Authentication token missing.")
        data = {
            "name": request.POST.get("name"),
            "description": request.POST.get("description"),
        }
        files = {
            'image': request.FILES.get('image')
        } if 'image' in request.FILES else {}

        api_url = "http://127.0.0.1:8000/backend/course-create/"
        headers = {'Authorization': f'Token {token}'}
        response = requests.post(api_url, data=data, files=files, headers=headers)

        if response.status_code == 201:
            return redirect("courses")
        
    return render(request, "dashboard/dashboard_course_create.html")

def dashboard_course_update_view(request, course_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to update courses.")
    
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    # Get current course data
    api_url = f"http://127.0.0.1:8000/backend/course-detail/{course_id}/"
    response = requests.get(api_url, headers={'Authorization': f'Token {token}'})

    if response.status_code == 200:
        course = response.json()
    else:
        return redirect("course-list")

    if request.method == "POST":
        # Separate text fields and file
        data = {
            "name": request.POST.get("name"),
            "description": request.POST.get("description"),
        }

        files = {}
        image_file = request.FILES.get("image")
        if image_file:
            files["image"] = (image_file.name, image_file, image_file.content_type)

        # Send multipart/form-data request
        update_url = f"http://127.0.0.1:8000/backend/course-update/{course_id}/"
        update_response = requests.post(update_url, data=data, files=files, headers={'Authorization': f'Token {token}'})

        if update_response.status_code == 200:
            return redirect("courses")
        else:
            return render(request, "dashboard/dashboard_course_update.html", {
                "course": course,
                "error": f"Failed to update course. {update_response.text}"
            })

    return render(request, "dashboard/dashboard_course_update.html", {"course": course})

def dashboard_course_delete_view(request, course_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to delete courses.")

    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")
    # Get the course to be deleted
    api_url = f"http://127.0.0.1:8000/backend/course-detail/{course_id}/"
    response = requests.get(api_url,headers={'Authorization': f'Token {token}'})

    if response.status_code == 200:
        course = response.json()
    else:
        return redirect("courses")

    if request.method == "POST":
        # Send DELETE request to delete the course
        delete_url = f"http://127.0.0.1:8000/backend/course-delete/{course_id}/"
        delete_response = requests.delete(delete_url, headers={'Authorization': f'Token {token}'})

        if delete_response.status_code == 204:
            return redirect("courses")
        else:
            return render(request, "dashboard/dashboard_course_delete.html", {"course": course, "error": "Failed to delete course."})

    return render(request, "dashboard/dashboard_course_delete.html", {"course": course})

#----------------------------------------------------------------------------------------------------------------------------------------------
# semester/views.py code for reference
#----------------------------------------------------------------------------------------------------------------------------------------------

def dashboard_semester_list_view(request, course_id):
    # Retrieve token from session
    token = request.session.get('auth_token')  # Check the correct key here
    if not token:
        print("No token found in session.")
        return JsonResponse({'error': 'Authentication required, please login first.'}, status=401)

    headers = {
        'Authorization': f'Token {token}'  # Include token in headers
    }

    print(f"Sending request with headers: {headers}")  # Debugging
    # Fetch semesters only for the selected course
    semester_api_url = f"http://127.0.0.1:8000/backend/semester-list/{course_id}"
    response = requests.get(semester_api_url, headers=headers)
    # Check the response status
    if response.status_code == 200:
        semesters = response.json()  # API response with courses
        print("API Response:", semesters)  # Debugging
    elif response.status_code == 401:
        print("Unauthorized access, check your token.")
        semesters = []
    else:
        print(f"Error fetching semesters: {response.status_code}, {response.text}")  # Debugging
        semesters = []

    return render(request, 'dashboard/manage_semester.html', {'semesters': semesters, 'course_id': course_id})

def dashboard_semester_detail_view(request, semester_id):
    token = request.user.auth_token.key  # Assuming DRF Token Auth

    headers = {
        'Authorization': f'Token {token}',
    }
    url = f"http://127.0.0.1:8000/backend/semester-detail/{semester_id}/"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        semester = response.json()
        course_id = semester.get('course')  # ✅ Get course ID from API data

        return render(request, 'dashboard/dashboard_semester_detail.html', {
            'semester': semester,
            'course_id': course_id  # ✅ Pass to template
        })
    else:
        return render(request, 'dashboard/dashboard_semester_detail.html', {
            'error': 'Semester not found'
        })

def dashboard_semester_create_view(request, course_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to create semesters.")
    if request.method == "POST":
        token = request.session.get('auth_token')
        if not token:
            return HttpResponseForbidden("Authentication token missing.")
        data = {
            "number": request.POST.get("number"),
            "description": request.POST.get("description"),
            "course": course_id  # include course id in data if API requires it
        }
        api_url = f"http://127.0.0.1:8000/backend/semester-create/{course_id}/"
        headers = {'Authorization': f'Token {token}'}
        response = requests.post(api_url, json=data, headers=headers)

        if response.status_code == 201:
            return redirect("dashboard_manage_semesters", course_id=course_id)
        else:
            # You can handle errors here or pass message to template
            pass

    return render(request, "dashboard/dashboard_semester_create.html", {
        "course_id": course_id,
    })

def dashboard_semester_update_view(request, semester_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to update semester.")
    
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}
    api_url = f"http://127.0.0.1:8000/backend/semester-detail/{semester_id}/"
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        semester = response.json()
        course_id = semester.get('course')  # ✅ Extract course_id from API
    else:
        return redirect("courses")  # fallback redirect if fetch fails

    if request.method == "POST":
        data = {
            "number": request.POST.get("number"),
            "description": request.POST.get("description"),
        }

        update_url = f"http://127.0.0.1:8000/backend/semester-update/{semester_id}/"
        update_response = requests.post(update_url, json=data, headers=headers)

        if update_response.status_code == 200:
            return redirect("dashboard_manage_semesters", course_id=course_id)  # ✅ Pass course_id to reverse
        else:
            return render(request, "dashboard/dashboard_semester_update.html", {
                "semester": semester,
                "course_id": course_id,
                "error": "Failed to update semester."
            })

    return render(request, "dashboard/dashboard_semester_update.html", {
        "semester": semester,
        "course_id": course_id
    })
 
def dashboard_semester_delete_view(request, semester_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to delete semester.")
    
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")
    
    headers = {'Authorization': f'Token {token}'}

    # Fetch semester data
    url = f"http://127.0.0.1:8000/backend/semester-detail/{semester_id}/"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return render(request, 'dashboard/dashboard_semester_delete.html', {
            'error': 'Semester not found.',
            'semester': None
        })

    semester = response.json()
    course_id = semester.get('course')

    if request.method == 'POST':
        # DELETE only happens on POST
        delete_url = f"http://127.0.0.1:8000/backend/semester-delete/{semester_id}/"
        delete_response = requests.delete(delete_url, headers=headers)

        if delete_response.status_code in [200, 204]:
            return redirect('dashboard_manage_semesters', course_id=course_id)
        else:
            return render(request, 'dashboard/dashboard_semester_delete.html', {
                'error': 'Failed to delete semester.',
                'semester': semester,
                'course_id': course_id
            })

    # GET request: just render confirmation page
    return render(request, 'dashboard/dashboard_semester_delete.html', {
        'semester': semester,
        'course_id': course_id
    })

#----------------------------------------------------------------------------------------------------------------------------------------------
# subject/views.py code for reference
#----------------------------------------------------------------------------------------------------------------------------------------------

def dashboard_subject_list_view(request,semester_id):
    # Retrieve token from session
    token = request.session.get('auth_token')  # Check the correct key here
    if not token:
        print("No token found in session.")
        return JsonResponse({'error': 'Authentication required, please login first.'}, status=401)

    headers = {
        'Authorization': f'Token {token}'  # Include token in headers
    }
    print(f"Sending request with headers: {headers}")  # Debugging

    api_url = f'http://127.0.0.1:8000/backend/subject-list/{semester_id}/'  # Adjust the URL as per your API endpoint
    # Make the API request with the token
    response = requests.get(api_url,headers=headers)

    if response.status_code == 200:
        subjects = response.json()
        print("API Response:", subjects)  # Debugging
    elif response.status_code == 401:
        print("Unauthorized access, check your token.")
        subjects = []
    else:
        print(f"Error fetching subjects: {response.status_code}, {response.text}")  # Debugging
        subjects = []
     # ✅ Proper way to get course_id
    try:
        semester = Semester.objects.get(id=semester_id)
        course_id = semester.course_id
    except Semester.DoesNotExist:
        course_id = None  # fallback
    return render(request, 'dashboard/manage_subject.html', {'subjects': subjects, 'semester_id': semester_id, 'course_id': course_id})

def dashboard_subject_detail_view(request, subject_id):
    # Retrieve token from session
    token = request.session.get('auth_token')  # Check the correct key here
    if not token:
        print("No token found in session.")
        return JsonResponse({'error': 'Authentication required, please login first.'}, status=401)

    headers = {
        'Authorization': f'Token {token}'  # Include token in headers
    }
    print(f"Sending request with headers: {headers}")  # Debugging

    # Adjust the API URL for the subject
    subject_url = f"http://127.0.0.1:8000/backend/subject-detail/{subject_id}/"  # Adjust as per your API endpoint
    notes_url = f"http://127.0.0.1:8000/backend/note-list/{subject_id}"  # API for notes
    past_questions_url = f"http://127.0.0.1:8000/backend/pastQuestion-list/{subject_id}"  # API for past questions
    syllabus_url = f"http://127.0.0.1:8000/backend/syllabus-detail-by-subject/{subject_id}/" #API for Syllabus
    lab_url = f"http://127.0.0.1:8000/backend/lab-list/{subject_id}" #API for Labs

    # Fetch subject details
    subject_response = requests.get(subject_url, headers=headers)
    if subject_response.status_code == 200:
        subject = subject_response.json()  # Fetch subject data
    else:
        return render(request, 'dashboard/dashboard_subject_detail.html', {'error': 'Subject not found'})

    # Fetch semester_id from subject data
    semester_id = subject.get('semester')
    if not semester_id:
        return render(request, 'dashboard/dashboard_subject_detail.html', {'error': 'Semester not found for this subject'})
    
    # Fetch syllabus
    syllabus = None
    syllabus_response = requests.get(syllabus_url, headers=headers)
    if syllabus_response.status_code == 200:
        syllabus = syllabus_response.json()

    # Fetch notes
    notes_response = requests.get(notes_url)
    notes = notes_response.json() if notes_response.status_code == 200 else []

    # Fetch past questions
    past_questions_response = requests.get(past_questions_url)
    past_questions = past_questions_response.json() if past_questions_response.status_code == 200 else []

    # Fetch labs
    lab_response = requests.get(lab_url)
    labs = lab_response.json() if lab_response.status_code == 200 else []

    # Fix file URLs for notes
    for note in notes:
        note['file'] = request.build_absolute_uri(note['file'])

    for pq in past_questions:
        pq['file'] = request.build_absolute_uri(pq['file'])

    for lab in labs:
        lab['file'] = request.build_absolute_uri(lab['file'])



    return render(request, 'dashboard/dashboard_subject_detail.html', {
        'subject': subject,
        'notes': notes,
        'past_questions': past_questions,
        'syllabus':syllabus,
        'semester_id': semester_id, # ✅ Pass semester_id to template
        'labs': labs
    })

def dashboard_subject_create_view(request, semester_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to create subjects.")

    # ✅ Fetch all semesters to show in the dropdown
    semesters = Semester.objects.all()

    if request.method == "POST":
        token = request.session.get('auth_token')
        if not token:
            return HttpResponseForbidden("Authentication token missing.")

        data = {
            "name": request.POST.get("name"),
            "code": request.POST.get("code"),
            "credits": request.POST.get("credits") or 0,
            "description": request.POST.get("description"),
        }

        api_url = f"http://127.0.0.1:8000/backend/subject-create/{semester_id}/"  # Adjust if needed
        headers = {'Authorization': f'Token {token}'}
        response = requests.post(api_url, json=data, headers=headers)

        if response.status_code == 201:
            return redirect("dashboard_manage_subjects", semester_id=semester_id)

    return render(request, "dashboard/dashboard_subject_create.html", {
        "semester_id": semester_id,
        "semesters": semesters,  # ✅ send this to template
    })

def dashboard_subject_update_view(request, subject_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to update semester.")
    
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")
    
    api_url = f"http://127.0.0.1:8000/backend/subject-detail/{subject_id}/"
    response = requests.get(api_url,headers={'Authorization': f'Token {token}'})
    subject = response.json() if response.status_code == 200 else {}

    semester_id = subject.get('semester')  

    if request.method == "POST":
        credits_value = request.POST.get("credits")
        data = {
            "name": request.POST.get("name"),
            "code": request.POST.get("code"),
            "credits": int(credits_value) if credits_value else 0,  # Convert or set default
            "description": request.POST.get("description"),
            "semester": semester_id
        }
        update_url = f"http://127.0.0.1:8000/backend/subject-update/{subject_id}/"
        response = requests.post(update_url, json=data,headers={'Authorization': f'Token {token}'})

        if response.status_code == 200:
            return redirect("dashboard_manage_subjects", semester_id=semester_id)

    return render(request, "dashboard/dashboard_subject_update.html", {"subject": subject, "semester_id": semester_id})

def dashboard_subject_delete_view(request, subject_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to delete subject.")

    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    api_url = f"http://127.0.0.1:8000/backend/subject-detail/{subject_id}/"
    response = requests.get(api_url, headers={'Authorization': f'Token {token}'})
    subject = response.json() if response.status_code == 200 else {}
    
    if not subject:
        return HttpResponseNotFound("Subject not found")

    semester_id = subject.get('semester')  # ✅ Get semester_id before deletion

    if request.method == "POST":
        delete_url = f"http://127.0.0.1:8000/backend/subject-delete/{subject_id}/"
        response = requests.delete(delete_url, headers={'Authorization': f'Token {token}'})

        if response.status_code == 204:
            return redirect("dashboard_manage_subjects", semester_id=semester_id)

    return render(request, "dashboard/dashboard_subject_delete.html", {
        "subject": subject,
        "semester_id": semester_id  # ✅ Include in context for cancel button
    })

#-------------------------------------------------------------------------------------------------------------------------------------------------
# labs views can be added similarly
#-------------------------------------------------------------------------------------------------------------------------------------------------

def dashboard_lab_list_view(request, subject_id):
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}
    api_url = f'http://127.0.0.1:8000/backend/lab-list/{subject_id}/'
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        labs = response.json()
    elif response.status_code == 401:
        labs = []
    else:
        labs = []

    try:
        subject = Subject.objects.get(id=subject_id)
        semester_id = subject.semester_id
    except Subject.DoesNotExist:
        subject = None
        semester_id = None

    return render(request, 'dashboard/manage_labs.html', {
        'labs': labs,
        'semester_id': semester_id,
        'subject_id': subject_id,
        'subject': subject
    })

def dashboard_lab_detail_view(request, lab_id):
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}

    # Fetch lab details
    lab_url = f"http://127.0.0.1:8000/backend/lab-detail/{lab_id}/"
    response = requests.get(lab_url, headers=headers)

    if response.status_code != 200:
        return HttpResponseNotFound("Lab not found")

    lab = response.json()
    file_url = lab.get('file', '')
    is_pdf = file_url.lower().endswith('.pdf') if file_url else False

    # Fetch the subject related to the lab
    subject_id = lab.get('subject')
    subject = {}
    semester_id = None
    if subject_id:
        subject_url = f"http://127.0.0.1:8000/backend/subject-detail/{subject_id}/"
        subject_response = requests.get(subject_url, headers=headers)
        if subject_response.status_code == 200:
            subject = subject_response.json()
            semester_id = subject.get('semester')  # ✅ Fetch semester_id from subject

    return render(request, 'dashboard/dashboard_lab_detail.html', {
        'lab': lab,
        'subject': subject,
        'semester_id': semester_id,
        'is_pdf': is_pdf,
    })

def dashboard_lab_create_view(request, subject_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to create labs.")

    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        return HttpResponseNotFound("Subject not found.")

    if request.method == "POST":
        token = request.session.get('auth_token')
        if not token:
            return HttpResponseForbidden("Authentication token missing.")

        data = {
            "title": request.POST.get("title"),
            "description": request.POST.get("description"),
            "subject": subject_id,
        }

        files = {}
        file_upload = request.FILES.get("file")
        if file_upload:
            files['file'] = file_upload

        api_url = f"http://127.0.0.1:8000/backend/lab-create/{subject_id}/"
        headers = {'Authorization': f'Token {token}'}
        response = requests.post(api_url, data=data, files=files, headers=headers)

        if response.status_code == 201:
            return redirect("dashboard_manage_labs", subject_id=subject_id)
        else:
            error_message = "Failed to create lab. Please try again."
            return render(request, "dashboard/dashboard_lab_create.html", {
                "subject": subject,
                "subject_id": subject_id,
                "error": error_message
            })

    return render(request, "dashboard/dashboard_lab_create.html", {
        "subject": subject,
        "subject_id": subject_id
    })

def dashboard_lab_update_view(request, lab_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to update labs.")

    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}
    api_url = f"http://127.0.0.1:8000/backend/lab-detail/{lab_id}/"
    response = requests.get(api_url, headers=headers)
    lab = response.json() if response.status_code == 200 else {}

    if not lab:
        return HttpResponseNotFound("Lab not found")

    subject_id = lab.get('subject')
    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        subject = None

    if request.method == "POST":
        data = {
            "title": request.POST.get("title"),
            "description": request.POST.get("description"),
            "subject": subject_id,
        }

        files = {}
        file_upload = request.FILES.get("file")
        if file_upload:
            files['file'] = file_upload

        update_url = f"http://127.0.0.1:8000/backend/lab-update/{lab_id}/"
        update_response = requests.post(update_url, data=data, files=files, headers=headers)

        if update_response.status_code == 200:
            return redirect("dashboard_manage_labs", subject_id=subject_id)
        else:
            return render(request, "dashboard/dashboard_lab_update.html", {
                "lab": lab,
                "subject": subject,
                "subject_id": subject_id,
                "error": "Failed to update lab. Please try again."
            })

    return render(request, "dashboard/dashboard_lab_update.html", {
        "lab": lab,
        "subject": subject,
        "subject_id": subject_id
    })

def dashboard_lab_delete_view(request, lab_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to delete labs.")

    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}
    url = f"http://127.0.0.1:8000/backend/lab-detail/{lab_id}/"
    response = requests.get(url, headers=headers)
    lab = response.json() if response.status_code == 200 else {}

    if not lab:
        return HttpResponseNotFound("Lab not found")

    subject_id = lab.get('subject')
    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        subject = None

    if request.method == 'POST':
        delete_url = f"http://127.0.0.1:8000/backend/lab-delete/{lab_id}/"
        delete_response = requests.delete(delete_url, headers=headers)

        if delete_response.status_code in [200, 204]:
            return redirect('dashboard_manage_labs', subject_id=subject_id)
        else:
            error_message = "Failed to delete lab. Please try again."
            return render(request, 'dashboard/dashboard_lab_delete.html', {
                'lab': lab,
                'subject': subject,
                'subject_id': subject_id,
                'error': error_message
            })

    return render(request, 'dashboard/dashboard_lab_delete.html', {
        'lab': lab,
        'subject': subject,
        'subject_id': subject_id
    })

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Syllabus views can be added similarly
#-------------------------------------------------------------------------------------------------------------------------------------------------

def dashboard_syllabus_list_view(request, subject_id):
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}
    api_url = f'http://127.0.0.1:8000/backend/syllabus-list/{subject_id}/'  # list endpoint
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        result = response.json()
        # If API returns a list, grab first element or None
        syllabus = result[0] if isinstance(result, list) and result else None
        print("API Response:", result)
    else:
        syllabus = None

    # Fetch subject for template breadcrumbs
    try:
        subject = Subject.objects.get(id=subject_id)
        semester_id = subject.semester_id
    except Subject.DoesNotExist:
        subject = None
        semester_id = None

    return render(request, 'dashboard/manage_syllabus.html', {
        'syllabus': syllabus,
        'subject': subject,
        'semester_id': semester_id,
        'subject_id': subject_id
    })

def dashboard_syllabus_detail_view(request, syllabus_id):
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}
    syllabus_url = f"http://127.0.0.1:8000/backend/syllabus-detail/{syllabus_id}/"

    response = requests.get(syllabus_url, headers=headers)
    if response.status_code == 200:
        syllabus = response.json()
    else:
        return HttpResponseNotFound("Syllabus not found")

    # Get subject_id for back button / breadcrumbs
    subject_id = syllabus.get('subject')
    if not subject_id:
        return HttpResponseNotFound("Subject not found for this syllabus")

    # Determine if the uploaded file is a PDF
    file_url = syllabus.get('file', '')
    is_pdf = file_url.lower().endswith('.pdf') if file_url else False

    return render(request, 'dashboard/dashboard_syllabus_detail.html', {
        'syllabus': syllabus,
        'subject_id': subject_id,
        'is_pdf': is_pdf,
    })

def dashboard_syllabus_create_view(request, subject_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to create syllabus.")

    # ✅ Fetch subject for template breadcrumbs
    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        return HttpResponseNotFound("Subject not found.")

    # ✅ Check if syllabus already exists
    if hasattr(subject, "syllabus"):
        return redirect("dashboard_syllabus_update", syllabus_id=subject.syllabus.id)

    if request.method == "POST":
        token = request.session.get('auth_token')
        if not token:
            return HttpResponseForbidden("Authentication token missing.")

        data = {
            "objectives": request.POST.get("objectives"),
            "subject": subject_id,
        }

        # ✅ Handle optional file upload
        files = {}
        file_upload = request.FILES.get('file')
        if file_upload:
            files['file'] = file_upload

        api_url = f"http://127.0.0.1:8000/backend/syllabus-create/{subject_id}/"
        headers = {'Authorization': f'Token {token}'}
        response = requests.post(api_url, data=data, files=files, headers=headers)

        if response.status_code == 201:
            return redirect("dashboard_manage_syllabus", subject_id=subject_id)
        else:
            error_message = "Failed to create syllabus. Please try again."
            return render(request, "dashboard/dashboard_syllabus_create.html", {
                "subject": subject,
                "subject_id": subject_id,
                "error": error_message
            })

    return render(request, "dashboard/dashboard_syllabus_create.html", {
        "subject": subject,
        "subject_id": subject_id
    })

def dashboard_syllabus_update_view(request, syllabus_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to update syllabus.")
    
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}
    
    # Fetch existing syllabus data
    api_url = f"http://127.0.0.1:8000/backend/syllabus-detail/{syllabus_id}/"
    response = requests.get(api_url, headers=headers)
    syllabus = response.json() if response.status_code == 200 else {}

    if not syllabus:
        return HttpResponseNotFound("Syllabus not found.")

    subject_id = syllabus.get('subject')

    if request.method == "POST":
        data = {
            "objectives": request.POST.get("objectives", ""),
            "subject": subject_id,
        }

        files = {}
        file_upload = request.FILES.get("file")
        if file_upload:
            files["file"] = (file_upload.name, file_upload, file_upload.content_type)

        update_url = f"http://127.0.0.1:8000/backend/syllabus-update/{syllabus_id}/"
        update_response = requests.post(update_url, data=data, files=files, headers=headers)

        if update_response.status_code == 200:
            return redirect("dashboard_manage_syllabus", subject_id=subject_id)
        else:
            error_message = "Failed to update syllabus. Please try again."
            return render(request, "dashboard/dashboard_syllabus_update.html", {
                "syllabus": syllabus,
                "subject_id": subject_id,
                "error": error_message
            })

    return render(request, "dashboard/dashboard_syllabus_update.html", {
        "syllabus": syllabus,
        "subject_id": subject_id
    })

def dashboard_syllabus_delete_view(request, syllabus_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to delete syllabus.")

    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}

    # Fetch syllabus data
    url = f"http://127.0.0.1:8000/backend/syllabus-detail/{syllabus_id}/"
    response = requests.get(url, headers=headers)
    syllabus = response.json() if response.status_code == 200 else {}

    if not syllabus:
        return HttpResponseNotFound("Syllabus not found")
    
    subject_id = syllabus.get('subject')  # ✅ Get subject_id before deletion

    if request.method == 'POST':
        # Correct DELETE URL using syllabus_id
        delete_url = f"http://127.0.0.1:8000/backend/syllabus-delete/{syllabus_id}/"
        delete_response = requests.delete(delete_url, headers=headers)

        if delete_response.status_code in [200, 204]:
            return redirect('dashboard_manage_syllabus', subject_id=subject_id)

    return render(request, 'dashboard/dashboard_syllabus_delete.html', {
        'error': 'Failed to delete syllabus.',
        'syllabus': syllabus,
        'subject_id': subject_id
    })

#----------------------------------------------------------------------------------------------------------------------------------------------
# Past Questions views can be added similarly
#----------------------------------------------------------------------------------------------------------------------------------------------

def dashboard_pastQuestion_list_view(request, subject_id):
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}
    print(f"Sending request with headers: {headers}")  # Debugging
    api_url = f'http://127.0.0.1:8000/backend/pastQuestion-list/{subject_id}/'  # Adjust the URL as per your API endpoint
     # Make the API request with the token
    response = requests.get(api_url,headers=headers)

    if response.status_code == 200:
        pastQuestions = response.json()
        print("API Response:", pastQuestions)  # Debugging
    elif response.status_code == 401:
        print("Unauthorized access, check your token.")
        pastQuestions = []
    else:
        print(f"Error fetching pastQuestions: {response.status_code}, {response.text}")  # Debugging
        pastQuestions = []
     # ✅ Proper way to get subject_id
    try:
        subject = Subject.objects.get(id=subject_id)
        semester_id = subject.semester_id
    except Subject.DoesNotExist:
        subject = None
        semester_id = None  # fallback
    return render(request, 'dashboard/manage_pastQuestion.html', {'pastQuestions': pastQuestions, 'semester_id': semester_id, 'subject_id': subject_id,'subject': subject})

def dashboard_pastQuestion_detail_view(request, pastQuestion_id):
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}
    api_url = f"http://127.0.0.1:8000/backend/pastQuestion-detail/{pastQuestion_id}/"

    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        pastQuestion = response.json()
        file_url = pastQuestion.get('file', '')
        is_pdf = file_url.lower().endswith('.pdf') if file_url else False
    else:
        return HttpResponseNotFound("Past Question not found")
    
    try:
        subject_id = pastQuestion.get('subject')
        subject = Subject.objects.get(id=subject_id)
        semester_id = subject.semester_id
    except Subject.DoesNotExist:
        subject = None
        semester_id = None  # fallback

    return render(request, 'dashboard/dashboard_pastQuestion_detail.html', {
        'pastQuestion': pastQuestion,
        'is_pdf': is_pdf,
        'subject': subject,
        'semester_id': semester_id,
    })

def dashboard_pastQuestion_create_view(request, subject_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to create past questions.")

    # ✅ Fetch the subject for template context
    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        return HttpResponseNotFound("Subject not found.")

    if request.method == "POST":
        token = request.session.get('auth_token')
        if not token:
            return HttpResponseForbidden("Authentication token missing.")

        data = {
            "title": request.POST.get("title"),
            "year": request.POST.get("year"),
            "description": request.POST.get("description"),
            "subject": subject_id,  # include subject id in data if API requires it
        }

        files = {}
        file_upload = request.FILES.get("file")
        if file_upload:
            files['file'] = file_upload

        api_url = f"http://127.0.0.1:8000/backend/pastQuestion-create/{subject_id}/"
        headers = {'Authorization': f'Token {token}'}
        response = requests.post(api_url, data=data, files=files, headers=headers)

        if response.status_code == 201:
            return redirect("dashboard_manage_pastQuestions", subject_id=subject_id)
        else:
            # ✅ Optional: handle API errors
            error_message = "Failed to create past question. Please try again."
            return render(request, "dashboard/dashboard_pastQuestion_create.html", {
                "subject": subject,
                "subject_id": subject_id,
                "error": error_message
            })

    return render(request, "dashboard/dashboard_pastQuestion_create.html", {
        "subject": subject,
        "subject_id": subject_id
    })

def dashboard_pastQuestion_update_view(request, pastQuestion_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to update past questions.")

    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}

    # ✅ Fetch past question details
    api_url = f"http://127.0.0.1:8000/backend/pastQuestion-detail/{pastQuestion_id}/"
    response = requests.get(api_url, headers=headers)
    pastQuestion = response.json() if response.status_code == 200 else {}

    if not pastQuestion:
        return HttpResponseNotFound("Past Question not found")

    subject_id = pastQuestion.get('subject')

    # ✅ Fetch subject for template breadcrumbs
    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        subject = None

    if request.method == "POST":
        data = {
            "title": request.POST.get("title"),
            "year": request.POST.get("year"),
            "description": request.POST.get("description"),
            "subject": subject_id,
        }

        # Handle optional file upload
        files = {}
        file_upload = request.FILES.get("file")
        if file_upload:
            files['file'] = file_upload

        update_url = f"http://127.0.0.1:8000/backend/pastQuestion-update/{pastQuestion_id}/"
        update_response = requests.post(update_url, data=data, files=files, headers=headers)

        if update_response.status_code == 200:
            return redirect("dashboard_manage_pastQuestions", subject_id=subject_id)
        else:
            return render(request, "dashboard/dashboard_pastQuestion_update.html", {
                "pastQuestion": pastQuestion,
                "subject": subject,
                "subject_id": subject_id,
                "error": "Failed to update past question. Please try again."
            })

    return render(request, "dashboard/dashboard_pastQuestion_update.html", {
        "pastQuestion": pastQuestion,
        "subject": subject,
        "subject_id": subject_id
    })

def dashboard_pastQuestion_delete_view(request, pastQuestion_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to delete past questions.")

    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}

    # ✅ Fetch past question details
    url = f"http://127.0.0.1:8000/backend/pastQuestion-detail/{pastQuestion_id}/"
    response = requests.get(url, headers=headers)
    pastQuestion = response.json() if response.status_code == 200 else {}

    if not pastQuestion:
        return HttpResponseNotFound("Past Question not found")

    subject_id = pastQuestion.get('subject')  # For redirect/back link

    # ✅ Fetch subject for template breadcrumbs
    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        subject = None

    if request.method == 'POST':
        delete_url = f"http://127.0.0.1:8000/backend/pastQuestion-delete/{pastQuestion_id}/"
        delete_response = requests.delete(delete_url, headers=headers)

        if delete_response.status_code in [200, 204]:
            return redirect('dashboard_manage_pastQuestions', subject_id=subject_id)
        else:
            error_message = "Failed to delete past question. Please try again."
            return render(request, 'dashboard/dashboard_pastQuestion_delete.html', {
                'pastQuestion': pastQuestion,
                'subject': subject,
                'subject_id': subject_id,
                'error': error_message
            })

    return render(request, 'dashboard/dashboard_pastQuestion_delete.html', {
        'pastQuestion': pastQuestion,
        'subject': subject,
        'subject_id': subject_id
    })

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Chapter views can be added similarly
#-------------------------------------------------------------------------------------------------------------------------------------------------

def dashboard_chapter_list_view(request, subject_id):
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}
    print(f"Sending request with headers: {headers}")

    api_url = f"http://127.0.0.1:8000/backend/chapter-list/{subject_id}/"
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        chapters = response.json()
        print("API Response:", chapters)
    elif response.status_code == 401:
        print("Unauthorized access, check your token.")
        chapters = []
    else:
        print(f"Error fetching chapters: {response.status_code}, {response.text}")
        chapters = []

    # ✅ Fetch subject info for template
    try:
        subject = Subject.objects.get(id=subject_id)
        semester_id = subject.semester_id
    except Subject.DoesNotExist:
        subject = None
        semester_id = None

    return render(request, 'dashboard/manage_chapters.html', {
        'chapters': chapters,
        'subject': subject,
        'semester_id': semester_id,
        'subject_id': subject_id,
    })

def dashboard_chapter_detail_view(request, chapter_id):
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}
    print(f"Sending request with headers: {headers}")

    chapter_url = f"http://127.0.0.1:8000/backend/chapter-detail/{chapter_id}/"
    response = requests.get(chapter_url, headers=headers)
    if response.status_code == 200:
        chapter = response.json()
    else:
        return HttpResponseNotFound("Chapter not found")
    # ✅ Get subject_id from chapter data
    subject_id = chapter.get('subject')
    if not subject_id:
        return HttpResponseNotFound("Subject not found for this chapter")
    try:
        subject = Subject.objects.get(id=subject_id)
        semester_id = subject.semester_id
    except Subject.DoesNotExist:
        subject = None
        semester_id = None

    return render(request, 'dashboard/dashboard_chapter_detail.html', {
        'chapter': chapter,
        'subject_id': subject_id,
        'subject': subject,
        'semester_id': semester_id,
    })

def dashboard_chapter_create_view(request, subject_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to create chapters.")

    # ✅ Fetch the subject to show context in template
    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        return HttpResponseNotFound("Subject not found.")

    if request.method == "POST":
        token = request.session.get('auth_token')
        if not token:
            return HttpResponseForbidden("Authentication token missing.")
        
        data = {
            "title": request.POST.get("title"),
            "description": request.POST.get("description"),
            "order": int(request.POST.get("order", 1))  # Convert to int, default to 1
        }
        
        # ✅ Fixed API URL - should be chapter-create, not chapter-update
        api_url = f"http://127.0.0.1:8000/backend/chapter-create/{subject_id}/"
        headers = {'Authorization': f'Token {token}'}
        response = requests.post(api_url, json=data, headers=headers)   

        if response.status_code == 201:
            return redirect("dashboard_manage_chapters", subject_id=subject_id)
        else:
            # ✅ Handle API errors (optional)
            error_message = "Failed to create chapter. Please try again."
            return render(request, "dashboard/dashboard_chapter_create.html", {
                "subject_id": subject_id,
                "subject": subject,
                "error": error_message
            })
    
    return render(request, "dashboard/dashboard_chapter_create.html", {
        "subject_id": subject_id,
        "subject": subject,  # ✅ Send subject to template for breadcrumb
    })
    
def dashboard_chapter_update_view(request, chapter_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to update chapters.")

    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    api_url = f"http://127.0.0.1:8000/backend/chapter-detail/{chapter_id}/"
    response = requests.get(api_url, headers={'Authorization': f'Token {token}'})
    chapter = response.json() if response.status_code == 200 else {}

    subject_id = chapter.get('subject')

    # ✅ DEFINE DEFAULTS (IMPORTANT)
    subject = None
    semester_id = None

    if subject_id:
        try:
            subject = Subject.objects.get(id=subject_id)
            semester_id = subject.semester_id
        except Subject.DoesNotExist:
            pass

    if request.method == "POST":
        order_value = request.POST.get("order")

        data = {
            "title": request.POST.get("title"),
            "description": request.POST.get("description"),
            "subject": subject_id,
            "order": int(order_value) if order_value else 0,
        }

        update_url = f"http://127.0.0.1:8000/backend/chapter-update/{chapter_id}/"
        update_response = requests.post(
            update_url,
            json=data,
            headers={'Authorization': f'Token {token}'}
        )

        if update_response.status_code == 200:
            return redirect("dashboard_manage_chapters", subject_id=subject_id)

    return render(
        request,
        "dashboard/dashboard_chapter_update.html",
        {
            "chapter": chapter,
            "subject_id": subject_id,
            "subject": subject,
            "semester_id": semester_id,
        }
    )

def dashboard_chapter_delete_view(request, chapter_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to delete chapters.")

    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    api_url = f"http://127.0.0.1:8000/backend/chapter-detail/{chapter_id}/"
    response = requests.get(api_url, headers={'Authorization': f'Token {token}'})
    chapter = response.json() if response.status_code == 200 else {}

    if not chapter:
        return HttpResponseNotFound("Chapter not found")

    subject_id = chapter.get('subject')  # ✅ Get subject_id before deletion

    if request.method == "POST":
        delete_url = f"http://127.0.0.1:8000/backend/chapter-delete/{chapter_id}/"
        delete_response = requests.delete(delete_url, headers={'Authorization': f'Token {token}'})

        if delete_response.status_code in [200, 204]:
            return redirect("dashboard_manage_chapters", subject_id=subject_id)

    return render(request, "dashboard/dashboard_chapter_delete.html", {
        "chapter": chapter,
        "subject_id": subject_id  # ✅ Include for cancel/back link
    })

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Notes views can be added similarly
#-------------------------------------------------------------------------------------------------------------------------------------------------

def dashboard_note_list_view(request, chapter_id):
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}
    print(f"Sending request with headers: {headers}")  # Debugging

    api_url = f'http://127.0.0.1:8000/backend/note-list/{chapter_id}/'
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        notes = response.json()
        print("API Response:", notes)  # Debugging
    elif response.status_code == 401:
        print("Unauthorized access, check your token.")
        notes = []
    else:
        print(f"Error fetching notes: {response.status_code}, {response.text}")  # Debugging
        notes = []

    # ✅ Fetch subject_id from chapter
    try:
        chapter = Chapter.objects.get(id=chapter_id)
        subject_id = chapter.subject_id
    except Chapter.DoesNotExist:
        chapter = None
        subject_id = None

    return render(request, 'dashboard/manage_notes.html', {
        'notes': notes,
        'chapter_id': chapter_id,
        'subject_id': subject_id,
        'chapter': chapter
    })

def dashboard_note_detail_view(request, note_id):
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}
    api_url = f"http://127.0.0.1:8000/backend/note-detail/{note_id}/"

    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        return HttpResponseNotFound("Note not found")

    note = response.json()

    # File handling
    file_url = note.get('file', '')
    is_pdf = file_url.lower().endswith('.pdf') if file_url else False

    # ✅ Get chapter_id from note API
    chapter_id = note.get('chapter')
    if not chapter_id:
        return HttpResponseNotFound("Chapter not found for this note")

    # ✅ Fetch Chapter object correctly
    try:
        chapter = Chapter.objects.select_related('subject').get(id=chapter_id)
        subject = chapter.subject
        semester_id = subject.semester_id if subject else None
    except Chapter.DoesNotExist:
        return HttpResponseNotFound("Chapter does not exist")

    return render(
        request,
        'dashboard/dashboard_note_detail.html',
        {
            'note': note,
            'chapter': chapter,
            'chapter_id': chapter_id,
            'subject': subject,
            'semester_id': semester_id,
            'is_pdf': is_pdf,
        }
    )

def dashboard_note_create_view(request, chapter_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to create notes.")

    # ✅ Fetch Chapter + Subject in ONE query
    try:
        chapter = Chapter.objects.select_related('subject').get(id=chapter_id)
        subject = chapter.subject
        semester_id = subject.semester_id if subject else None
    except Chapter.DoesNotExist:
        return HttpResponseNotFound("Chapter not found.")

    if request.method == "POST":
        token = request.session.get('auth_token')
        if not token:
            return HttpResponseForbidden("Authentication token missing.")

        data = {
            "title": request.POST.get("title"),
            "description": request.POST.get("description"),
            "chapter": chapter_id,
        }

        files = {}
        if 'file' in request.FILES:
            files['file'] = request.FILES['file']

        api_url = f"http://127.0.0.1:8000/backend/note-create/{chapter_id}/"
        headers = {'Authorization': f'Token {token}'}
        response = requests.post(api_url, data=data, files=files, headers=headers)

        if response.status_code == 201:
            return redirect("dashboard_manage_notes", chapter_id=chapter_id)

        return render(
            request,
            "dashboard/dashboard_note_create.html",
            {
                "chapter": chapter,
                "subject": subject,
                "semester_id": semester_id,
                "error": "Failed to create note. Please try again.",
            }
        )

    return render(
        request,
        "dashboard/dashboard_note_create.html",
        {
            "chapter": chapter,
            "subject": subject,
            "semester_id": semester_id,
        }
    )

def dashboard_note_update_view(request, note_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to update notes.")

    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}

    # ✅ Get note details
    note_url = f"http://127.0.0.1:8000/backend/note-detail/{note_id}/"
    response = requests.get(note_url, headers=headers)
    note = response.json() if response.status_code == 200 else {}

    # Get chapter details for template
    chapter_id = note.get('chapter')
    chapter = {}
    if chapter_id:
        chapter_url = f"http://127.0.0.1:8000/backend/chapter-detail/{chapter_id}/"
        chapter_response = requests.get(chapter_url, headers=headers)
        if chapter_response.status_code == 200:
            chapter = chapter_response.json()

    if request.method == "POST":
        data = {
            "title": request.POST.get("title"),
            "description": request.POST.get("description"),
            "chapter": chapter_id,
        }

        # Handle optional file upload
        files = {}
        file_upload = request.FILES.get("file")
        if file_upload:
            files["file"] = (file_upload.name, file_upload, file_upload.content_type)

        update_url = f"http://127.0.0.1:8000/backend/note-update/{note_id}/"
        update_response = requests.post(update_url, data=data, files=files, headers=headers)

        if update_response.status_code == 200:
            return redirect("dashboard_manage_notes", chapter_id=chapter_id)

    return render(
        request,
        "dashboard/dashboard_note_update.html",
        {
            "note": note,
            "chapter": chapter,  # Pass chapter object to template
        }
    )

def dashboard_note_delete_view(request, note_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to delete notes.")

    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}

    # ✅ Fetch note data
    detail_url = f"http://127.0.0.1:8000/backend/note-detail/{note_id}/"
    response = requests.get(detail_url, headers=headers)
    note = response.json() if response.status_code == 200 else {}

    if not note:
        return HttpResponseNotFound("Note not found")

    chapter_id = note.get('chapter')  # ✅ Get chapter_id before deletion

    if request.method == 'POST':
        # DELETE request
        delete_url = f"http://127.0.0.1:8000/backend/note-delete/{note_id}/"
        delete_response = requests.delete(delete_url, headers=headers)

        if delete_response.status_code in [200, 204]:
            return redirect('dashboard_manage_notes', chapter_id=chapter_id)

    return render(request, 'dashboard/dashboard_note_delete.html', {
        'note': note,
        'chapter_id': chapter_id
    })

