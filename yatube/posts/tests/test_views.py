from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group
from django import forms
from django.core.cache import cache

from posts.views import COUNT_POSTS


User = get_user_model()


class PostPagesTest(TestCase):
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

    def test_pages_and_url_for_auth_client(self):
        """Каждый URL используется правильный шаблон для авторизованного"""
        templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': 'auth'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', args={f'{self.post.id}'}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', args={f'{self.post.id}'}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for name, template in templates.items():
            with self.subTest(reverse_name=name):
                response = self.auth_client.get(name)
                self.assertTemplateUsed(response, template)

    def test_pages_and_url_for_guest(self):
        """Каждый URL использует правильный шаблон для гостя"""
        templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': 'auth'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', args={f'{self.post.id}'}
            ): 'posts/post_detail.html',
        }
        for name, template in templates.items():
            with self.subTest(reverse_name=name):
                response = self.guest_client.get(name)
                self.assertTemplateUsed(response, template)

    def test_index_page_context(self):
        """Шаблон index с правильным контекстом"""
        response = self.auth_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_author = first_object.author.username
        post_text = first_object.text
        post_group = first_object.group.title
        self.assertEqual(post_author, 'auth')
        self.assertEqual(post_text, 'Тестовый текст')
        self.assertEqual(post_group, 'Тестовая группа')

    def test_index_page_cache(self):
        """Шаблон index с кешированием"""
        response = self.auth_client.get(reverse('posts:index'))
        self.post.text = 'Изменили текст'
        self.post.save()
        response_cache = self.auth_client.get(reverse('posts:index'))
        self.assertEqual(response.content, response_cache.content)
        cache.clear()
        response_clear = self.auth_client.get(reverse('posts:index'))
        self.assertNotEqual(response_cache.content, response_clear.content)

    def test_group_list_context(self):
        """Шаблон group_list с правильным контекстом"""
        response = self.auth_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(response.context.get('post').author.username, 'auth')
        self.assertEqual(response.context.get('post').text, 'Тестовый текст')

    def test_profile_context(self):
        """Шаблон profile с правильным контекстом"""
        response = self.auth_client.get(reverse(
            'posts:profile', kwargs={'username': f'{self.user}'})
        )
        self.assertEqual(response.context.get('post').author.username, 'auth')
        self.assertEqual(response.context.get('post').text, 'Тестовый текст')
        self.assertEqual(
            response.context.get('post').group.title, 'Тестовая группа'
        )

    def test_post_detail_context(self):
        """Шаблон post_detail с правильным контекстом"""
        response = self.auth_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': f'{self.post.id}'})
        )
        self.assertEqual(response.context.get('post').author.username, 'auth')
        self.assertEqual(
            response.context['counter_posts'], self.post.author.posts.count()
        )

    def test_create_post_edit_context(self):
        """Шаблон post_edit с правильным контекстом"""
        response = self.post_author.get(reverse(
            'posts:post_edit', kwargs={'post_id': f'{self.post.id}'})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_context(self):
        """Шаблон create_post с правильным контекстом"""
        response = self.auth_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_another_group(self):
        """При указании группы новый пост не попал в неверную группу"""
        response = self.auth_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        first_object = response.context['page_obj'][0]
        post_text = first_object.text
        self.assertEqual(post_text, 'Тестовый текст')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.posts = [
            Post(
                author=cls.user,
                text=f'Тестовый текст {i}',
                group=cls.group,
            ) for i in range(13)
        ]
        cls.post = Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(self.user)
        cache.clear()

    def test_first_page_contains_ten_records(self):
        urls = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': f'{self.user}'}),
        }
        for name in urls:
            response = self.auth_client.get(name)
            self.assertEqual(len(response.context['page_obj']), COUNT_POSTS)

    def test_second_page_contains_three_records(self):
        urls = {
            reverse('posts:index') + '?page=2',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
            + '?page=2',
            reverse('posts:profile', kwargs={'username': f'{self.user}'})
            + '?page=2',
        }
        for name in urls:
            response = self.auth_client.get(name)
            self.assertEqual(len(
                response.context['page_obj']
            ), len(self.post) - COUNT_POSTS)
