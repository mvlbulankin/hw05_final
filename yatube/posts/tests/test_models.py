from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="NoName")
        cls.group = Group.objects.create(
            title="test_title",
            slug="test-slug",
            description="test_description",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="test_text",
        )

    def test_models_have_correct_object_names(self):
        """
        Проверяем, что у моделей корректно работает __str__.

        """
        self.assertEqual(self.group.title, str(self.group))
        self.assertEqual(
            self.post.text[: settings.NUM_OF_SYMBOLS_ON_TEXT], str(self.post)
        )

    def test_verbose_name(self):
        """
        verbose_name в полях совпадает с ожидаемым.

        """
        post = PostModelTest.post
        field_verboses = {
            "author": "Автор",
            "group": "Группа",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_text(self):
        """
        help_text в полях совпадает с ожидаемым.

        """
        post = PostModelTest.post
        field_help_texts = {
            "text": "Введите текст поста",
            "group": "Группа, к которой будет относиться пост",
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )
