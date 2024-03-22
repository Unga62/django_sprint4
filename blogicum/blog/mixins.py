from django.shortcuts import redirect
from django.urls import reverse

from blog.config import POST_SLICE
from blog.forms import CommentForm, PostForm
from blog.models import Comment, Post
from blog.post_filter_published import post_published


class PaginateMixin:
    paginate_by = POST_SLICE


class CheckMixin:
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class RedirectionMixin:
    def get_success_url(self):
        return reverse('blog:profile', kwargs={
            'username': self.request.user.username}
        )


class PostDetailandDeleteMixin:
    model = Post
    template_name = 'blog/detail.html'


class PostEditandCreateMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

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
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class BasicPostViewMixin(PaginateMixin):
    model = Post

    def get_queryset(self):
        return post_published()
