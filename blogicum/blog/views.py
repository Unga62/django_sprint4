from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.utils import timezone

from blog.models import Post, Category
from blog.config import POST_SLICE


def postpublished():
    """Функция возвращает проверку времени, флага публикации,
    проверку публикации категории
    """
    return (
        Q(pub_date__date__lt=timezone.now()) & Q(is_published=True)
        & Q(category__is_published=True)
    )


def index(request):
    """Функция возвращает все посты на главной странице"""
    templates = 'blog/index.html'
    posts = Post.objects.select_related('author').filter(
        Q(postpublished()))[:POST_SLICE]
    context = {'posts': posts}
    return render(request, templates, context)


def post_detail(request, id):
    """Функция возвращает детализированную информацию поста"""
    templates = 'blog/detail.html'
    post = get_object_or_404(Post, postpublished(), pk=id)
    context = {'post': post}
    return render(request, templates, context)


def category_posts(request, category_slug):
    """Функция возвращает страницу категории публикации"""
    templates = 'blog/category.html'
    category = get_object_or_404(Category, slug=category_slug,
                                 is_published=True)
    posts = category.posts.filter(postpublished()
                                  & Q(category__slug=category_slug))
    context = {'category': category, 'post_list': posts}
    return render(request, templates, context)
