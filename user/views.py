from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login ,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm
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
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Create token if you want (optional)
            token, created = Token.objects.get_or_create(user=user)
            request.session['auth_token'] = token.key

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
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('user-profile')  # redirect back to profile page
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'user/profile.html', {'form': form})