import shutil
import tempfile

from posts.forms import PostForm
from posts.models import Post
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

# TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()  
        form_data = {
            # 'author': 'auth',
            'text': 'Тестовый текст',
        }
        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile', kwargs={'username': f'{self.user}'}))
        self.assertEqual(Post.objects.count(), posts_count+1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
            ).exists()
        )

    def test_post_edit(self):
        """Валидация формы редактирования поста."""
        form_data = {
            'text': 'Тестовый текст для редактирования',
        }
        self.auth_client.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.get(
                text='Тестовый текст для редактирования',
            )
        )
