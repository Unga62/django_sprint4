from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    # просмотор всех постов и отдельного поста
    path('', views.PostIndexView.as_view(), name='index'),
    path('posts/<int:id>/', views.PostDetailView.as_view(),
         name='post_detail'),

    # создание нового поста
    path('posts/create/', views.PostCreateViews.as_view(), name='create_post'),

    # редактирование поста
    path('posts/<int:id>/edit/', views.PostEditView.as_view(),
         name='edit_post'),

    # удаление поста
    path('posts/<int:id>/delete/', views.PostDeleteView.as_view(),
         name='delete_post'),

    # комментирование поста
    path('posts/<int:id>/comment', views.PostCommentView.as_view(),
         name='add_comment'),

    # редактирование комментария поста
    path('posts/<int:id>/edit_comment/<int:comment_id>/',
         views.PostEditCommentView.as_view(),
         name='edit_comment'),

    # удаление комментария к посту
    path('posts/<int:id>/delete_comment/<int:comment_id>/',
         views.PostDeleteCommentView.as_view(),
         name='delete_comment'),

    path('category/<slug:category_slug>/', views.CategoryPostsView.as_view(),
         name='category_posts'),

    # страницы профиля пользователя и редактирование страницы
    path('profile/<slug:username>/', views.ProfileViews.as_view(),
         name='profile'),
    path('profile/edit_profile',
         views.EditProfileViews.as_view(),
         name='edit_profile'),
]