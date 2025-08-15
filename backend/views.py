import uuid
from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
import requests
from rest_framework import generics,status,permissions

from sikshanepal import settings
from .models import Subject,Syllabus,Chapter,Semester,Course,Note,PastQuestion
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from .serializers import ChangePasswordSerializer, PasswordResetConfirmSerializer, PasswordResetRequestSerializer, UserSerializer,SubjectSerializer,SyllabusSerializer,ChapterSerializer,SemesterSerializer,CourseSerializer,NotesSerializer,PastQuestionsSerializer, UserProfileSerializer      
from django.urls import reverse
from user.models import CustomUser
from .permissions import IsAdminUser, IsAdminOrReadOnly
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

#-----------------------------------------------------------------------------------------------------------------------------------------------
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

@api_view(['GET'])
@permission_classes([IsAuthenticated,IsAdminUser]) 
def apiOverview(request):
    api_urls = {
        "Users": {
            "List": request.build_absolute_uri(reverse('user-list-api')),
            "Detail View": request.build_absolute_uri(reverse('user-detail-api', args=['<id>'])),
            "Create": request.build_absolute_uri(reverse('user-create-api')),
            "Update": request.build_absolute_uri(reverse('user-update-api', args=['<id>'])),
            "Delete": request.build_absolute_uri(reverse('user-delete-api', args=['<id>'])),
            "Profile": request.build_absolute_uri(reverse('user-profile-api')),
            "Token Authentication": request.build_absolute_uri(reverse('api_token_auth')),
            # 🔹 New Endpoints for Password Management
            "Password Reset Request": request.build_absolute_uri(reverse('password_reset_api')),
            "Password Reset Confirm": request.build_absolute_uri(reverse('password_reset_confirm_api')),
            "Change Password": request.build_absolute_uri(reverse('change_password_api'))
        },
        "Courses": {
            "List": request.build_absolute_uri(reverse('course-list-api')),
            "Detail View": request.build_absolute_uri(reverse('course-detail-api', args=[1])),
            "Create": request.build_absolute_uri(reverse('course-create-api')),
            "Update": request.build_absolute_uri(reverse('course-update-api', args=[1])),
            "Delete": request.build_absolute_uri(reverse('course-delete-api', args=[1]))
        },
        "Semesters": {
            "List All": request.build_absolute_uri(reverse('semester-list-api')),
            "List by Course": request.build_absolute_uri(reverse('semester-list-by-course-api', args=[1])), 
            "Detail View": request.build_absolute_uri(reverse('semester-detail-api', args=[1])),
            "Create": request.build_absolute_uri(reverse('semester-create-api',args=[1])),
            "Update": request.build_absolute_uri(reverse('semester-update-api', args=[1])),
            "Delete": request.build_absolute_uri(reverse('semester-delete-api', args=[1]))
        },
        "Subjects": {
            "List All": request.build_absolute_uri(reverse('subject-list-api')),
            "List By Semester": request.build_absolute_uri(reverse('subject-list-by-semester-api', args=[1])),
            "Detail View": request.build_absolute_uri(reverse('subject-detail-api', args=[1])),
            "Create": request.build_absolute_uri(reverse('subject-create-api',args=[1])),
            "Update": request.build_absolute_uri(reverse('subject-update-api', args=[1])),
            "Delete": request.build_absolute_uri(reverse('subject-delete-api', args=[1]))
        },
        "PastQuestions": {
            "List All": request.build_absolute_uri(reverse('pastQuestion-list-api')),
            "List By Subject": request.build_absolute_uri(reverse('pastQuestion-list-by-subject-api', args=[1])),
            "Detail View": request.build_absolute_uri(reverse('pastQuestion-detail-api', args=[1])),
            "Create": request.build_absolute_uri(reverse('pastQuestion-create-api',args=[1])),
            "Update": request.build_absolute_uri(reverse('pastQuestion-update-api', args=[1])),
            "Delete": request.build_absolute_uri(reverse('pastQuestion-delete-api', args=[1]))
        },
        "Syllabus": {
            "List All": request.build_absolute_uri(reverse('syllabus-list-api')),
            "List By Subject": request.build_absolute_uri(reverse('syllabus-list-by-subject-api', args=[1])),
            "Detail View": request.build_absolute_uri(reverse('syllabus-detail-api', args=[1])),
            "Create": request.build_absolute_uri(reverse('syllabus-create-api',args=[1])),
            "Update": request.build_absolute_uri(reverse('syllabus-update-api', args=[1])),
            "Delete": request.build_absolute_uri(reverse('syllabus-delete-api', args=[1]))
        },
        "Chapters": {
            "List All": request.build_absolute_uri(reverse('chapter-list-api')),
            "List By Subject": request.build_absolute_uri(reverse('chapter-list-by-subject-api', args=[1])),
            "Detail View": request.build_absolute_uri(reverse('chapter-detail-api', args=[1])),
            "Create": request.build_absolute_uri(reverse('chapter-create-api',args=[1])),
            "Update": request.build_absolute_uri(reverse('chapter-update-api', args=[1])),
            "Delete": request.build_absolute_uri(reverse('chapter-delete-api', args=[1]))
        },
        "Notes": {
            "List All": request.build_absolute_uri(reverse('note-list-api')),
            "List By Chapter": request.build_absolute_uri(reverse('note-list-by-chapter-api', args=[1])),
            "Detail View": request.build_absolute_uri(reverse('note-detail-api', args=[1])),
            "Create": request.build_absolute_uri(reverse('note-create-api',args=[1])),
            "Update": request.build_absolute_uri(reverse('note-update-api', args=[1])),
            "Delete": request.build_absolute_uri(reverse('note-delete-api', args=[1]))
        }
    }

    return Response(api_urls)

#-------------------------------------------------------------------------------------------------------------------------------
#                           USERS
#----------------------------------------------------------------------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([ IsAdminUser])  # Only Admin can create users
def userCreate(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([ IsAdminOrReadOnly])  # Admin can list, others can view
def userList(request):
    users = CustomUser.objects.all().order_by('id')  # Ensuring ordered query
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([ IsAdminOrReadOnly])  # Admin can view details, others can only read
def userDetail(request, pk):
    try:
        user = CustomUser.objects.get(id=pk)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAdminUser])  # Only Admin can update users
def userUpdate(request, pk):
    try:
        user = CustomUser.objects.get(id=pk)  # Attempt to retrieve user by pk
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Proceed to update user fields (excluding user_type)
    username = request.data.get("username")
    email = request.data.get("email")
    phone_no = request.data.get("phone_no")
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")

    if username:
        user.username = username
    if email:
        user.email = email
    if phone_no:
        user.phone_no = phone_no
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name

    try:
        user.save()  # Attempt to save the updated user
    except Exception as e:
        return Response({'error': f"Failed to update user: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    # Return the updated user data
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])  # Only Admin can delete users
def userDelete(request, pk):
    try:
        user = CustomUser.objects.get(id=pk)
        user.delete()
        return Response({'message': 'User successfully deleted!'}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def userProfile(request):
    user = request.user
    if request.method == 'GET':
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    serializer = UserProfileSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        token, created = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "user": {
                "username": user.username,
                "email": user.email,
                "is_admin": user.user_type
            }
        })

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    serializer = PasswordResetRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = CustomUser.objects.get(email=serializer.validated_data['email'])
    token_generator = PasswordResetTokenGenerator()
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)

    reset_link = request.build_absolute_uri(
    reverse('password_reset_confirm_form', args=[uidb64, token])
)
     # 🔹 Print the link for testing
    print(f"Password reset link for {user.email}: {reset_link}")
    send_password_reset_email(user, reset_link)
    return Response({"detail": "Password reset link sent"}, status=status.HTTP_200_OK)

def send_password_reset_email(user, reset_link):
    subject = "Reset Your Password"
    from_email = "noreply@example.com"
    to_email = [user.email]

    # Render HTML content from a template
    html_content = render_to_string("emails/password_reset_email.html", {
        "user": user,
        "reset_link": reset_link,
    })

    # Plain text fallback
    text_content = f"Hello {user.username},\n\nClick the link below to reset your password:\n{reset_link}"

    email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"detail": "Password has been reset"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"detail": "Password updated successfully"}, status=status.HTTP_200_OK)
#-------------------------COURSE---------------------------------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated,IsAdminUser]) 
def courseCreate(request):
    serializer = CourseSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrReadOnly])
def courseList(request):
    courses = Course.objects.all().order_by('id')  # Ensure ordered query
    serializer = CourseSerializer(courses, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrReadOnly])
def courseDetail(request, pk):
    try:
        course = Course.objects.get(id=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CourseSerializer(course)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated,IsAdminUser])
