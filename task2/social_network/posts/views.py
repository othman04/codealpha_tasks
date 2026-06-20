from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from interactions.models import Follow, Like
from .forms import PostForm
from .models import Post


@login_required
def feed_view(request):
    following_ids = Follow.objects.filter(
        follower=request.user
    ).values_list('following_id', flat=True)
    user_ids = list(following_ids) + [request.user.id]
    posts = Post.objects.filter(author_id__in=user_ids).select_related(
        'author', 'author__profile'
    ).prefetch_related('likes', 'comments')

    liked_post_ids = set(
        Like.objects.filter(user=request.user).values_list('post_id', flat=True)
    )

    return render(request, 'posts/feed.html', {
        'posts': posts,
        'liked_post_ids': liked_post_ids,
    })


@login_required
def create_post_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Publication créée avec succès !')
            return redirect('feed')
    else:
        form = PostForm()

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_detail_view(request, pk):
    post = get_object_or_404(
        Post.objects.select_related('author', 'author__profile'),
        pk=pk
    )
    comments = post.comments.select_related('user', 'user__profile')
    is_liked = Like.objects.filter(user=request.user, post=post).exists()

    return render(request, 'posts/post_detail.html', {
        'post': post,
        'comments': comments,
        'is_liked': is_liked,
    })


@login_required
def edit_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, "Vous ne pouvez modifier que vos propres publications.")
        return redirect('post_detail', pk=pk)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Publication modifiée avec succès !')
            return redirect('post_detail', pk=pk)
    else:
        form = PostForm(instance=post)

    return render(request, 'posts/edit_post.html', {'form': form, 'post': post})


@login_required
def delete_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, "Vous ne pouvez supprimer que vos propres publications.")
        return redirect('post_detail', pk=pk)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Publication supprimée.')
        return redirect('feed')

    return render(request, 'posts/delete_post.html', {'post': post})
