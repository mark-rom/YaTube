from http import HTTPStatus

from django.test import TestCase, Client
from django.urls.base import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_author(self):
        """Static pages are availible."""
        template_urls = (
            '/about/author/',
            '/about/tech/',
        )

        for url in template_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_static_use_correct_template(self):
        """Static pages use correct templates."""
        templates = {
            reverse('about:tech'): 'about/tech.html',
            reverse('about:author'): 'about/author.html',
        }

        for action, template in templates.items():
            with self.subTest(action=action):
                response = self.guest_client.get(action)

                self.assertTemplateUsed(response, template)
