from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse, reverse_lazy

User = get_user_model()


class CreationFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_create_user(self):
        """
        Валидная форма создает User.

        """
        users_count = User.objects.count()
        form_data = {
            "first_name": "new_first",
            "last_name": "new_last",
            "username": "new_user",
            "email": "new_email@gmail.com",
            "password1": "Pass123456",
            "password2": "Pass123456",
        }
        response = self.guest_client.post(
            reverse("users:signup"), data=form_data, follow=True
        )
        self.assertRedirects(response, reverse_lazy("posts:index"))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                first_name="new_first",
                last_name="new_last",
                username="new_user",
                email="new_email@gmail.com",
            ).exists()
        )
