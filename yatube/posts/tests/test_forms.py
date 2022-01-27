import shutil
import tempfile
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Post, Group, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Mark')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )

        cls.comment = Comment.objects.create(
            text='Комментарий',
            author=cls.user,
            post=cls.post,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user)

        self.guest_client = Client()

    def test_valid_form_creates_post_with_group(self):
        """Creating post with group and redirect to posts:profile."""
        posts_count = Post.objects.count()
        post_data = {
            'text': 'Новый пост',
            'group': self.group.pk,
        }

        response = self.author_client.post(
            reverse('posts:post_create'),
            data=post_data,
        )

        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        ))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Новый пост',
                group=self.group.pk,
                author=self.user.pk,
            ).exists()
        )

    def test_valid_form_creates_post_without_group(self):
        """Creating new text only post and redirect to posts:profile."""
        posts_count = Post.objects.count()
        post_data = {'text': 'Второй новый пост'}

        response = self.author_client.post(
            reverse('posts:post_create'),
            data=post_data,
        )

        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Второй новый пост',
                author=self.user.pk,
                group__isnull=True
            ).exists()
        )

    def test_form_creates_post_with_image(self):
        """Creating post with image and redirect to posts:profile."""
        posts_count = Post.objects.count()
        post_data = {
            'text': 'Новый пост',
            'image': self.uploaded,
        }

        response = self.author_client.post(
            reverse('posts:post_create'),
            data=post_data,
        )

        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        ))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Новый пост',
                author=self.user.pk,
                image='posts/small.gif'
            ).exists()
        )

    def test_valid_form_edites_post(self):
        """Editing post and redirect to posts:post_detail."""
        form_data = {
            'text': 'Измененный пост',
        }

        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
        )

        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}
        ))
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, 'Измененный пост')

    def test_authorised_user_comment(self):
        """Authorised user adding a comment and redirect to post_detail."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Новый комментарий',
        }

        response = self.author_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}
        ))
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text='Новый комментарий',
                author=self.user.pk,
                post=self.post.id,
            ).exists()
        )

    def test_unauthorised_user_cant_comment(self):
        """Unauthorised user can't add a comment."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Новый комментарий',
        }

        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )

        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)
