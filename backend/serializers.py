from rest_framework import serializers
from django.conf import settings
from user.models import CustomUser
from .models import Subject,Semester,Syllabus,Chapter,Course,Note,PastQuestion

from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

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

# 🔹 Forgot Password Request
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("No account found with this email")
        return value


# 🔹 Reset Password Confirm
class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data['uidb64']))
            self.user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            raise serializers.ValidationError({"uidb64": "Invalid UID"})

        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(self.user, data['token']):
            raise serializers.ValidationError({"token": "Invalid or expired token"})

        return data

    def save(self):
        self.user.set_password(self.validated_data['new_password'])
        self.user.save()
        return self.user


# 🔹 Change Password (Logged-in Users)
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
