from django.contrib.auth import get_user_model
from django.urls.base import reverse
from django.test import TestCase, Client
from django import forms

User = get_user_model()


class UsersUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # мб просто .create(...)?
        cls.user = User.objects.create_user(
            username='Mark',
            email='Mark@mark.com',
            password='1234passs',
        )

    def setUp(self):
        self.unreg_client = Client()

    def test_signup_template_fileds(self):
        """"SignUp template has correct fields."""
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
            'password1': forms.fields.CharField,
            'password2': forms.fields.CharField,

        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.unreg_client.get(reverse('users:signup'))
                form_field = response.context['form'].fields.get(value)

                self.assertIsInstance(form_field, expected)

    def test_signup_correct_template_used(self):
        """"SignUp view uses correct template."""
        response = self.unreg_client.get(reverse('users:signup'))
        self.assertTemplateUsed(response, 'users/signup.html')
