from django.shortcuts import render, get_object_or_404, redirect
from .models import Post
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required

def blog_list(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        extra_details = request.POST.get('extra_details')
        image = request.FILES.get('image')

        if title and content:
            slug = slugify(title)
            post = Post.objects.create(
                title=title,
                slug=slug,
                content=content,
                extra_details=extra_details,
                image=image,
                author=request.user
            )
            return redirect('blog_list')
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'blog/blog_list.html', {'posts': posts})

def blog_detail(request, slug):
    # Get the current post by slug
    post = get_object_or_404(Post, slug=slug)

    # Fetch the next post, you can adjust the ordering logic as per your requirements
    next_post = Post.objects.filter(created_at__gt=post.created_at).order_by('created_at').first()

    # Pass post and next_post to the template
    return render(request, 'blog/blog_detail.html', {'post': post, 'next_post': next_post})
