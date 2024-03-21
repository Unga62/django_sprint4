from django.urls import path, include

from . import views

app_name = 'blog'

posts_urls = [

    path('<int:post_id>/', views.PostDetailView.as_view(),
         name='post_detail'),


    path('create/', views.PostCreateViews.as_view(), name='create_post'),


    path('<int:post_id>/edit/', views.PostEditView.as_view(),
         name='edit_post'),


    path('<int:post_id>/delete/', views.PostDeleteView.as_view(),
         name='delete_post'),


    path('<int:post_id>/comment', views.CreateCommentView.as_view(),
         name='add_comment'),


    path('<int:post_id>/edit_comment/<int:comment_id>/',
         views.PostEditCommentView.as_view(),
         name='edit_comment'),


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

    # просмотр постов определенной категории
    path('category/<slug:category_slug>/', views.CategoryPostsView.as_view(),
         name='category_posts'),
]
