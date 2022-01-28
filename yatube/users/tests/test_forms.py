from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Mark')

    def setUp(self):
        self.unreg_client = Client()

    def test_signup_creates_new_user(self):
        """Sign Up view registers new user."""
        user_count = User.objects.count()
        form_data = {
            'first_name': 'Pavel',
            'last_name': 'Sergeev',
            'username': 'Sergeev_P',
            'email': 'New@user.com',
            'password1': 'kir185nUHT',
            'password2': 'kir185nUHT',
        }

        response = self.unreg_client.post(
            reverse('users:signup'),
            data=form_data
        )

        self.assertEqual(User.objects.count(), user_count + 1)
        self.assertRedirects(response, reverse('posts:index'))
        self.assertTrue(
            User.objects.filter(
                username='Sergeev_P',
            ).exists()
        )
