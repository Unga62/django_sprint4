from django.urls import path, include

from . import views

app_name = 'blog'

posts_urls = [
    # просмотор отдельного поста
    path('<int:post_id>/', views.PostDetailView.as_view(),
         name='post_detail'),

    # создание нового поста
    path('create/', views.PostCreateViews.as_view(), name='create_post'),

    # редактирование поста
    path('<int:post_id>/edit/', views.PostEditView.as_view(),
         name='edit_post'),

    # удаление поста
    path('<int:post_id>/delete/', views.PostDeleteView.as_view(),
         name='delete_post'),

    # комментирование поста
    path('<int:post_id>/comment', views.CreateCommentView.as_view(),
         name='add_comment'),

    # редактирование комментария поста
    path('<int:post_id>/edit_comment/<int:comment_id>/',
         views.PostEditCommentView.as_view(),
         name='edit_comment'),

    # удаление комментария к посту
    path('<int:post_id>/delete_comment/<int:comment_id>/',
         views.PostDeleteCommentView.as_view(),
         name='delete_comment'),

]

profile_urls = [
    # страницы профиля пользователя и редактирование страницы
    path('edit_profile/',
         views.EditProfileViews.as_view(),
         name='edit_profile'),
    path('<slug:username>/', views.ProfileViews.as_view(),
         name='profile'),
]

urlpatterns = [
    # просмотор всех постов
    path('', views.PostIndexView.as_view(), name='index'),

    path('posts/', include(posts_urls)),
    path('profile/', include(profile_urls)),
    path('category/<slug:category_slug>/', views.CategoryPostsView.as_view(),
         name='category_posts'),
]
