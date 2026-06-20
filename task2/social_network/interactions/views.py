from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from posts.models import Post
from .models import Like, Follow, Comment
from .forms import CommentForm


@login_required
def toggle_like_view(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
    return redirect(request.META.get('HTTP_REFERER', 'feed'))


@login_required
def add_comment_view(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            messages.success(request, 'Commentaire ajouté !')
    return redirect('post_detail', pk=post_id)


@login_required
def toggle_follow_view(request, username):
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        messages.error(request, 'Vous ne pouvez pas vous suivre vous-même.')
        return redirect('profile', username=username)

    follow, created = Follow.objects.get_or_create(
        follower=request.user, following=target_user
    )
    if not created:
        follow.delete()
        messages.info(request, f"Vous ne suivez plus {username}.")
    else:
        messages.success(request, f"Vous suivez maintenant {username} !")

    return redirect('profile', username=username)
