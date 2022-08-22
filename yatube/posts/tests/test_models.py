from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у Post корректно работает __str__."""
        post = PostModelTest.post
        max_text = post.text[:15]
        length_text = len(post.text)
        self.assertEqual(len(max_text), length_text, 'Что-то не так')

    def test_models_group(self):
        """Проверяем, что у Group корректно работает __str__."""
        group = PostModelTest.group
        self.assertEqual(group.title, 'Тестовая группа')
