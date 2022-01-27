from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls.base import reverse

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Mark')
        cls.other_user = User.objects.create_user(username='other_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.other_user)

        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_unauthorized_user_pages_availible(self):
        """Checking of page is availible."""
        unauthorized_urls = (
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.pk}/',
        )

        for address in unauthorized_urls:
            with self.subTest(adress=address):
                response = self.guest_client.get(address)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_user_pages_availible(self):
        """Checking of page is availible for authorized user."""
        unauthorized_urls = (
            f'/posts/{self.post.pk}/edit/',
            '/create/',
        )

        for address in unauthorized_urls:
            with self.subTest(adress=address):
                response = self.author_client.get(address)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unauthorized_user_redirects(self):
        """Checking of redirecting unauthorized users."""
        redirects = {
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ): f'/auth/login/?next=/posts/{self.post.pk}/edit/',
            reverse('posts:post_create'): '/auth/login/?next=/create/',
        }

        for reverse_page, redirect in redirects.items():
            with self.subTest(reverse_page=reverse_page):
                response = self.guest_client.get(reverse_page, follow=True)

                self.assertRedirects(response, redirect)

    def test_authorized_user_redirects(self):
        """Checking of /posts/post_id/edit/
        redirects anuthorized nonauthor user.
        """
        response = self.authorized_client.get(
            f'/posts/{self.post.pk}/edit/', follow=True
        )

        self.assertRedirects(
            response, f'/posts/{self.post.pk}/'
        )

    def test_address_uses_correct_template(self):
        """URL uses a proper template."""
        templates = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

        for address, template in templates.items():
            with self.subTest(adress=address):
                response = self.author_client.get(address)

                self.assertTemplateUsed(response, template)

    def test_unexisting_page(self):
        """Unexisting page raises 404 error"""
        response = self.guest_client.get('/unexisting_page/')

        self.assertEquals(response.status_code, HTTPStatus.NOT_FOUND)
