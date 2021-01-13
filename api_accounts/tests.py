from typing import Dict

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


User = get_user_model()


class UserAccountTest(APITestCase):
    def setUp(self):
        self.user_data = {
            "email": "user@example.com",
            "password": "password123",
        }
        self.bad_email_data = {
            "email": "bad_email.com",
            "password": "password123",
        }

    def _post_register(self, user_data: Dict[str, str]) -> None:
        url = reverse("api_accounts:register")
        return self.client.post(url, user_data, format="json")

    def test_register(self):
        response = self._post_register(self.user_data)
        expected_users_count = 1

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), expected_users_count)
        self.assertEqual(User.objects.get().email, self.user_data["email"])

        # try to create the same user again
        response = self._post_register(self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), expected_users_count)

    def test_short_password(self):
        user_data = self.user_data
        user_data["password"] = "123"
        response = self._post_register(user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_bad_email_register(self):
        response = self._post_register(self.bad_email_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
