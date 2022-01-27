import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls.base import reverse
from django import forms

from ..models import Comment, Follow, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Mark')
        cls.follower_user = User.objects.create_user(username='Following')
        Follow.objects.create(user=cls.follower_user, author=cls.user)

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
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        Post.objects.create(
            author=cls.follower_user,
            text='Mark не увидит этот текст',
        )
        cls.post_list = [
            Post(
                author=cls.user,
                group=PostsURLTests.group,
                text=f'Тестовая группа {i}',
                image=uploaded,
            )
            for i in range(1, 14)
        ]
        Post.objects.bulk_create(cls.post_list)

        cls.comment = Comment.objects.create(
            text='Комментарий',
            author=cls.user,
            post=Post.objects.first(),
        )

        cls.empty_group = Group.objects.create(
            title='Пустая группа',
            slug='Пустой слаг',
            description='Пустое описание',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user)

        self.follower_client = Client()
        self.follower_client.force_login(self.follower_user)

    def test_pages_use_correct_template(self):
        """App's templates are correct."""
        templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_posts',
                kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': Post.objects.first().pk}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': Post.objects.first().pk}
            ): 'posts/create_post.html',
        }

        for reverse_name, template in templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)

                self.assertTemplateUsed(response, template)

    def test_page_shows_correct_forms_in_context(self):
        """Template has proper forms in context."""
        reverses = (
            reverse('posts:post_create'),
            reverse(
                'posts:post_edit',
                kwargs={'post_id': Post.objects.first().pk}
            ),
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }

        for reverse_item in reverses:
            with self.subTest(reverse_item=reverse_item):
                response = self.author_client.get(reverse_item)

                for value, expected in form_fields.items():
                    form_field = response.context['form'].fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_pages_shows_correct_context(self):
        """Templates index, group_posts, profile have proper context.
        """
        reverses = (
            reverse('posts:index'),
            reverse(
                'posts:group_posts',
                kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ),
        )

        for reverse_item in reverses:
            with self.subTest(reverse_item=reverse_item):
                response = self.author_client.get(reverse_item)
                first_post = response.context['page_obj'][0]
                first_post_0 = {
                    first_post.author: Post.objects.first().author,
                    first_post.group: Post.objects.first().group,
                    first_post.text: Post.objects.first().text,
                    first_post.image: Post.objects.first().image,
                }

            for value, expected in first_post_0.items():
                self.assertEqual(value, expected)

    def test_post_detail_shows_correct_context(self):
        """Template post_detail has proper post in context."""
        reverses = (
            reverse(
                'posts:post_detail',
                kwargs={'post_id': Post.objects.first().pk}
            ),
        )

        for reverse_item in reverses:
            with self.subTest(reverse_item=reverse_item):
                response = self.author_client.get(reverse_item)
                first_post = response.context['post']
                first_post_0 = {
                    first_post.author: Post.objects.first().author,
                    first_post.group: Post.objects.first().group,
                    first_post.text: Post.objects.first().text,
                    first_post.image: Post.objects.first().image,
                }
                post_comment = response.context['comments'][0]

            for value, expected in first_post_0.items():
                self.assertEqual(value, expected)
            self.assertEqual(post_comment, self.comment)

    def test_post_detail_comment_context(self):
        """Post_detail template has correct form in context."""
        # не работает. В слак спросил
        comment_form_field = {'text': forms.fields.CharField}

        response = self.author_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': Post.objects.first().pk},
            )
        )
        for value, expected in comment_form_field.items():
            comment_form = response.context['form'].fields.get(value)
            self.assertIsInstance(comment_form, expected)

    def test_profile_page_shows_correct_context(self):
        """Profile template has a proper author in context."""
        response = self.author_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )

        author = response.context['author']

        self.assertEqual(author, self.user)

    def test_first_page_contains_ten_posts(self):
        """Site's first page contains ten posts."""
        reverses = (
            reverse('posts:index'),
            reverse(
                'posts:group_posts',
                kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ),
        )

        for reverse_item in reverses:
            with self.subTest(reverse_item=reverse_item):
                response = self.author_client.get(reverse_item)

                self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_four_posts(self):
        """Index's second page contains four posts."""
        response = self.author_client.get(reverse('posts:index') + '?page=2')

        self.assertEqual(len(response.context['page_obj']), 4)

    def test_second_page_contains_three_posts(self):
        """Site's second page contains three posts."""
        reverses = (
            reverse(
                'posts:group_posts',
                kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ),
        )

        for reverse_item in reverses:
            with self.subTest(reverse_item=reverse_item):
                response = self.author_client.get(reverse_item + '?page=2')

                self.assertEqual(len(response.context['page_obj']), 3)

    def test_post_in_correct_group(self):
        """Post shown in correct group."""
        response = self.author_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': Post.objects.first().pk}
            )
        )
        post = response.context['post']

        self.assertNotEqual(post.group, 'Пустая группа')

    def test_post_has_comment(self):
        """Propper comment has shown on post's page."""
        response = self.author_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': Post.objects.first().pk}
            )
        )
        post_comment = response.context['comments'][0]

        self.assertEqual(post_comment, self.comment)

    def test_index_page_cache(self):
        """Index page's cache performs correctly."""
        # Никита, я буду удивлён, если это не надо бить на несколько тестов

        response_cntnt = self.author_client.get(reverse('posts:index')).content
        Post.objects.first().delete()
        cache_content = self.author_client.get(reverse('posts:index')).content

        self.assertEqual(response_cntnt, cache_content)

        cache.clear()
        new_content = self.author_client.get(reverse('posts:index')).content

        self.assertNotEqual(response_cntnt, new_content)

    def test_follow_index_empty(self):
        """Follow_index's context is empty."""
        response = self.author_client.get(
            reverse('posts:follow_index')
        )
        response_page_obj = response.context['page_obj']
        self.assertCountEqual(response_page_obj, [])

    def test_follow_index_not_empty(self):
        """Follow_index's context contains posts."""
        response = self.follower_client.get(
            reverse('posts:follow_index')
        )
        expected = Post.objects.filter(author=self.user)[:10]
        response_page_obj = response.context['page_obj']
        self.assertCountEqual(response_page_obj, expected)

    def test_profile_follow(self):
        """Profile_follow function executes correctly."""
        follower_user = self.follower_user.username
        response = self.author_client.get(reverse(
            'posts:profile',
            kwargs={'username': follower_user}
        ))
        response_flwng = response.context['following']

        self.author_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': follower_user}
        ))
        response_upd = self.author_client.get(reverse(
            'posts:profile',
            kwargs={'username': follower_user}
        ))
        response_flwng_upd = response_upd.context['following']

        self.assertNotEqual(response_flwng, response_flwng_upd)

    def test_profile_unfollow(self):
        """Profile_unfollow function executes correctly."""
        author_user = self.user.username
        response = self.follower_client.get(reverse(
            'posts:profile',
            kwargs={'username': author_user}
        ))
        response_flwng = response.context['following']

        self.follower_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': author_user}
        ))
        response_upd = self.follower_client.get(reverse(
            'posts:profile',
            kwargs={'username': author_user}
        ))
        response_flwng_upd = response_upd.context['following']

        self.assertNotEqual(response_flwng, response_flwng_upd)
