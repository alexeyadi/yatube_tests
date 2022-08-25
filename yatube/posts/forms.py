from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        labels = {
            'text': 'Текст',
            'group': 'Выберите группу',
        }
        help_texts = {
            'text': ('Напишите текст вашего поста'),
            'group': ('Выбор группы')
        }
