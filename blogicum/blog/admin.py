from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Category, Post, Location, Comment


@admin.register(Post)
class PostModel(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at',
    )

    list_editable = (
        'is_published',
        'category',
        'pub_date',
        'location',
        'author'
    )

    search_fields = ('title',)
    list_filter = ('author', 'category', 'is_published')
    list_display_links = ('title',)


@admin.register(Category)
class CategoryModel(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'slug',
        'is_published',
        'created_at',
    )
    list_editable = (
        'is_published',
        'slug',
        'description',
    )

    search_fields = ('title',)


@admin.register(Location)
class LocationModel(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
        'created_at',
    )


@admin.register(Comment)
class CommetModel(admin.ModelAdmin):
    list_display = (
        'author',
        'text',
        'created_at',
        'post',
    )


admin.site.unregister(Group)
