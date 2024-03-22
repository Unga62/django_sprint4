from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from blog.forms import CommentForm, PostForm
from blog.mixins import (
    CheckMixin, PaginateMixin, PostEditandCreateMixin,
    PostDetailandDeleteMixin, BasicPostViewMixin,
    RedirectionMixin, CommentMixin, CommentEditDelete,
)
from blog.models import Category, Post, User
from blog.post_filter_published import post_filter_count, post_published


class ProfileViews(BasicPostViewMixin, ListView):
    """CBV для страницы профиля"""

    template_name = 'blog/profile.html'
    ordering = ['-pub_date']

    def get_queryset(self):
        posts = Post.objects
        self.profile = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        posts = post_filter_count(posts).filter(
            author=self.profile
        )
        if self.request.user != self.profile:
            posts = super().get_queryset().filter(
                author=self.profile
            )
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs['username']
        profile = get_object_or_404(User, username=username)
        context['profile'] = profile
        return context


class EditProfileViews(LoginRequiredMixin, RedirectionMixin, UpdateView):
    """CBV для редактирования профиля"""

    model = User
    fields = (
        'first_name',
        'last_name',
        'username',
        'email'
    )
    slug_field = 'username'
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user


class PostCreateViews(LoginRequiredMixin, RedirectionMixin,
                      PostEditandCreateMixin,
                      CreateView):
    """CBV для создание новых постов"""

    pass


class PostIndexView(BasicPostViewMixin, PaginateMixin, ListView):
    """CBV для оторожения постов на главной странице"""

    template_name = 'blog/index.html'


class PostEditView(LoginRequiredMixin, CheckMixin,
                   PostEditandCreateMixin, UpdateView):
    """СBV для редактирования поста"""

    def get_success_url(self):
        return reverse(
            'blog:post_detail', args=[self.kwargs['post_id']]
        )


class PostDetailView(PostDetailandDeleteMixin, DetailView):
    """CBV для отоброжения отдельного поста и коммента"""

    def get_object(self):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if self.request.user == post.author:
            return post
        return get_object_or_404(post_published(), pk=self.kwargs['post_id'])

    def get_queryset(self):
        return super().get_queryset().select_related(
            'author',
            'location',
            'category',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class PostDeleteView(LoginRequiredMixin, RedirectionMixin,
                     CheckMixin, PostEditandCreateMixin,
                     DeleteView):
    """CBV для удаления поста"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


class CreateCommentView(LoginRequiredMixin, CommentMixin,
                        CreateView):
    """CBV для добавления комментариев"""

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={
            'post_id': self.kwargs['post_id']}
        )


class PostEditCommentView(LoginRequiredMixin, CommentEditDelete,
                          CheckMixin, UpdateView):
    """CBV для редактирование комментариев"""

    pass


class PostDeleteCommentView(LoginRequiredMixin, CommentEditDelete, CheckMixin,
                            DeleteView):
    """CBV для удаления комментариев"""

    pass


class CategoryPostsView(BasicPostViewMixin, ListView):
    """CBV для вывода постов по категориям"""

    model = Category
    template_name = 'blog/category.html'

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return super().get_queryset().filter(
            category=self.category
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context
