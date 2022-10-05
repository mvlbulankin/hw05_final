from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User
from .utils import get_paginator


def index(request):
    """Выводит шаблон главной страницы"""
    page_obj = get_paginator(
        Post.objects.select_related("author", "group"), request
    )
    return render(request, "posts/index.html", {"page_obj": page_obj})


def group_posts(request, slug):
    """Выводит шаблон с группами постов"""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related("author")
    page_obj = get_paginator(posts, request)
    return render(
        request,
        "posts/group_list.html",
        {"group": group, "page_obj": page_obj},
    )


def profile(request, username):
    """Выводит шаблон профайла пользователя"""
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related("group")
    page_obj = get_paginator(posts, request)
    following = Follow.objects.filter(
        user__username=request.user, author=author
    )
    return render(
        request,
        "posts/profile.html",
        {
            "author": author,
            "posts": posts,
            "page_obj": page_obj,
            "following": following,
        },
    )


def post_detail(request, post_id):
    """Выводит детальное описание поста"""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post=post)
    return render(
        request,
        "posts/post_detail.html",
        {"post": post, "form": form, "comments": comments},
    )


@login_required
def post_create(request):
    """Создает новый пост"""
    form = PostForm(request.POST or None)
    if request.method != "POST" or not form.is_valid():
        return render(request, "posts/create_post.html", {"form": form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("posts:profile", post.author)


@login_required
def post_edit(request, post_id):
    """Редактирует пост"""
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect("posts:post_detail", post_id=post_id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if request.method != "POST" or not form.is_valid():
        return render(
            request,
            "posts/create_post.html",
            {"form": form, "is_edit": is_edit},
        )
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("posts:post_detail", post_id)


@login_required
def add_comment(request, post_id):
    """Добавляет комментарий"""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    """Добавляет комментарий"""
    template = "posts/follow.html"
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = get_paginator(posts, request)
    return render(request, template, {"page_obj": page_obj})


@login_required
def profile_follow(request, username):
    """Подписывает на автора"""
    user = request.user
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(author=author, user=user).exists()
    if user != author and not following:
        follow = Follow.objects.create(user=user, author=author)
        follow.save()
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    """Отписывает от автора"""
    user = get_object_or_404(User, username=username)
    unfollow, _ = Follow.objects.get_or_create(user=request.user, author=user)
    unfollow.delete()
    return redirect("posts:profile", username)
