from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Заголовок",
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name="Идентификатор",
    )
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField("Текст поста", help_text="Введите текст поста")
    pub_date = models.DateTimeField(
        "Дата публикации",
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="posts",
        verbose_name="Группа",
        help_text="Группа, к которой будет относиться пост",
    )
    image = models.ImageField(
        "Картинка",
        upload_to="posts/",
        blank=True,
    )

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text[: settings.NUM_OF_SYMBOLS_ON_TEXT]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        blank=True,
        null=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор",
        blank=True,
        null=True,
    )
    text = models.TextField(
        verbose_name="Текст комментария",
        help_text="Введите текст комментария",
    )
    created = models.DateTimeField("Дата публикации", auto_now_add=True)

    class Meta:
        ordering = ["created"]
        verbose_name = "Комментарий"

    def __str__(self):
        return self.text[: settings.NUM_OF_SYMBOLS_ON_TEXT]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Подписка",
    )