def courseUpdate(request, pk):
    try:
        course = Course.objects.get(id=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

    # Updating fields
    name = request.data.get("name")
    description = request.data.get("description")
    image = request.FILES.get("image")

    if name:
        course.name = name
    if description:
        course.description = description
    if image:
        course.image = image

    try:
        course.save()
    except Exception as e:
        return Response({'error': f"Failed to update course: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = CourseSerializer(course)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated,IsAdminUser])
def courseDelete(request, pk):
    try:
        course = Course.objects.get(id=pk)
        course.delete()
        return Response({'message': 'Course successfully deleted!'}, status=status.HTTP_200_OK)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
#--------------------------------------------------------------------------------------------------------------------

#-------------------------SEMESTER-----------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated,IsAdminUser])
def semesterCreate(request, course_id):
    serializer = SemesterSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrReadOnly])
def semesterList(request):
    """
    Retrieve all semesters.
    """
    semesters = Semester.objects.all().order_by('id')
    serializer = SemesterSerializer(semesters, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrReadOnly])
def semesterListByCourse(request, course_id):
    """
    Retrieve semesters by course ID.
    """
    # Ensure we filter semesters by course_id
    semesters = Semester.objects.filter(course_id=course_id).order_by('id')
    
    # If no semesters are found for that course, return an empty list or a message
    if not semesters.exists():
        return Response({"detail": "No semesters found for this course."}, status=404)
    
    serializer = SemesterSerializer(semesters, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([ IsAuthenticated,IsAdminOrReadOnly]) 
def semesterDetail(request, pk):
    try:
        semester = Semester.objects.get(id=pk)
    except Semester.DoesNotExist:
        return Response({'error': 'Semester not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = SemesterSerializer(semester, many=False)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated,IsAdminUser]) 
def semesterUpdate(request, pk):
    try:
        # Fetch the semester object
        semester = Semester.objects.get(id=pk)
    except Semester.DoesNotExist:
        return Response({'error': 'Semester not found'}, status=status.HTTP_404_NOT_FOUND)

    # Get updated fields from the request data
    number = request.data.get("number")
    description = request.data.get("description")

    # Update the semester fields
    if number:
        semester.number = number
    if description:
        semester.description = description

    # Save the changes
    try:
        semester.save()
    except Exception as e:
        return Response({'error': f"Failed to update semester: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    # Return the updated data
    serializer = SemesterSerializer(semester)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated,IsAdminUser]) 
def semesterDelete(request, pk):
    try:
        semester = Semester.objects.get(id=pk)
        semester.delete()
        return Response('Semester successfully deleted!')
    except Semester.DoesNotExist:
        return Response({'error': 'Semester not found'}, status=status.HTTP_404_NOT_FOUND)
    
    
#--------------------------------------------------------------------------------------------------------------------

#-------------------------SUBJECT-----------------------------------    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def subjectCreate(request, semester_id):
    # Ensure the semester_id is valid
    try:
        semester = Semester.objects.get(id=semester_id)
    except Semester.DoesNotExist:
        return Response({"detail": "Semester not found."}, status=status.HTTP_404_NOT_FOUND)
    
    # Add the semester_id to the request data so that it can be used in the serializer
    request.data['semester'] = semester.id  # this will be passed to the serializer

    # Create the subject using the serializer
    serializer = SubjectSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()  # Save the new subject
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdminOrReadOnly]) 
def subjectList(request):
    """
    Retrieve all subjects.
    """
    subjects = Subject.objects.all().order_by('id')
    serializer = SubjectSerializer(subjects, many=True, context={'request': request})  # Add request context here
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrReadOnly])
def subjectListBySemester(request, semester_id):
    """
    Retrieve subjects by semester ID.
    """
    # Ensure we filter subjects by semester_id
    subjects = Subject.objects.filter(semester_id=semester_id).order_by('id')
    
    # If no subjects are found for that semester, return an empty list or a message
    if not subjects.exists():
        return Response({"detail": "No subjects found for this semester."}, status=404)
    
    # Use SubjectSerializer to serialize subjects, not SemesterSerializer
    serializer = SubjectSerializer(subjects, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([ IsAuthenticated,IsAdminOrReadOnly]) 
def subjectDetail(request,pk):
    subjects = Subject.objects.get(id=pk)
    serializer= SubjectSerializer(subjects,many=False)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated,IsAdminUser]) 
