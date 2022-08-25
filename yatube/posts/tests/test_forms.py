from posts.models import Post
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

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
        self.nonauth_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_create_post_for_auth_client(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
        }
        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': f'{self.user}'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(form_data['text'])

    def test_create_post_for_nonauth_client(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
        }
        response = self.nonauth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), posts_count)

    def test_post_edit_for_auth(self):
        """Валидация формы редактирования поста для авторизованного"""
        form_data = {
            'text': 'Тестовый текст для редактирования',
        }
        self.auth_client.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True
        )
        self.assertTrue(form_data['text'])

    def test_post_edit_for_guest(self):
        """Валидация формы редактирования поста для гостя"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст для редактирования',
        }
        response = self.nonauth_client.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, (
                f'/auth/login/?next=/posts/{PostFormTests.post.id}/edit/')
        )
        self.assertEqual(Post.objects.count(), posts_count)
