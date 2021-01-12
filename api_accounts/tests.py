from typing import Dict

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework.response import Response

User = get_user_model()


class UserAccountTest(APITestCase):
    def setUp(self):
        self.register_url = reverse("api_accounts:register")
        self.obtain_token_url = reverse("api_accounts:token_obtain_pair")

        self.user_data = {
            "email": "user@example.com",
            "password": "password123",
        }
        self.bad_email_data = {
            "email": "bad_email.com",
            "password": "password123",
        }

    def _user_data_post(self, user_data: Dict[str, str], url: str) -> Response:
        return self.client.post(url, user_data, format="json")

    def test_register(self):
        response = self._user_data_post(self.user_data, self.register_url)
        expected_users_count = 1

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), expected_users_count)
        self.assertEqual(User.objects.get().email, self.user_data["email"])

        # try to create the same user again
        response = self._user_data_post(self.user_data, self.register_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), expected_users_count)

    def test_short_password(self):
        user_data = self.user_data
        user_data["password"] = "123"
        response = self._user_data_post(user_data, self.register_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_bad_email_register(self):
        response = self._user_data_post(self.bad_email_data, self.register_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_login(self):
        _ = self._user_data_post(self.user_data, self.register_url)
        # set user as active
        user = User.objects.first()
        user.is_active = True
        user.save()
        response = self._user_data_post(self.user_data, self.obtain_token_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            "access" in response.data and "refresh" in response.data)

    def test_login_inactive(self):
        _ = self._user_data_post(self.user_data, self.register_url)
        response = self._user_data_post(self.user_data, self.obtain_token_url)

        # user should be inactive after registration
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
