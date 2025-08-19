from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, PostForm
from .models import Post
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404
import markdown
from django.utils.safestring import mark_safe

def home(request):
    query = request.GET.get('q')
    posts = Post.objects.order_by('-created')
    if query:
        posts = posts.filter(title__icontains=query)

    for post in posts:
        post.content_html = mark_safe(markdown.markdown(post.content, extensions=['fenced_code', 'codehilite']))
  
    
    return render(request, 'blog/home.html', {'posts': posts})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'blog/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'blog/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'blog/new_post.html', {'form': form})


@login_required
def edit_post(request, id):
    post = get_object_or_404(Post, id=id, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/new_post.html', {'form': form, 'view_title': 'Edit Post'})

@login_required
def delete_post(request, id):
    post = get_object_or_404(Post, id=id, author=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('home')
    return render(request, 'blog/delete_confirm.html', {'post': post})
