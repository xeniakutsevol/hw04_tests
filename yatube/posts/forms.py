from django import forms
from .models import Post
from django.utils.translation import gettext_lazy as _


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        help_texts = {
            'text': _('Добавьте текст поста (обязательно).'),
            'group': _('Добавьте сообщество (необязательно).'),
        }
