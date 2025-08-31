from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from requests import post
from .models import Post

def blog_list(request):
    posts = Post.objects.all().order_by('-created_at')
    categories = Post.objects.values_list('category', flat=True).distinct()
    category_choices = Post.CATEGORY_CHOICES  # for dropdown

    # Handle create post in the same view
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        extra_details = request.POST.get('extra_details')
        category = request.POST.get('category')
        image = request.FILES.get('image')

        if title and content and category:
            new_post= Post.objects.create(
                title=title,
                content=content,
                extra_details=extra_details,
                category=category,
                image=image,
            )

            # Trigger FCM notification
            from sikshanepal.firebase import send_blog_notification
            try:
                send_blog_notification(
                    title="📢 New Blog Added!",
                    body=f"{new_post.title} was just published.",
                    blog_id=new_post.id
                )
                print(f"[DEBUG] Notification sent for blog: {new_post.title} (ID: {new_post.id})")
            except Exception as e:
                print(f"[ERROR] Failed to send notification: {e}")

            messages.success(request, "Post created successfully.")
            return redirect('blog_list')
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(request, 'blog/blog_list.html', {
        'posts': posts,
        'categories': categories,
        'category_choices': category_choices,
    })


def blog_detail(request, id):
    post = get_object_or_404(Post, id=id)
    next_post = Post.objects.filter(created_at__gt=post.created_at).order_by('created_at').first()
    return render(request, 'blog/blog_detail.html', {'post': post, 'next_post': next_post})


@login_required
def blog_update(request, id):
    post = get_object_or_404(Post, id=id)

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        extra_details = request.POST.get('extra_details')
        category = request.POST.get('category')
        image = request.FILES.get('image')

        if title and content and category:
            post.title = title
            post.content = content
            post.extra_details = extra_details
            post.category = category
            if image:
                post.image = image
            post.save()
            messages.success(request, "Post updated successfully.")
            return redirect('blog_list')
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(request, 'blog/blog_update.html', {'post': post})


@login_required
def blog_delete(request, id):
    post = get_object_or_404(Post, id=id)

    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted successfully.")
        return redirect('blog_list')

    return render(request, 'blog/blog_delete.html', {'post': post})
