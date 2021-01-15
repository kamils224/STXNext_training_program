from typing import Dict

from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase
from rest_framework.response import Response


User = get_user_model()


class UserAccountTest(APITestCase):

    REGISTER_URL = reverse_lazy("api_accounts:register")
    OBTAIN_TOKEN_URL = reverse_lazy("api_accounts:token_obtain_pair")
    USER_DETAILS_URL = reverse_lazy("api_accounts:user_details")

    def setUp(self):

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
        response = self._user_data_post(self.user_data, self.REGISTER_URL)
        expected_obj_count = 1

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), expected_obj_count)
        self.assertEqual(User.objects.get().email, self.user_data["email"])

        # try to create the same user again
        response = self._user_data_post(self.user_data, self.REGISTER_URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), expected_obj_count)

        # there should be a new message
        self.assertEqual(len(mail.outbox), expected_obj_count)

    def test_short_password(self):
        expected_users_count = User.objects.count()
        user_data = self.user_data
        user_data["password"] = "123"
        response = self._user_data_post(user_data, self.REGISTER_URL)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), expected_users_count)

    def test_bad_email_register(self):
        expected_users_count = User.objects.count()
        response = self._user_data_post(self.bad_email_data, self.REGISTER_URL)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), expected_users_count)

    def test_login(self):
        self._user_data_post(self.user_data, self.REGISTER_URL)
        # set user as active
        user = User.objects.first()
        user.is_active = True
        user.save()
        response = self._user_data_post(self.user_data, self.OBTAIN_TOKEN_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            "access" in response.data and "refresh" in response.data)

    def test_login_inactive(self):
        self._user_data_post(self.user_data, self.REGISTER_URL)
        response = self._user_data_post(self.user_data, self.OBTAIN_TOKEN_URL)

        # user should be inactive after registration
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_details(self):
        self._user_data_post(self.user_data, self.REGISTER_URL)
        # set user as active
        user = User.objects.first()
        user.is_active = True
        user.save()

        response = self._user_data_post(self.user_data, self.OBTAIN_TOKEN_URL)
        access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(self.USER_DETAILS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], user.email)

    def test_user_details_fail(self):
        response = self.client.get(self.USER_DETAILS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
