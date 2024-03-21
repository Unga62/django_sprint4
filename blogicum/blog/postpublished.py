from django.db.models import Count
from django.utils import timezone

from blog.models import Post


def post_published():
    """Функция возвращает проверки.

    Времени,
    флага публикации,
    публикации категории.
    """
    return Post.objects.select_related(
        'author',
        'location',
        'category',
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


def post_profile():
    """Функция для подсчета комментариев в профиле."""
    return Post.objects.annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
