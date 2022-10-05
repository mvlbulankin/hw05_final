import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="NoName")
        cls.group = Group.objects.create(
            title="test_title",
            slug="test_slug_1",
            description="test_description",
        )
        cls.post = Post.objects.create(
            text="test_post", author=cls.user, group=cls.group
        )
        cls.form = PostForm()
        cls.posts_count = Post.objects.count()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """
        Валидная форма создает Post.

        """
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )
        form_data = {
            "group": self.group.id,
            "text": "test_post",
            "image": uploaded,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response, reverse("posts:profile", kwargs={"username": self.user})
        )
        self.assertEqual(Post.objects.count(), self.posts_count + 1)
        self.assertEqual(Post.objects.last().group.id, form_data["group"])
        self.assertEqual(Post.objects.last().text, form_data["text"])
        self.assertTrue(
            Post.objects.filter(
                text="test_post",
                group__slug="test_slug_1",
            ).exists()
        )

    def test_not_create_post(self):
        """
        Неавторизованный пользователь не может создать Post.

        """
        form_data = {
            "group": self.group.id,
            "text": "test_post",
        }
        self.guest_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertEqual(Post.objects.count(), self.posts_count)

    def test_edit_post(self):
        """
        Валидная форма редактирует Post.

        """
        form_data = {
            "group": self.group.id,
            "text": "test_post_new",
        }
        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": self.post.pk}),
        )
        self.assertEqual(Post.objects.count(), self.posts_count)
        self.assertEqual(Post.objects.last().group.id, form_data["group"])
        self.assertEqual(Post.objects.last().text, form_data["text"])

    def test_comment(self):
        """Комментарий появляется на странице поста."""
        comment_count = Comment.objects.count()
        post_id = self.post.pk
        form_data = {
            "text": "new_comment",
        }
        response = self.authorized_client.post(
            reverse("posts:add_comment", kwargs={"post_id": post_id}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(Comment.objects.filter(text="new_comment").exists())
        self.assertRedirects(
            response, reverse("posts:post_detail", kwargs={"post_id": post_id})
        )
