from django.core.paginator import Paginator
from django.utils.text import Truncator
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import Group, Post, User
from .forms import PostForm


POSTS_PER_PAGE = 10
NUM_CHARS = 30


def index(request):
    template = "posts/index.html"
    posts = Post.objects.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = "posts/group_list.html"
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    author_posts = Post.objects.filter(author=author)
    author_posts_count = Post.objects.filter(author=author).count()
    paginator = Paginator(author_posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "author": author,
        "author_posts_count": author_posts_count,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    truncator = Truncator(post.text).chars(NUM_CHARS)
    author_posts_count = Post.objects.filter(author=post.author).count()
    title = f"Пост {truncator}"
    context = {
        "title": title,
        "post": post,
        "author_posts_count": author_posts_count,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    title = 'Создать новую запись'
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('posts:profile', username=request.user)
    context = {
        'form': form,
        'title': title,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    title = 'Редактировать запись'
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)

    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('posts:post_detail', post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'title': title,
        'is_edit': True
    }
    return render(request, template, context)
