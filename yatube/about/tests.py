from http import HTTPStatus

from django.test import TestCase, Client


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_author(self):
        template_urls = (
            '/about/author/',
            '/about/tech/',
        )

        for url in template_urls:
            response = self.guest_client.get(url)

            self.assertEqual(response.status_code, HTTPStatus.OK)
