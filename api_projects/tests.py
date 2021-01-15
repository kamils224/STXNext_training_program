from rest_framework.test import APITestCase

from api_projects.models import Project
from api_accounts.models import User


# TODO
class UserProjectsTest(APITestCase):

    def setUp(self):
        user = User.objects.create_user(email="project_owner@example.com",
                                        password="password123")
        user.is_active = True
        user.save()
