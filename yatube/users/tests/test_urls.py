import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls.base import reverse
from django.test import TestCase, Client, override_settings

TEMP_EMAIL_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(EMAIL_FILE_PATH=TEMP_EMAIL_ROOT)
class UsersUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='Mark',
            email='Mark@mark.com',
            password='1234passs',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_EMAIL_ROOT, ignore_errors=True)

    def setUp(self):
        self.unreg_client = Client()

        self.reg_client = Client()
        self.reg_client.force_login(self.user)

    def test_users_pages_are_availible_for_guests(self):
        """"Pages are availible for guest_user."""
        pages = (
            reverse('users:signup'),
            reverse('users:login'),
            reverse('users:password_reset_form'),
            reverse('users:password_reset_done'),
            reverse('users:password_reset_complete'),
            reverse(
                'users:password_reset_confirm',
                args=['test-uidb64', 'test-token']
            ),
            reverse('users:logout'),
        )

        for page in pages:
            with self.subTest(page=page):
                response = self.unreg_client.get(page)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_users_pages_are_availible_for_users(self):
        """"Pages are availible for registered user."""
        pages = (
            reverse('users:password_change_form'),
            reverse('users:password_change_done'),
        )

        for page in pages:
            with self.subTest(page=page):
                response = self.reg_client.get(page)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_address_uses_correct_template(self):
        """"Pages uses correct templates."""
        templates = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse(
                'users:password_reset_form'
            ): 'users/password_reset_form.html',
            reverse(
                'users:password_reset_done'
            ): 'users/password_reset_done.html',
            reverse(
                'users:password_reset_complete'
            ): 'users/password_reset_complete.html',
            reverse(
                'users:password_change_form',
            ): 'users/password_change_form.html',
            reverse(
                'users:password_change_done'
            ): 'users/password_change_done.html',
            reverse(
                'users:password_reset_confirm',
                args=['test-uidb64', 'test-token']
            ): 'users/password_reset_confirm.html',
            reverse('users:logout'): 'users/logged_out.html',
        }

        for page, template in templates.items():
            with self.subTest(page=page):
                response = self.reg_client.get(page)

                self.assertTemplateUsed(response, template)
