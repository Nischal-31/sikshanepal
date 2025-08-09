from django import forms
from .models import CustomUser  # Import your custom user model
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    phone_no = forms.CharField(max_length=20)
    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=20)
    terms_agree = forms.BooleanField(required=True, label="I Agree to Terms and Conditions")
    remember_me = forms.BooleanField(required=False, label="Remember Me")
    
    
    class Meta:
        model = CustomUser  # Make sure to point to your custom user model
        fields = ['username', 'email', 'phone_no', 'first_name', 'last_name', 'password1', 'password2','user_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set form to horizontal layout
        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4 col-form-label text-md-end'  # Labels on the left
        self.helper.field_class = 'col-md-8'  # Fields on the right
        
        # Define layout for crispy forms
        self.helper.layout = Layout(
            Row(Column(Field('username'))),
            Row(Column(Field('email'))),
            Row(Column(Field('phone_no'))),

            # First Name and Last Name in the same row (horizontal)
            Row(
                Column(Field('first_name'), css_class='col-md-6'),
                Column(Field('last_name'), css_class='col-md-6'),
            ),

            Row(Column(Field('password1'))),
            Row(Column(Field('password2'))),

            # Terms and Remember Me checkboxes
            Row(
                Column(Field('terms_agree'), css_class='col-md-6'),
                Column(Field('remember_me'), css_class='col-md-6'),
            ),

            Submit('submit', 'Continue', css_class='btn btn-primary w-100')
        )
    def clean_user_type(self):
        user_type = self.cleaned_data.get('user_type')
        # If it's a Google signup, automatically set the user type to "normal"
        if not user_type:
            user_type = 'normal'
        return user_type 

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_no', 'first_name', 'last_name', 'profile_picture']