from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User
from .forms import PostForm
from django.contrib.auth.decorators import login_required


COUNT_POSTS: int = 10
SIMBOLS: int = 30


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.select_related()
    paginator = Paginator(posts, COUNT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.groups.select_related('group')
    paginator = Paginator(posts, COUNT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    user = get_object_or_404(User, username=username)
    posts = user.posts.select_related('author')
    counter_posts = posts.count()
    paginator = Paginator(posts, COUNT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'posts': posts,
        'page_obj': page_obj,
        'author': user,
        'counter_posts': counter_posts,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    counter_posts = post.author.posts.count()
    title = post.text[:SIMBOLS]
    context = {
        'post': post,
        'title': title,
        'counter_posts': counter_posts,
    }
    return render(request, template, context)


def tech(request):
    template = 'about/tech.html'
    return render(request, template)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm()
    context = {
        'form': form,
    }
    if request.method == 'POST':
        post = PostForm(request.POST, files=request.FILES or None,)
        if post.is_valid():
            post = post.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author)
        return render(request, template, context)
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = PostForm(
            request.POST,
            instance=post
        )
        context = {
            'form': form,
            'post': post,
            'is_edit': True,
        }
        if post.author.username != request.user.username:
            return redirect('posts:post_detail', post_id)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:post_detail', post_id)
        return render(request, template, context)
    form = PostForm(instance=post, files=request.FILES or None,)
    context = {
        'form': form,
        'post': post,
        'is_edit': True,
    }
    return render(request, template, context)