def subjectUpdate(request,pk):
    subject = get_object_or_404(Subject, id=pk)
    serializer = SubjectSerializer(instance=subject, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        print("Serializer errors:", serializer.errors)  # Debug print
        return Response(serializer.errors, status=400)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def subjectDelete(request, pk):
    try:
        subject = Subject.objects.get(id=pk)
    except Subject.DoesNotExist:
        return Response({'detail': 'Subject not found.'}, status=status.HTTP_404_NOT_FOUND)

    subject.delete()
    return Response({'detail': 'Subject successfully deleted!'}, status=status.HTTP_204_NO_CONTENT)
#--------------------------------------------------------------------------------------------------------------------

#-------------------------OLDQUESTIONS-----------------------------------   

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def pastQuestionCreate(request, subject_id):
    # Ensure the subject_id is valid
    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        return Response({"detail": "Subject not found."}, status=status.HTTP_404_NOT_FOUND)

    # Add the subject_id to the request data so that it can be used in the serializer
    data = request.data.copy()  # Copy request data to modify safely
    data['subject'] = subject.id  # Assign correct subject_id

    # Create the past question using the serializer
    serializer = PastQuestionsSerializer(data=data)

    if serializer.is_valid():
        serializer.save()  # Save the new past question
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrReadOnly]) 
def pastQuestionList(request):
    pastquestions = PastQuestion.objects.all().order_by('id')
    serializer = PastQuestionsSerializer(pastquestions, many=True,context={'request':request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrReadOnly])
def pastQuestionListBySubject(request, subject_id):
    """
    Retrieve pastQuestions by subject ID.
    """
    # Ensure we filter pastQuestions by subject_id
    pastQuestions = PastQuestion.objects.filter(subject_id=subject_id).order_by('id')
    
    # If no pastQuestions are found for that subject, return an empty list or a message
    if not pastQuestions.exists():
        return Response({"detail": "No pastQuestions found for this subject."}, status=404)
    
    # Use PastQuestionSerializer to serialize subjects, not SemesterSerializer
    serializer = PastQuestionsSerializer(pastQuestions, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrReadOnly]) 
def pastQuestionDetail(request,pk):
    pastquestion = PastQuestion.objects.get(id=pk)
    serializer= PastQuestionsSerializer(pastquestion,many=False)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated,IsAdminUser]) 
def pastQuestionUpdate(request, pk):
    try:
        pastquestion = PastQuestion.objects.get(id=pk)
    except PastQuestion.DoesNotExist:
        return Response({"detail": "Past question not found"}, status=404)

    serializer = PastQuestionsSerializer(instance=pastquestion, data=request.data, partial=True)  # allow partial updates

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=200)
    
    return Response(serializer.errors, status=400)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated,IsAdminUser]) 
def pastQuestionDelete(request,pk):
    pastquestion = PastQuestion.objects.get(id=pk)
    pastquestion.delete()
    return Response('Note successfully Deleted!')

#--------------------------------------------------------------------------------------------------------------------

#-------------------------SYLLABUS-----------------------------------    


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def syllabusCreate(request, subject_id):
    # Ensure the subject_id is valid
    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        return Response({"detail": "Subject not found."}, status=status.HTTP_404_NOT_FOUND)

    # Add the subject_id to the request data so that it can be used in the serializer
    data = request.data.copy()  # Copy request data to modify safely
    data['subject'] = subject.id  # Assign correct subject_id

    # Create the past question using the serializer
    serializer = SyllabusSerializer(data=data)

    if serializer.is_valid():
        serializer.save()  # Save the new syllabus
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrReadOnly]) 
def syllabusList(request):
    syllabuses = Syllabus.objects.all().order_by('id')
    serializer = SyllabusSerializer(syllabuses, many=True,context={'request':request})

    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrReadOnly])
def syllabusListBySubject(request, subject_id):
    """
    Retrieve syllabus by subject ID.
    """
    # Ensure we filter syllabus by subject_id
    syllabus = Syllabus.objects.filter(subject_id=subject_id).order_by('id')
    
    # If no syllabus are found for that subject, return an empty list or a message
    if not syllabus.exists():
        return Response({"detail": "No syllabus found for this subject."}, status=404)
    
    # Use SyllabusSerializer to serialize subjects, not SemesterSerializer
    serializer = SyllabusSerializer(syllabus, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrReadOnly]) 
