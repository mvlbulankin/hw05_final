import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Follow, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


TEMP_NUM_OF_POSTS_ON_LAST_PAGE = 5
TEMP_NUM_OF_POSTS_TO_PAGINATE = (
    settings.NUM_OF_POSTS_ON_PAGE + TEMP_NUM_OF_POSTS_ON_LAST_PAGE
)


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = TEMP_MEDIA_ROOT
        cls.author = User.objects.create_user(username="NoName")
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.author_another = User.objects.create_user(
            username="author_another"
        )
        cls.authorized_author_another_client = Client()
        cls.authorized_author_another_client.force_login(cls.author_another)
        cls.small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00"
            b"\x01\x00\x00\x00\x00\x21\xf9\x04"
            b"\x01\x0a\x00\x01\x00\x2c\x00\x00"
            b"\x00\x00\x01\x00\x01\x00\x00\x02"
            b"\x02\x4c\x01\x00\x3b"
        )
        cls.uploaded = SimpleUploadedFile(
            name="small.gif", content=cls.small_gif, content_type="image/gif"
        )
        cls.group = Group.objects.create(
            title="test_title",
            slug="test_slug",
            description="test_description",
        )
        cls.post = Post.objects.create(
            text="test_post",
            author=cls.author,
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={"slug": self.group.slug}
            ): "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={"username": self.author}
            ): "posts/profile.html",
            reverse(
                "posts:post_detail", kwargs={"post_id": self.post.pk}
            ): "posts/post_detail.html",
        }
        self.templates_pages_names_user = {
            reverse("posts:post_create"): "posts/create_post.html",
            reverse(
                "posts:post_edit", kwargs={"post_id": self.post.pk}
            ): "posts/create_post.html",
            reverse(
                "posts:add_comment", kwargs={"post_id": self.post.pk}
            ): "posts/post_detail.html",
            reverse("posts:follow_index"): "posts/follow.html",
            reverse(
                "posts:profile_follow", kwargs={"username": self.author}
            ): "posts/profile.html",
            reverse(
                "posts:profile_unfollow", kwargs={"username": self.author}
            ): "posts/profile.html",
        }

    def _assert_post_has_attribs(self, post, pk, author, group, image):
        self.assertEqual(post.pk, pk)
        self.assertEqual(post.author, author)
        self.assertEqual(post.group, group)
        self.assertEqual(post.image, image)

    def test_pages_uses_correct_template_and_context_guest(self):
        """
        URL-адрес использует соответствующий шаблон
        и контекст для guest_client

        """
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                self._assert_post_has_attribs(
                    self.post,
                    self.post.pk,
                    self.author,
                    self.group,
                    self.post.image,
                )

    def test_pages_uses_correct_template_and_context_authorized(self):
        """
        URL-адрес использует соответствующий шаблон
        и контекст для authorized_client.

        """
        for reverse_name, template in self.templates_pages_names_user.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(
                    reverse_name, follow=True
                )
                self.assertTemplateUsed(response, template)
                self._assert_post_has_attribs(
                    self.post,
                    self.post.pk,
                    self.author,
                    self.group,
                    self.post.image,
                )

    def assert_post_response(self, response):
        """
        Проверяем Context в формах шаблонов post_create и post_edit.

        """
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_page_show_correct_context(self):
        """
        Шаблон post_create сформирован с правильным контекстом.

        """
        response = self.authorized_client.get(reverse("posts:post_create"))
        self.assert_post_response(response)

    def test_post_edit_page_show_correct_context(self):
        """
        Шаблон post_edit сформирован с правильным контекстом.

        """
        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk})
        )
        self.assert_post_response(response)

    def test_follow_author_another(self):
        """
        Follow на другого пользователя работает корректно,
        Follow на самого себя не возможен,
        Follow на одного пользователя дважды не возможен

        """
        for i in range(2):
            self.authorized_author_another_client.get(
                reverse(
                    "posts:profile_follow",
                    kwargs={"username": self.author.username},
                )
            )
        self.authorized_client.get(
            reverse(
                "posts:profile_follow",
                kwargs={"username": self.author.username},
            )
        )
        follow_exist = Follow.objects.filter(
            user=self.author_another, author=self.author
        ).exists()
        follow_exist_myself = Follow.objects.filter(
            user=self.author, author=self.author
        ).exists()
        follow_count = Follow.objects.count()
        self.assertTrue(follow_exist)
        self.assertFalse(follow_exist_myself)
        self.assertEqual(follow_count, 1)

    def test_unfollow_author_another(self):
        """
        Unfollow от другого пользователя работает корректно

        """
        self.authorized_author_another_client.get(
            reverse(
                "posts:profile_follow",
                kwargs={"username": self.author.username},
            )
        )
        self.authorized_author_another_client.get(
            reverse(
                "posts:profile_unfollow",
                kwargs={"username": self.author.username},
            )
        )
        follow_exist = Follow.objects.filter(
            user=self.author_another, author=self.author
        ).exists()
        self.assertFalse(follow_exist)

    def test_new_post_follow_index_show_correct_context(self):
        """
        Новая запись автора появляется в ленте подписчиков
        и не появляется в ленте тех, кто не подписан

        """
        self.authorized_author_another_client.get(
            reverse(
                "posts:profile_follow",
                kwargs={"username": self.author.username},
            )
        )
        follow_exist = Follow.objects.filter(
            user=self.author_another, author=self.author
        ).exists()
        self.assertTrue(follow_exist)
        response = self.authorized_author_another_client.get(
            reverse("posts:follow_index")
        )
        count_0 = len(response.context.get("page_obj"))
        first_object = response.context.get("page_obj").object_list[0]
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        post_group_0 = first_object.group.slug
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, self.group.slug)

        self.authorized_author_another_client.get(
            reverse(
                "posts:profile_unfollow",
                kwargs={"username": self.author.username},
            )
        )
        follow_exist = Follow.objects.filter(
            user=self.author_another, author=self.author
        ).exists()
        self.assertFalse(follow_exist)
        response = self.authorized_author_another_client.get(
            reverse("posts:follow_index")
        )
        count_1 = len(response.context.get("page_obj"))
        self.assertEqual(count_0 - 1, count_1)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authorized_client = Client()
        cls.author = User.objects.create_user(username="NoName")
        cls.group = Group.objects.create(
            title="test_title",
            description="test_description",
            slug="test_slug",
        )

    def setUp(self):
        for post_temp in range(TEMP_NUM_OF_POSTS_TO_PAGINATE):
            Post.objects.create(
                text=f"text{post_temp}", author=self.author, group=self.group
            )

    def _test_pagination(self, url_params, expected_count):
        """
        Общий метод для проверки паджинатора

        """
        templates_pages_names = {
            reverse("posts:index") + url_params: "posts/index.html",
            reverse("posts:group_list", kwargs={"slug": self.group.slug})
            + url_params: "posts/group_list.html",
            reverse("posts:profile", kwargs={"username": self.author})
            + url_params: "posts/profile.html",
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(
                    len(response.context["page_obj"]), expected_count
                )

    def test_first_page_contains_ten_records(self):
        """
        Количество постов на первой странице паджинатора
        равно settings.NUM_OF_POSTS_ON_PAGE.

        """
        self._test_pagination("", settings.NUM_OF_POSTS_ON_PAGE)

    def test_second_page_contains_three_records(self):
        """
        Количество постов на последней странице
        паджинатора равно TEMP_NUM_OF_POSTS_ON_LAST_PAGE.

        """
        self._test_pagination("?page=2", TEMP_NUM_OF_POSTS_ON_LAST_PAGE)


class CacheViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = TEMP_MEDIA_ROOT
        cls.author = User.objects.create_user(username="NoName")
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.group = Group.objects.create(
            title="test_group",
            slug="test_slug",
            description="test_description",
        )
        cls.post = Post.objects.create(
            text="test_text",
            group=cls.group,
            author=cls.author,
        )

    def test_cache_index(self):
        """
        Кэш для "/" хранится и обновляется.

        """
        response = self.authorized_client.get(reverse("posts:index"))
        posts = response.content
        Post.objects.create(
            text="test_new_text",
            author=self.author,
        )
        response_old = self.authorized_client.get(reverse("posts:index"))
        old_posts = response_old.content
        self.assertEqual(old_posts, posts, "cached_page_not_return")
        cache.clear()
        response_new = self.authorized_client.get(reverse("posts:index"))
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts, "cache_not_cleared")
