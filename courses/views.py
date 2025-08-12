
from django.shortcuts import render,HttpResponse,redirect
import requests  # For making HTTP requests
from django.http import Http404, HttpResponseForbidden, HttpResponseNotFound, JsonResponse
import requests
from django.contrib.auth.decorators import login_required
from backend.models import Chapter, Semester, Subject


def is_admin(request):
    return request.user.is_authenticated and request.user.user_type == 'admin'

#-------------------------------------------------------------------------------------------------------------------
#                       COURSE VIEWS
#-------------------------------------------------------------------------------------------------------------------

@login_required
def course_list_view(request):
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

    return render(request, 'courses/course_list.html', {'courses': courses})

@login_required
def course_detail_view(request, course_id):
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

    return render(request, 'courses/course_detail.html', {'course': course, 'semesters': filtered_semesters})

@login_required
def course_create_view(request):
    if not is_admin(request):
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
            return redirect("course-list")  # Redirect to course list page
    
    return render(request, "courses/course_create.html")

@login_required
def course_update_view(request, course_id):
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
            return redirect("course-list")
        else:
            return render(request, "courses/course_update.html", {
                "course": course,
                "error": f"Failed to update course. {update_response.text}"
            })

    return render(request, "courses/course_update.html", {"course": course})

@login_required
def course_delete_view(request, course_id):
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
        return redirect("course-list")

    if request.method == "POST":
        # Send DELETE request to delete the course
        delete_url = f"http://127.0.0.1:8000/backend/course-delete/{course_id}/"
        delete_response = requests.delete(delete_url, headers={'Authorization': f'Token {token}'})

        if delete_response.status_code == 204:
            return redirect("course-list")
        else:
            return render(request, "courses/course_delete.html", {"course": course, "error": "Failed to delete course."})

    return render(request, "courses/course_delete.html", {"course": course})

#-------------------------------------------------------------------------------------------------------------------
#                       SEMESTER VIEWS
#-------------------------------------------------------------------------------------------------------------------

@login_required
def semester_list_view(request, course_id):
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

    return render(request, 'semesters/semester_list.html', {'semesters': semesters, 'course_id': course_id})

@login_required
def semester_detail_view(request, semester_id):
    token = request.user.auth_token.key  # Assuming DRF Token Auth

    headers = {
        'Authorization': f'Token {token}',
    }
    url = f"http://127.0.0.1:8000/backend/semester-detail/{semester_id}/"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        semester = response.json()
        course_id = semester.get('course')  # ✅ Get course ID from API data

        return render(request, 'semesters/semester_detail.html', {
            'semester': semester,
            'course_id': course_id  # ✅ Pass to template
        })
    else:
        return render(request, 'semesters/semester_detail.html', {
            'error': 'Semester not found'
        })

@login_required
def semester_create_view(request, course_id):
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
            return redirect("semester-list", course_id=course_id)
        else:
            # You can handle errors here or pass message to template
            pass

    return render(request, "semesters/semester_create.html", {
        "course_id": course_id,
    })

@login_required
def semester_update_view(request, semester_id):
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
        return redirect("course-list")  # fallback redirect if fetch fails

    if request.method == "POST":
        data = {
            "number": request.POST.get("number"),
            "description": request.POST.get("description"),
        }

        update_url = f"http://127.0.0.1:8000/backend/semester-update/{semester_id}/"
        update_response = requests.post(update_url, json=data, headers=headers)

        if update_response.status_code == 200:
            return redirect("semester-list", course_id=course_id)  # ✅ Pass course_id to reverse
        else:
            return render(request, "semesters/semester_update.html", {
                "semester": semester,
                "course_id": course_id,
                "error": "Failed to update semester."
            })

    return render(request, "semesters/semester_update.html", {
        "semester": semester,
        "course_id": course_id
    })
 
