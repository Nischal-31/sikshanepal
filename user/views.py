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

from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from django.http import JsonResponse

def Login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Get or create token
            token, created = Token.objects.get_or_create(user=user)

            # Store the token in the session
            request.session['auth_token'] = token.key  # Storing token in session

            # Debugging - Print session and token
            print("Session after login:", request.session)
            print("Stored Token:", request.session.get('auth_token'))
         
            return JsonResponse({'token': token.key})
        else:
            return JsonResponse({'error': 'Invalid username or password'}, status=400)

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