from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_http_methods

from .models import Follow, Group, Post, User, Comment
from .forms import PostForm, CommentForm
from .decorators import user_is_author


@require_GET
def index(request):
    """The index function submit 10 posts ordered by date to index.html template.
    """
    template = 'posts/index.html'
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


@require_GET
def group_posts(request, slug):
    """The group_post function submit 10 posts of a group
    ordered by date to the group page.
    It recieves slug of a group as a parameter.
    """
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    posts = group.posts.all()

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


@require_GET
def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = False
    user = request.user

    if user.is_authenticated:
        check_following = author.following.values_list('user', flat=True)
        if user.pk in check_following:
            following = True

    posts = author.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    template = 'posts/profile.html'
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


@require_GET
def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    comments = Comment.objects.filter(post=post_id)

    template = 'posts/post_detail.html'
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
@require_http_methods(['GET', 'POST'])
def post_create(request):
    template = 'posts/create_post.html'

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user

        post.save()
        return redirect('posts:profile', username=request.user.username)

    return render(request, template, {'form': form})


@login_required
@user_is_author
@require_http_methods(['GET', 'POST'])
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)

    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }

    return render(request, template, context)


@login_required
@require_http_methods(['GET', 'POST'])
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
@require_GET
def follow_index(request):
    user = request.user
    authors = user.follower.values_list('author', flat=True)
    posts = Post.objects.filter(author__id__in=authors)

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
@require_GET
def profile_follow(request, username):
    # нам же не нужно использовать get_object_or_404, тк автор точно есть?
    author = User.objects.get(username=username)
    current_user = request.user
    check_following = author.following.values_list('user', flat=True)

    if current_user != author:
        if current_user.pk not in check_following:
            check_following.create(user=current_user, author=author)
    return redirect('posts:profile', username=username)


@login_required
@require_GET
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    current_user = request.user

    if current_user != author:
        check_following = Follow.objects.filter(
            user=current_user,
            author=author
        )
        if check_following.exists():
            check_following.delete()
    return redirect('posts:profile', username=username)
