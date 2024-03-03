from django.db import models
from django.contrib.auth import get_user_model

from abstractions.models import PublishedModel, TitleModel
from blog.config import MAX_LINE_SIZE, LINE_SLICE

User = get_user_model()


class Post(PublishedModel, TitleModel):
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(auto_now_add=False,
                                    verbose_name='Дата и время публикации',
                                    help_text='Если установить дату и время в'
                                    ' будущем — можно делать'
                                    ' отложенные публикации.')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        related_name='posts',
        null=True,
        verbose_name='Категория',
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)


class Category(PublishedModel, TitleModel):
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(unique=True, verbose_name='Идентификатор',
                            help_text='Идентификатор страницы для URL;'
                            ' разрешены символы латиницы, цифры,'
                            ' дефис и подчёркивание.')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Location(PublishedModel):
    name = models.CharField(max_length=MAX_LINE_SIZE,
                            verbose_name='Название места')

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        return self.name[:LINE_SLICE]
