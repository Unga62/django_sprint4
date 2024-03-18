from django.db.models.base import Model as Model
from django.db.models import Count
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from blog.models import Post, Category, User, Comment
from blog.config import POST_SLICE
from blog.forms import PostForm, CommentForm


def postpublished():
    """Функция возвращает проверку времени, флага публикации,
    проверку публикации категории
    """
    return (
        Q(pub_date__date__lt=timezone.now()) & Q(is_published=True)
        & Q(category__is_published=True)
    )


class PaginateMixin:
    paginate_by = POST_SLICE


class RedirectionMixin:
    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={
            'username': self.request.user.username}
        )


class DetailandDeleteMixin:
    model = Post
    template_name = 'blog/detail.html'


class EditandCreateMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentMixin:
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'


class CommentEditDelete(CommentMixin):

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', pk=self.kwargs['id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'id': self.kwargs['id']}
        )


class ProfileViews(PaginateMixin, ListView):
    """CBV для страницы профиля"""

    model = Post
    template_name = 'blog/profile.html'
    ordering = ['-pub_date']

    def get_queryset(self):
        username = self.kwargs['username']
        profile = get_object_or_404(User, username=username)
        if profile == self.request.user:
            queryset = super().get_queryset().select_related(
                'location', 'author', 'category'
            ).filter(
                author=profile
            ).annotate(
                comment_count=Count('comments')
            )
            return queryset
        else:
            return super().get_queryset().select_related(
                'location', 'author', 'category'
            ).filter(
                postpublished(), author=profile
            ).annotate(comment_count=Count('comments'))

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

    def get_object(self, queryset=None):
        return self.request.user


class PostCreateViews(LoginRequiredMixin, RedirectionMixin, EditandCreateMixin,
                      CreateView):
    """CBV для создание новых постов"""

    pass


class PostIndexView(PaginateMixin, ListView):
    """CBV для оторожения постов на главной странице"""

    model = Post
    template_name = 'blog/index.html'

    def get_queryset(self):
        posts = super().get_queryset().select_related('author',
                                                      'category').filter(
            postpublished()
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')
        return posts


class PostEditView(LoginRequiredMixin, EditandCreateMixin, UpdateView):
    """СBV для редактирования поста"""

    pk_url_kwarg = 'id'
    exclude = ('pub_date',)

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', pk=self.kwargs['id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'id': self.kwargs['id']}
        )


class PostDetailView(DetailandDeleteMixin, DetailView):
    """CBV для отоброжения отдельного поста и коммента"""

    def get_object(self):
        return get_object_or_404(
            Post.objects.select_related('author', 'location', 'category',
                                        ).filter(postpublished(),
                                                 pk=self.kwargs['id']))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class PostDeleteView(RedirectionMixin, DetailandDeleteMixin, DeleteView):
    """CBV для удаления поста"""

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostCommentView(LoginRequiredMixin, CommentMixin,
                      CreateView):
    """CBV для добавления комментариев"""

    def dispatch(self, request, *args, **kwargs):
        self.comment_edit = get_object_or_404(Post, pk=kwargs['id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.comment_edit
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={
            'id': self.comment_edit.pk}
        )


class PostEditCommentView(CommentEditDelete, LoginRequiredMixin,
                          UpdateView):
    """CBV для редактирование комментариев"""

    pass


class PostDeleteCommentView(CommentEditDelete, LoginRequiredMixin,
                            DeleteView):
    """CBV для удаления комментариев"""

    pass


class CategoryPostsView(PaginateMixin, ListView):
    """CBV для вывода постов по категориям"""

    model = Category
    template_name = 'blog/category.html'

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return self.category.posts.filter(
            postpublished(),
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context