@login_required
def semester_delete_view(request, semester_id):
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
        return render(request, 'courses/semester_delete.html', {
            'error': 'Semester not found.',
            'semester': None
        })

    semester = response.json()
    course_id = semester.get('course')

    if request.method == 'POST':
        # DELETE request with headers
        delete_url = f"http://127.0.0.1:8000/backend/semester-delete/{semester_id}/"
        delete_response = requests.delete(delete_url, headers=headers)

        if delete_response.status_code in [200, 204]:
            return redirect('semester-list', course_id=course_id)

        return render(request, 'semesters/semester_delete.html', {
            'error': 'Failed to delete semester.',
            'semester': semester,
            'course_id': course_id
        })

    return render(request, 'semesters/semester_delete.html', {
        'semester': semester,
        'course_id': course_id
    })

#-------------------------------------------------------------------------------------------------------------------
#                       SUBJECT VIEWS
#-------------------------------------------------------------------------------------------------------------------

@login_required
def subject_list_view(request,semester_id):
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
    return render(request, 'subjects/subject_list.html', {'subjects': subjects, 'semester_id': semester_id, 'course_id': course_id})

@login_required
def subject_detail_view(request, subject_id):
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

    # Fetch subject details
    subject_response = requests.get(subject_url, headers=headers)
    if subject_response.status_code == 200:
        subject = subject_response.json()  # Fetch subject data
    else:
        return render(request, 'subjects/subject_detail.html', {'error': 'Subject not found'})

    # Fetch semester_id from subject data
    semester_id = subject.get('semester')
    if not semester_id:
        return render(request, 'subjects/subject_detail.html', {'error': 'Semester not found for this subject'})
    
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

    for note in notes:
        note['file'] = request.build_absolute_uri(note['file'])
        
        
    return render(request, 'subjects/subject_detail.html', {
        'subject': subject,
        'notes': notes,
        'past_questions': past_questions,
        'syllabus':syllabus,
        'semester_id': semester_id, # ✅ Pass semester_id to template
    })

@login_required
def subject_create_view(request, semester_id):
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
        }

        api_url = f"http://127.0.0.1:8000/backend/subject-create/{semester_id}/"  # Adjust if needed
        headers = {'Authorization': f'Token {token}'}
        response = requests.post(api_url, json=data, headers=headers)

        if response.status_code == 201:
            return redirect("subject-list", semester_id=semester_id)

    return render(request, "subjects/subject_create.html", {
        "semester_id": semester_id,
        "semesters": semesters,  # ✅ send this to template
    })

@login_required
def subject_update_view(request, subject_id):
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
            return redirect("subject-list", semester_id=semester_id)

    return render(request, "subjects/subject_update.html", {"subject": subject, "semester_id": semester_id})

@login_required
def subject_delete_view(request, subject_id):
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
            return redirect("subject-list", semester_id=semester_id)

    return render(request, "subjects/subject_delete.html", {
        "subject": subject,
        "semester_id": semester_id  # ✅ Include in context for cancel button
    })

#-------------------------------------------------------------------------------------------------------------------
#                       PAST QUESTIONS VIEWS 
#-------------------------------------------------------------------------------------------------------------------

@login_required
def pastQuestion_list_view(request, subject_id):
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
    return render(request, 'pastQuestions/pastQuestion_list.html', {'pastQuestions': pastQuestions, 'semester_id': semester_id, 'subject_id': subject_id,'subject': subject})

@login_required
def pastQuestion_detail_view(request, pastQuestion_id):
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

    return render(request, 'pastQuestions/pastQuestion_detail.html', {
        'pastQuestion': pastQuestion,
        'is_pdf': is_pdf,
    })


