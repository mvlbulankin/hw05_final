from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="NoName")
        cls.group = Group.objects.create(
            title="test_title",
            slug="test_description",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="test_post",
        )
        cls.templates_url_names_guest_client = {
            "/": "posts/index.html",
            "/group/test_description/": "posts/group_list.html",
            "/profile/NoName/": "posts/profile.html",
            f"/posts/{cls.post.pk}/": "posts/post_detail.html",
        }
        cls.templates_url_names_authorized_client = {
            "/create/": "posts/create_post.html",
            f"/posts/{cls.post.pk}/edit/": "posts/create_post.html",
            f"/posts/{cls.post.pk}/comment/": "posts/post_detail.html",
            "/follow/": "posts/follow.html",
            f"/profile/{cls.post.author}/follow/": "posts/profile.html",
            f"/profile/{cls.post.author}/unfollow/": "posts/profile.html",
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """
        URL-адрес доступен по адресу и использует
        соответствующий шаблон для guest_client.

        """
        for address, template in self.templates_url_names_guest_client.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_url_uses_correct_template_authorized_client(self):
        """
        URL-адрес доступен по адресу и использует
        соответствующий шаблон для authorized_client.

        """
        for (
            address,
            template,
        ) in self.templates_url_names_authorized_client.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address, follow=True)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_404(self):
        """
        Несуществующий адрес вызывает 404

        """
        response = self.client.get("/unexisting_page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "core/404.html")
