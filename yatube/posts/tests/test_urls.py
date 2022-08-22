from django.test import TestCase, Client
from django.contrib.auth import get_user_model

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

    def test_home_page(self):
        """Главная доступна любому пользователю"""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_list_page(self):
        """Проверка доступности страницы группы"""
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_profile_page(self):
        """Проверка доступности страницы автора"""
        response = self.guest_client.get('/profile/auth/')
        self.assertEqual(response.status_code, 200)

    def test_post_detail_page(self):
        """Проверка доступности страницы поста"""
        response = self.guest_client.get(f'/posts/{PostURLTests.post.id}/')
        self.assertEqual(response.status_code, 200)

    def test_posts_edit_page(self):
        """Проверка страницы редактирования поста"""
        response = self.guest_client.get(
            f'/posts/{PostURLTests.post.id}/edit/', follow=True
        )
        self.assertRedirects(
            response, (
                f'/auth/login/?next=/posts/{PostURLTests.post.id}/edit/'
            )
        )

    def test_post_edit_page_for_author(self):
        """Проверка страницы редактирования поста для автора этого поста"""
        response = self.post_author.get(f'/posts/{PostURLTests.post.id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_create_page(self):
        """Проверка страницы создания поста"""
        response = self.guest_client.get('/create/')
        self.assertRedirects(response, ('/auth/login/?next=/create/'))

    def test_create_post_for_auth_client(self):
        """Проверка страницы создания поста для авторизованного пользователя"""
        response = self.auth_client.get('/create/')
        self.assertEqual(response.status_code, 200)

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
                response_non_auth = self.auth_client.get(url)
                self.assertTemplateUsed(response_non_auth, template)