@login_required
def pastQuestion_create_view(request, subject_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to create past questions.")

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
        files = {
            'file': request.FILES.get('file')
        } if 'file' in request.FILES else {}

        api_url = f"http://127.0.0.1:8000/backend/oldQuestion-create/{subject_id}/"
        headers = {'Authorization': f'Token {token}'}
        response = requests.post(api_url, data=data, files=files, headers=headers)

        if response.status_code == 201:
            return redirect("pastQuestion-list", subject_id=subject_id)
        
    return render(request, "pastQuestions/pastQuestion_create.html", {
        "subject_id": subject_id,
    })

@login_required
def pastQuestion_update_view(request, pastQuestion_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to update past questions.")
    
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}
    api_url = f"http://127.0.0.1:8000/backend/oldQuestion-create/{pastQuestion_id}/"
    response = requests.get(api_url, headers=headers)
    pastQuestion = response.json() if response.status_code == 200 else {}

    subject_id = pastQuestion.get('subject')  # ✅ Extract subject_id from API

    if request.method == "POST":
        data = {
            "title": request.POST.get("title"),
            "year": request.POST.get("year"),
            "description": request.POST.get("description"),
            "subject": subject_id,  # include subject id in data if API requires it
        }

        files = {}
        file_upload = request.FILES.get("file")
        if file_upload:
            files["file"] = (file_upload.name, file_upload, file_upload.content_type)

        update_url = f"http://127.0.0.1:8000/backend/pastQuestion-update/{pastQuestion_id}/"
        update_response = requests.post(update_url, data=data, files=files, headers=headers)

        if update_response.status_code == 200:
            return redirect("pastQuestion-list", subject_id=subject_id)
        else:
            return render(request, "pastQuestions/pastQuestion_update.html", {
                "pastQuestion": pastQuestion,
                "subject_id": subject_id,
                "error": "Failed to update past question."
            })
    return render(request, "pastQuestions/pastQuestion_update.html", {
        "pastQuestion": pastQuestion,
        "subject_id": subject_id
    })

@login_required
def pastQuestion_delete_view(request, pastQuestion_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to delete past questions.")

    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}

    # Fetch past question data
    url = f"http://127.0.0.1:8000/backend/pastQuestion-delete/{pastQuestion_id}/"
    response = requests.get(url, headers=headers)
    pastQuestion = response.json() if response.status_code == 200 else {}

    if not pastQuestion:
        return HttpResponseNotFound("Past Question not found")
    
    subject_id = pastQuestion.get('subject')  # ✅ Get subject_id before deletion

    if request.method == 'POST':
        # DELETE request with headers
        delete_url = f"http://127.0.0.1:8000/backend/pastQuestion-delete/{pastQuestion_id}/"
        delete_response = requests.delete(delete_url, headers=headers)

        if delete_response.status_code in [200, 204]:
            return redirect('pastQuestion-list', subject_id=subject_id)
        
    return render(request, 'pastQuestions/pastQuestion_delete.html', {
            'error': 'Failed to delete past question.',
            'pastQuestion': pastQuestion,
            'subject_id': subject_id
    })
   
#-------------------------------------------------------------------------------------------------------------------
#                       SYLLABUS VIEWS 
#-------------------------------------------------------------------------------------------------------------------

@login_required
def syllabus_list_view(request, subject_id):
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}
    print(f"Sending request with headers: {headers}")

    api_url = f"http://127.0.0.1:8000/backend/syllabus-list/{subject_id}/"
    # Make the API request with the token
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        syllabus = response.json()
        # If syllabus is a list (empty or not), convert to None
        if isinstance(syllabus, list):
            syllabus = syllabus[0] if syllabus else None
    elif response.status_code == 401:
        print("Unauthorized access, check your token.")
        syllabus = []
    else:
        print(f"Error fetching syllabus: {response.status_code}, {response.text}")
        syllabus = []
    # ✅ Proper way to get subject_id
    try:
        subject = Subject.objects.get(id=subject_id)
        semester_id = subject.semester_id
    except Subject.DoesNotExist:
        semester_id = None  # fallback
    return render(request, 'syllabuses/syllabus_list.html', {'syllabus': syllabus, 'semester_id': semester_id, 'subject_id': subject_id})


@login_required
def syllabus_detail_view(request, syllabus_id):
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}
    print(f"Sending request with headers: {headers}")

    syllabus_url = f"http://127.0.0.1:8000/backend/syllabus-detail/{syllabus_id}/"

    response = requests.get(syllabus_url, headers=headers)
    if response.status_code == 200:
        syllabus = response.json()
    else:
        return HttpResponseNotFound("Syllabus not found")
    # ✅ Get subject_id from syllabus data
    subject_id = syllabus.get('subject')    
    if not subject_id:
        return HttpResponseNotFound("Subject not found for this syllabus")
    return render(request, 'syllabuses/syllabus_detail.html', {
        'syllabus': syllabus,
        'subject_id': subject_id,
    })

