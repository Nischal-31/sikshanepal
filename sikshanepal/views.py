from django.shortcuts import render

def index_view(request):
    return render(request, 'index.html')

def about_view(request):
    return render(request, 'about.html')

def blog_view(request):
    return render(request, 'blog.html')

def contact_view(request):
    return render(request, 'contact.html')

def course_view(request):
    return render(request, 'course.html')

def course_inner_view(request):
    return render(request, 'course-inner.html')

def post_view(request):
    return render(request, 'post.html')

def subscription_view(request):
    return render(request, 'subscription.html')

def checkout_view(request):
    return render(request, 'checkout.html')

