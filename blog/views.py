from django.shortcuts import render, get_object_or_404
from .models import Post

def blog(request):
    posts = Post.objects.all()
    return render(request, "blog/blog.html", {"posts": posts})

def post_detalle(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, "blog/post_detalle.html", {"post": post})