@login_required
def syllabus_create_view(request, subject_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to create syllabus.")

    if request.method == "POST":
        token = request.session.get('auth_token')
        if not token:
            return HttpResponseForbidden("Authentication token missing.")
        
        data = {
            "title": request.POST.get("title"),
            "description": request.POST.get("description"),
            "subject": subject_id,  # include subject id in data if API requires it
        }
        files = {
            'file': request.FILES.get('file')
        } if 'file' in request.FILES else {}

        api_url = f"http://127.0.0.1:8000/backend/syllabus-create/{subject_id}/"
        headers = {'Authorization': f'Token {token}'}
        response = requests.post(api_url, data=data, files=files, headers=headers)

        if response.status_code == 201:
            return redirect("syllabus-list", subject_id=subject_id)
        
    return render(request, "syllabuses/syllabus_create.html", {
        "subject_id": subject_id,
    })

@login_required
def syllabus_update_view(request, syllabus_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to update syllabus.")
    
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}
    api_url = f"http://127.0.0.1:8000/backend/syllabus-update/{syllabus_id}/"
    response = requests.get(api_url, headers=headers)
    syllabus = response.json() if response.status_code == 200 else {}

    subject_id = syllabus.get('subject')  # ✅ Extract subject_id from API

    if request.method == "POST":
        data = {
            "title": request.POST.get("title"),
            "description": request.POST.get("description"),
            "subject": subject_id,  # include subject id in data if API requires it
        }

        files = {}
        file_upload = request.FILES.get("file")
        if file_upload:
            files["file"] = (file_upload.name, file_upload, file_upload.content_type)

        update_url = f"http://127.0.0.1:8000/backend/syllabus-update/{subject_id}/"
        update_response = requests.post(update_url, data=data, files=files, headers=headers)
        if update_response.status_code == 200:
            return redirect("syllabus-list", subject_id=subject_id)
        
    return render(request, "syllabuses/syllabus_update.html", {
        "syllabus": syllabus,
        "subject_id": subject_id
    })

@login_required
def syllabus_delete_view(request, syllabus_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to delete syllabus.")

    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}

    # Fetch syllabus data
    url = f"http://127.0.0.1:8000/backend/syllabus-delete/{syllabus_id}/"
    response = requests.get(url, headers=headers)
    syllabus = response.json() if response.status_code == 200 else {}

    if not syllabus:
        return HttpResponseNotFound("Syllabus not found")
    subject_id = syllabus.get('subject')  # ✅ Get subject_id before deletion
    if request.method == 'POST':
        # DELETE request with headers
        delete_url = f"http://127.0.0.1:8000/backend/syllabus-delete/{subject_id}/"
        delete_response = requests.delete(delete_url, headers=headers)

        if delete_response.status_code in [200, 204]:
            return redirect('syllabus-list', subject_id=subject_id)
    return render(request, 'syllabuses/syllabus_delete.html', {
        'error': 'Failed to delete syllabus.',
        'syllabus': syllabus,
        'subject_id': subject_id
    })
#-------------------------------------------------------------------------------------------------------------------
#                       CHAPTERS VIEWS 
#-------------------------------------------------------------------------------------------------------------------

@login_required
def chapter_list_view(request, subject_id):
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}
    print(f"Sending request with headers: {headers}")
    api_url = f"http://127.0.0.1:8000/backend/chapter-list/{subject_id}/"
    # Make the API request with the token
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
    # ✅ Proper way to get subject_id
    try:
        subject = Subject.objects.get(id=subject_id)
        semester_id = subject.semester_id
    except Subject.DoesNotExist:
        semester_id = None  # fallback
    return render(request, 'chapters/chapter_list.html', {'chapters': chapters, 
'semester_id': semester_id, 'subject_id': subject_id})

