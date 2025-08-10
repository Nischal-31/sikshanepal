from rest_framework import serializers
from django.conf import settings
from user.models import CustomUser
from .models import Subject,Semester,Syllabus,Chapter,Course,Note,PastQuestion

class NotesSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()
    class Meta:
        model = Note
        fields = ['id', 'chapter', 'title', 'description', 'file']
    
    def get_file(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        elif obj.file:
            return obj.file.url
        return None


class ChapterSerializer(serializers.ModelSerializer):
    notes = NotesSerializer(many=True, read_only=True)

    class Meta:
        model = Chapter
        fields = ['id', 'subject', 'title', 'description', 'order', 'notes']


class PastQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PastQuestion
        fields = ['id', 'subject', 'year', 'title', 'description', 'file']


class SyllabusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Syllabus
        fields = ['id', 'subject', 'objectives', 'file']


class SubjectSerializer(serializers.ModelSerializer):
    syllabus = SyllabusSerializer(read_only=True)
    past_questions = PastQuestionsSerializer(many=True, read_only=True)
    chapters = ChapterSerializer(many=True, read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'semester', 'name', 'code', 'credits', 'description', 'syllabus', 'past_questions', 'chapters']


class SemesterSerializer(serializers.ModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)

    class Meta:
        model = Semester
        fields = ['id', 'course', 'number', 'description', 'subjects']


class CourseSerializer(serializers.ModelSerializer):
    semesters = SemesterSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'image', 'semesters']

    def get_image(self, obj):
        # Ensure that we are using the request context to build the absolute URL
        request = self.context.get('request')  # Get the current request
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        elif obj.image:
            return obj.image.url
        return None

#=======================================================================================================================================

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone_no', 'first_name', 'last_name', 'terms_agree', 'remember_me', 'user_type']

    def create(self, validated_data):
        # Ensure the user_type is set, defaulting to 'normal' if not provided
        user_type = validated_data.get('user_type', 'normal')
        user = CustomUser.objects.create(**validated_data)
        user.user_type = user_type
        user.save()
        return user
    
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile_picture']  # Add your custom fields here

