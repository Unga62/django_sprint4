from django import forms
from .models import Post, Comment
from blog.config import COLS_SLICE, ROWS_SLICE


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%d-%m-%Y %H:%M',
                attrs={'type': 'datetime-local'}
            )
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea({'cols': COLS_SLICE, 'rows': ROWS_SLICE}),
        }
