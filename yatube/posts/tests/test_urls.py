from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus
from django.core.cache import cache
from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.author = User.objects.create_user(username='post_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(self.user)
        self.post_author = Client()
        self.post_author.force_login(self.author)
        cache.clear()

    def test_pages_for_guest(self):
        """Доступность страниц для гостя"""
        urls = {
            '/',
            '/group/test-slug/',
            '/profile/auth/',
            f'/posts/{PostURLTests.post.id}/',
        }
        for url in urls:
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_edit_and_create_page(self):
        """Проверка создания и редактирования страницы для гостя"""
        url_redirect = {
            f'/posts/{PostURLTests.post.id}/edit/':
            f'/auth/login/?next=/posts/{PostURLTests.post.id}/edit/',
            '/create/': '/auth/login/?next=/create/',
        }
        for url, redirect in url_redirect.items():
            with self.subTest(address=url):
                response = self.guest_client.get(url)
                self.assertRedirects(response, redirect)

    def test_post_edit_page_for_author(self):
        """Проверка страницы редактирования поста для автора этого поста"""
        response = self.post_author.get(f'/posts/{PostURLTests.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_for_auth_client(self):
        """Проверка страницы создания поста для авторизованного пользователя"""
        response = self.auth_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_404(self):
        """Проверка страницы 404"""
        response = self.guest_client.get('/404/')
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct(self):
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            f'/posts/{PostURLTests.post.id}/': 'posts/post_detail.html',
            f'/posts/{PostURLTests.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(address=url):
                response = self.auth_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct(self):
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            f'/posts/{PostURLTests.post.id}/': 'posts/post_detail.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(address=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
