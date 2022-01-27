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
            text='Тестовая группа',
        )

    def test_models_have_correct_object_names(self):
        """Check __str__. method works correctly."""
        objects = (
            PostModelTest.post,
            PostModelTest.group
        )
        for object in objects:
            with self.subTest(object=object):
                self.assertEqual(
                    str(object), 'Тестовая группа')

    def test_post_verbose_names(self):
        """Check verbose names are correct."""
        post = PostModelTest.post
        verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }
        for field, example in verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, example)

    def test_post_help_text(self):
        """Check help_text is correct."""
        post = PostModelTest.post
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Выберите группу'
        }
        for field, example in help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, example)
