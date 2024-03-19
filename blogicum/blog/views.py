from django.db.models import Count
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import Http404
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


class CheckMixin:
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)


class RedirectionMixin:
    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={
            'username': self.request.user.username}
        )


class PostDetailandDeleteMixin:
    model = Post
    template_name = 'blog/detail.html'


class PostEditandCreateMixin:
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

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.kwargs['pk']}
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


class PostCreateViews(LoginRequiredMixin, RedirectionMixin,
                      PostEditandCreateMixin,
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


class PostEditView(LoginRequiredMixin, CheckMixin,
                   PostEditandCreateMixin, UpdateView):
    """СBV для редактирования поста"""

    pk_url_kwarg = 'pk'
    exclude = ('pub_date',)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.kwargs['pk']}
        )


class PostDetailView(PostDetailandDeleteMixin, DetailView):
    """CBV для отоброжения отдельного поста и коммента"""

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        post = self.object
        if not post.is_published or (
            post.category and not post.category.is_published
        ):
            if request.user.is_authenticated and request.user == post.author:
                return super().dispatch(request, *args, **kwargs)
            raise Http404('Page not found')
        if post.pub_date > timezone.now() and request.user != post.author:
            raise Http404('Page not found')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class PostDeleteView(LoginRequiredMixin, RedirectionMixin, CheckMixin,
                     PostDetailandDeleteMixin, DeleteView):
    """CBV для удаления поста"""

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostCommentView(LoginRequiredMixin, CommentMixin,
                      CreateView):
    """CBV для добавления комментариев"""

    def dispatch(self, request, *args, **kwargs):
        self.comment_edit = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.comment_edit
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={
            'pk': self.comment_edit.pk}
        )


class PostEditCommentView(LoginRequiredMixin, CommentEditDelete,
                          CheckMixin, UpdateView):
    """CBV для редактирование комментариев"""

    pass


class PostDeleteCommentView(LoginRequiredMixin, CommentEditDelete, CheckMixin,
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
