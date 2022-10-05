from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class UserURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.author = User.objects.create_user(username="NoName")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_urls_uses_correct_template_guest(self):
        """
        URL-адрес использует соответствующий
        шаблон и статус страницы для guest_client.

        """
        templates_url_names = {
            reverse("users:signup"): "users/signup.html",
            reverse("users:logout"): "users/logged_out.html",
            reverse("users:login"): "users/login.html",
            reverse("users:password_reset"): "users/password_reset_form.html",
            reverse(
                "users:password_reset_done"
            ): "users/password_reset_done.html",
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_authorized(self):
        """
        URL-адрес использует соответствующий
        шаблон и статус страницы для authorized_client.

        """
        templates_url_names = {
            reverse(
                "users:password_change"
            ): "users/password_change_form.html",
            reverse(
                "users:password_change_done"
            ): "users/password_change_done.html",
            reverse(
                "users:password_reset_confirm",
                kwargs={"token": "token", "uidb64": "uid64"},
            ): "users/password_reset_confirm.html",
            reverse(
                "users:password_reset_complete"
            ): "users/password_reset_complete.html",
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
