from functools import wraps

from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

from .models import Post


def user_is_author(func):
    @wraps(func)
    def check_user(request, *args, **kwargs):
        author = get_object_or_404(Post, pk=kwargs['post_id']).author
        if request.user == author:
            return func(request, *args, **kwargs)

        return redirect('posts:post_detail', post_id=kwargs['post_id'])

    return check_user