@login_required
def chapter_detail_view(request, chapter_id):
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}
    print(f"Sending request with headers: {headers}")

    chapter_url = f"http://127.0.0.1:8000/backend/chapter-update/{chapter_id}/"
    response = requests.get(chapter_url, headers=headers)
    if response.status_code == 200:
        chapter = response.json()
    else:
        return HttpResponseNotFound("Chapter not found")
    # ✅ Get subject_id from chapter data
    subject_id = chapter.get('subject')
    if not subject_id:
        return HttpResponseNotFound("Subject not found for this chapter")
    return render(request, 'chapters/chapter_detail.html', {
        'chapter': chapter,
        'subject_id': subject_id,
    })

@login_required
def chapter_create_view(request, subject_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to create chapters.")

    if request.method == "POST":
        token = request.session.get('auth_token')
        if not token:
            return HttpResponseForbidden("Authentication token missing.")
        
        data = {
            "title": request.POST.get("title"),
            "description": request.POST.get("description"),
            "subject": subject_id,  # include subject id in data if API requires it
            "order": request.POST.get("order", 0)  # Optional order field
        }
        api_url = f"http://127.0.0.1:8000/backend/chapter-update/{subject_id}/"
        headers = {'Authorization': f'Token {token}'}
        response = requests.post(api_url, json=data, headers=headers)   

        if response.status_code == 201:
            return redirect("chapter-list", subject_id=subject_id)
    return render(request, "chapters/chapter_create.html", {
        "subject_id": subject_id,
    })
    

@login_required
def chapter_update_view(request, chapter_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to update chapters.")
    
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}
    api_url = f"http://127.0.0.1:8000/backend/chapter-update/{chapter_id}/"
    response = requests.get(api_url, headers=headers)
    chapter = response.json() if response.status_code == 200 else {}

    subject_id = chapter.get('subject')  # ✅ Extract subject_id from API
    if request.method == "POST":
        data = {
            "title": request.POST.get("title"),
            "description": request.POST.get("description"),
            "subject": subject_id,  # include subject id in data if API requires it
            "order": request.POST.get("order", 0)  # Optional order field
        }

        update_url = f"http://127.0.0.1:8000/backend/chapter-update/{subject_id}/"
        update_response = requests.post(update_url, json=data, headers=headers)

        if update_response.status_code == 200:
            return redirect("chapter-list", subject_id=subject_id)
        
    return render(request, "chapters/chapter_update.html", {
        "chapter": chapter,
        "subject_id": subject_id
    })


@login_required
def chapter_delete_view(request, chapter_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to delete chapters.")

    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}

    # Fetch chapter data
    url = f"http://127.0.0.1:8000/backend/chapter-delete/{chapter_id}/"
    response = requests.get(url, headers=headers)
    chapter = response.json() if response.status_code == 200 else {}

    if not chapter:
        return HttpResponseNotFound("Chapter not found")
    subject_id = chapter.get('subject')  # ✅ Get subject_id before deletion

    if request.method == 'POST':
        # DELETE request with headers
        delete_url = f"http://127.0.0.1:8000/backend/chapter-update/{subject_id}/"

        delete_response = requests.delete(delete_url, headers=headers)

        if delete_response.status_code in [200, 204]:
            return redirect('chapter-list', subject_id=subject_id)
        
    return render(request, 'chapters/chapter_delete.html', {
        'error': 'Failed to delete chapter.',
        'chapter': chapter,
        'subject_id': subject_id
    })
#-------------------------------------------------------------------------------------------------------------------
#                       Note VIEWS 
#-------------------------------------------------------------------------------------------------------------------
@login_required
def note_list_view(request, chapter_id):
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}
    print(f"Sending request with headers: {headers}")  # Debugging
    api_url = f'http://127.0.0.1:8000/backend/note-list/{chapter_id}/'  # Adjust the URL as per your API endpoint
     # Make the API request with the token
    response = requests.get(api_url,headers=headers)

    if response.status_code == 200:
        notes = response.json()
        print("API Response:", notes)  # Debugging
    elif response.status_code == 401:
        print("Unauthorized access, check your token.")
        notes = []
    else:
        print(f"Error fetching notes: {response.status_code}, {response.text}")  # Debugging
        notes = []
     # ✅ Proper way to get course_id
    try:
        chapter = Chapter.objects.get(id=chapter_id)
        subject_id = chapter.subject_id
    except Chapter.DoesNotExist:
        subject_id = None  # fallback
    return render(request, 'notes/note_list.html', {'notes': notes, 'subject_id': subject_id, 'chapter_id': chapter_id})