def syllabusDetail(request, pk):
    try:
        syllabus = Syllabus.objects.get(id=pk)
    except Syllabus.DoesNotExist:
        return Response({'error': 'Syllabus not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = SyllabusSerializer(syllabus, many=False)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated,IsAdminUser]) 
def syllabusUpdate(request, pk):
    try:
        syllabus = Syllabus.objects.get(id=pk)
    except Syllabus.DoesNotExist:
        return Response({'error': 'Syllabus not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = SyllabusSerializer(instance=syllabus, data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated,IsAdminUser]) 
def syllabusDelete(request, pk):
    try:
        syllabus = Syllabus.objects.get(id=pk)
        syllabus.delete()
        return Response('Syllabus successfully deleted!')
    except Syllabus.DoesNotExist:
        return Response({'error': 'Syllabus not found'}, status=status.HTTP_404_NOT_FOUND)

#--------------------------------------------------------------------------------------------------------------------

#-------------------------CHAPTER-----------------------------------    

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def chapterCreate(request, subject_id):
    # Ensure the subject_id is valid
    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        return Response({"detail": "Subject not found."}, status=status.HTTP_404_NOT_FOUND)

    # Add the subject_id to the request data so that it can be used in the serializer
    data = request.data.copy()  # Copy request data to modify safely
    data['subject'] = subject.id  # Assign correct subject_id

    # Create the past question using the serializer
    serializer = ChapterSerializer(data=data)

    if serializer.is_valid():
        serializer.save()  # Save the new chapter
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([ IsAuthenticated,IsAdminOrReadOnly]) 
def chapterList(request):
    chapters = Chapter.objects.all().order_by('id')
    serializer = ChapterSerializer(chapters, many=True,context={'request':request})

    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrReadOnly])
def chapterListBySubject(request, subject_id):
    """
    Retrieve chapter subject ID.
    """
    # Ensure we filter chapters by subject_id
    chapters = Chapter.objects.filter(subject_id=subject_id).order_by('id')
    
    # If no chapters are found for that subject, return an empty list or a message
    if not chapters.exists():
        return Response({"detail": "No chapters found for this subject."}, status=404)
    
    # Use ChapterSerializer to serialize subjects, not SemesterSerializer
    serializer = ChapterSerializer(chapters, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrReadOnly]) 
def chapterDetail(request, pk):
    try:
        chapter = Chapter.objects.get(id=pk)
    except Chapter.DoesNotExist:
        return Response({'error': 'Chapter not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ChapterSerializer(chapter, many=False)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated,IsAdminUser]) 
def chapterUpdate(request, pk):
    try:
        chapter = Chapter.objects.get(id=pk)
    except Chapter.DoesNotExist:
        return Response({'error': 'Chapter not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ChapterSerializer(instance=chapter, data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated,IsAdminUser]) 
def chapterDelete(request, pk):
    try:
        chapter = Chapter.objects.get(id=pk)
        chapter.delete()
        return Response('Chapter successfully deleted!')
    except Chapter.DoesNotExist:
        return Response({'error': 'Chapter not found'}, status=status.HTTP_404_NOT_FOUND)

#-----------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------

#-------------------------NOTES-----------------------------------  

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def noteCreate(request, chapter_id):
    # Ensure the chapter_id is valid
    try:
        chapter = Chapter.objects.get(id=chapter_id)
    except Chapter.DoesNotExist:
        return Response({"detail": "Chapter not found."}, status=status.HTTP_404_NOT_FOUND)

    # Add the chapter_id to the request data so that it can be used in the serializer
    data = request.data.copy()  # Copy request data to modify safely
    data['chapter'] = chapter.id  # Assign correct chapter_id

    if request.method == 'POST':
        data = request.data.copy()
        
        # Extract file from request.FILES
        file = request.FILES.get('file')

        # Ensure a file was uploaded
        if not file:
            return Response({'error': 'No file uploaded'}, status=400)
        
    # Create the past question using the serializer
    serializer = NotesSerializer(data=data)

    if serializer.is_valid():
        serializer.save(file=file)  # Save the new note
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrReadOnly]) 
def noteList(request):
    notes = Note.objects.all().order_by('id')
    serializer = NotesSerializer(notes, many=True,context={'request':request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrReadOnly])
def noteListByChapter(request, chapter_id):
    """
    Retrieve notes by chapter ID.
    """
    # Ensure we filter notes by chapter_id
    notes = Note.objects.filter(chapter_id=chapter_id).order_by('id')
    
    # If no notes are found for that chapter, return an empty list or a message
    if not notes.exists():
        return Response({"detail": "No notes found for this chapter."}, status=404)
    
    # Use NoteSerializer to serialize chapters, not SemesterSerializer
    serializer = NotesSerializer(notes, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrReadOnly]) 
def noteDetail(request,pk):
    note = Note.objects.get(id=pk)
    serializer= NotesSerializer(note,many=False)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated,IsAdminUser]) 
def noteUpdate(request,pk):
    note = Note.objects.get(id=pk)
    serializer=NotesSerializer(instance=note ,data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated,IsAdminUser]) 
def noteDelete(request,pk):
    note = Note.objects.get(id=pk)
    note.delete()
    return Response('Note successfully Deleted!')