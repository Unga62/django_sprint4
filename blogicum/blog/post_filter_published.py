from django.db.models import Count
from django.utils import timezone

from blog.models import Post


def post_filter_count(queryset):
    """Функция для подсчета комментариев в профиле."""
    return queryset.select_related(
        'author',
        'location',
        'category',
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


def post_published():
    """Функция возвращает проверки.

    Времени,
    флага публикации,
    публикации категории.
    """
    return post_filter_count(Post.objects).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )
