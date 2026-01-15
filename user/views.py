from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login ,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
import requests

from user.models import CustomUser
from user.signals import User
from .forms import UserRegisterForm, UserUpdateForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from backend.permissions import IsAdminUser, IsAdminOrReadOnly
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view,permission_classes
from .forms import ProfileUpdateForm
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login

########### register here ##################################### 
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()  # This automatically triggers the signal to send the email

            messages.success(request, 'Your account has been created! You are now able to log in.')
            return redirect('login')  # Ensure 'login' matches the name in your urls.py

    else:
        form = UserRegisterForm()
    
    return render(request, 'user/register.html', {'form': form, 'title': 'Register Here'})

def Login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        remember = request.POST.get('remember')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Create token if you want (optional)
            token, created = Token.objects.get_or_create(user=user)
            request.session['auth_token'] = token.key

            # Handle "Remember me"
            if not remember:
                # Session will expire when the browser closes
                request.session.set_expiry(0)
            else:
                # Session will last 30 days (you can change this)
                request.session.set_expiry(60 * 60 * 24 * 30)

            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('index')  # Redirect to your home/dashboard page
        else:
            messages.error(request, "Invalid username or password")

    form = AuthenticationForm()
    return render(request, 'user/login.html', {'form': form, 'title': 'Log In'})


def logout_view(request):
    logout(request)
    return redirect('index') 

@login_required
def profile_view(request):
    user = request.user
    token, created = Token.objects.get_or_create(user=user)  # create token if missing

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile')
    else:
        form = ProfileUpdateForm(instance=user)

    return render(request, 'user/profile.html', {
        'form': form,
        'user': user,           # pass user
        'token': token.key       # pass token for AJAX
    })

def password_reset_form(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # Validate email exists in DB (optional)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(email=email).exists():
            return render(request, 'user/password_reset.html', {"error": "Email not found"})

        # Build API URL (strip trailing spaces)
        api_url = request.build_absolute_uri('/backend/password-reset/').strip()

        # Call DRF endpoint
        try:
            response = requests.post(api_url, json={"email": email})
            response.raise_for_status()  # raises exception if status_code >= 400
        except requests.exceptions.RequestException as e:
            return render(request, 'user/password_reset.html', {
                "error": f"Something went wrong: {str(e)}"
            })

        # Success
        return render(request, 'user/password_reset_done.html', {"email": email})

    return render(request, 'user/password_reset.html')


def password_reset_confirm_view(request, uidb64, token):
    # Render a page where user can enter new password
    context = {'uidb64': uidb64, 'token': token}
    return render(request, 'user/password_reset_confirm.html', context)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def admin_view_user_profile(request, user_id):
    """
    Admin dashboard view to see a specific user's profile
    """
    user = get_object_or_404(User, id=user_id)
    return render(request, 'dashboard/admin_view_user.html', {'user': user})

def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)  # <-- important
        if form.is_valid():
            form.save()
            messages.success(request, f"{user.username} updated successfully!")
            return redirect('users')
    else:
        form = UserUpdateForm(instance=user)
    
    return render(request, 'dashboard/edit_user.html', {'form': form, 'user': user})