@login_required
def note_detail_view(request, note_id):
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}
    print(f"Sending request with headers: {headers}")
    note_url = f"http://127.0.0.1:8000/backend/note-detail/{note_id}/"

    response = requests.get(note_url, headers=headers)
    if response.status_code == 200:
        note = response.json()
    else:
        return HttpResponseNotFound("Note not found")
    
    # ✅ Get chapter_id from note data
    chapter_id = note.get('chapter')
    if not chapter_id:
        return HttpResponseNotFound("Chapter not found for this note")
    return render(request, 'notes/note_detail.html', {
        'note': note,
        'chapter_id': chapter_id,
    })

@login_required
def note_create_view(request, chapter_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to create notes.")

    if request.method == "POST":
        token = request.session.get('auth_token')
        if not token:
            return HttpResponseForbidden("Authentication token missing.")
        
        data = {
            "title": request.POST.get("title"),
            "description": request.POST.get("description"),
            "chapter": chapter_id,  # include chapter id in data if API requires it
        }
        files = {
            'file': request.FILES.get('file')
        } if 'file' in request.FILES else {}

        api_url = f"http://127.0.0.1:8000/backend/note-update/{chapter_id}/"
        headers = {'Authorization': f'Token {token}'}
        response = requests.post(api_url, data=data, files=files, headers=headers)
        if response.status_code == 201:
            return redirect("note-list", chapter_id=chapter_id)
    return render(request, "notes/note_create.html", {
        "chapter_id": chapter_id,
    })

@login_required
def note_update_view(request, note_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to update notes.")
    
    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}
    api_url = f"http://127.0.0.1:8000/backend/note-update/{note_id}/"
    response = requests.get(api_url, headers=headers)
    note = response.json() if response.status_code == 200 else {}
    chapter_id = note.get('chapter')  # ✅ Extract chapter_id from API
    if request.method == "POST":
        data = {
            "title": request.POST.get("title"),
            "description": request.POST.get("description"),
            "chapter": chapter_id,  # include subject id in data if API requires it
        }

        files = {}
        file_upload = request.FILES.get("file")
        if file_upload:
            files["file"] = (file_upload.name, file_upload, file_upload.content_type)

        update_url = f"http://127.0.0.1:8000/backend/note-update/{note_id}/"

        update_response = requests.post(update_url, data=data, files=files, headers=headers)
        if update_response.status_code == 200:
            return redirect("note-list", chapter_id=chapter_id)
    return render(request, "notes/note_update.html", {
        "note": note,
        "chapter_id": chapter_id
    })

@login_required
def note_delete_view(request, note_id):
    if not is_admin(request):
        return HttpResponseForbidden("You do not have permission to delete notes.")

    token = request.session.get('auth_token')
    if not token:
        return HttpResponseForbidden("Authentication token missing.")

    headers = {'Authorization': f'Token {token}'}

    # Fetch note data
    url = f"http://127.0.0.1:8000/backend/chapter-delete/{note_id}/"
    response = requests.get(url, headers=headers)
    note = response.json() if response.status_code == 200 else {}

    if not note:
        return HttpResponseNotFound("Note not found")
    chapter_id = note.get('chapter')
    # ✅ Get chapter_id before deletion
    if request.method == 'POST':
        # DELETE request with headers
        delete_url = f"http://127.0.0.1:8000/backend/chapter-delete/{note_id}/"
        delete_response = requests.delete(delete_url, headers=headers)
        
        if delete_response.status_code in [200, 204]:
            return redirect('note-list', chapter_id=chapter_id)

    return render(request, 'notes/note_delete.html', {
        'error': 'Failed to delete note.',
        'note': note,
        'chapter_id': chapter_id
    })
        
