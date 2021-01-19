from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse_lazy, reverse
from rest_framework import status

from api_projects.models import Project


User = get_user_model()

# NOTE: It's better option to create some test fixtures in future


class ProjectsTest(APITestCase):

    OBTAIN_TOKEN_URL = reverse_lazy("api_accounts:token_obtain_pair")

    PROJECT_LIST_URL = reverse_lazy("api_projects:project-list")
    PROJECT_DETAILS_URL = reverse_lazy("api_projects:project-detail")

    def _init_db(self) -> None:
        self.project_owner_1 = {
            "email": "project_owner1@example.com", "password": "password000"}
        self.project_owner_2 = {
            "email": "project_owner2@example.com", "password": "password999"}
        self.no_project_user = {
            "email": "no_project_user@example.com", "password": "passwordxxx"}
        self.member_1 = {"email": "member_owner1@example.com",
                         "password": "password111"}
        self.member_2 = {"email": "member_owner2@example.com",
                         "password": "password222"}
        self.member_3 = {"email": "member_owner3@example.com",
                         "password": "password333"}
        self.user_1 = User.objects.create_user(**self.project_owner_1)
        self.user_2 = User.objects.create_user(**self.project_owner_2)
        self.user_3 = User.objects.create_user(**self.no_project_user)

        members = []
        members.append(User.objects.create_user(**self.member_1))
        members.append(User.objects.create_user(**self.member_2))
        members.append(User.objects.create_user(**self.member_3))

        User.objects.all().update(is_active=True)

        project_1 = Project.objects.create(
            name="Project1 with members", owner=self.user_1)
        project_1.members.add(*members)

        Project.objects.create(
            name="Project1 without members", owner=self.user_1)
        Project.objects.create(name="Project2 empty", owner=self.user_2)

    def setUp(self):
        self._init_db()

    def _login_user(self, user: User) -> None:
        response = self.client.post(self.OBTAIN_TOKEN_URL, user, format="json")
        access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_get_projects_not_logged_in(self):
        response = self.client.get(self.PROJECT_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_projects(self):
        user = self.project_owner_1
        self._login_user(user)
        expected_count = Project.objects.filter(
            owner__email=user["email"]).count()

        response = self.client.get(self.PROJECT_LIST_URL)
        self.assertEqual(len(response.data), expected_count)

    def test_get_projects_as_member(self):
        user = self.member_1
        self._login_user(user)
        expected_count = Project.objects.filter(
            members__email=user["email"]).count()

        response = self.client.get(self.PROJECT_LIST_URL)
        self.assertEqual(len(response.data), expected_count)

    def test_get_projects_empty(self):
        self._login_user(self.no_project_user)
        expected_count = 0
        response = self.client.get(self.PROJECT_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), expected_count)

    def test_create_project(self):
        new_project = {"name": "New project"}
        response_bad = self.client.post(self.PROJECT_LIST_URL, new_project)

        user = self.no_project_user
        self._login_user(user)
        expected_count = Project.objects.filter(
            owner__email=user["email"]).count() + 1
        response_ok = self.client.post(self.PROJECT_LIST_URL, new_project)
        current_projects_count = Project.objects.filter(
            owner__email=user["email"]).count()

        self.assertEqual(response_bad.status_code,
                         status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_ok.status_code, status.HTTP_201_CREATED)
        self.assertEqual(current_projects_count, expected_count)

    def test_delete_project(self):
        user = self.project_owner_1
        project = Project.objects.filter(owner__email=user["email"]).first()
        projects_init_count = Project.objects.count()
        url = reverse("api_projects:project-detail", kwargs={"pk": project.pk})

        response_bad = self.client.delete(url)
        projects_count_non_auth_delete = Project.objects.count()

        self._login_user(user)
        response_ok = self.client.delete(url)
        projects_count_delete = Project.objects.count()

        self.assertEqual(projects_count_non_auth_delete, projects_init_count)
        self.assertEqual(response_bad.status_code,
                         status.HTTP_401_UNAUTHORIZED)

        self.assertEqual(projects_count_delete, projects_init_count - 1)
        self.assertEqual(response_ok.status_code,
                         status.HTTP_204_NO_CONTENT)

    def test_get_project_details(self):
        user_1 = self.project_owner_1
        user_2 = self.project_owner_2
        project = Project.objects.filter(owner__email=user_1["email"]).first()
        projects_init_count = Project.objects.count()
        url = reverse("api_projects:project-detail", kwargs={"pk": project.pk})

        self._login_user(user_1)
        response_ok = self.client.get(url)
        self._login_user(user_2)
        response_bad = self.client.get(url)

        self.assertEqual(response_ok.status_code,
                         status.HTTP_200_OK)
        self.assertEqual(response_bad.status_code,
                         status.HTTP_404_NOT_FOUND)

    def test_update_project(self):
        user_1 = self.project_owner_1
        user_2 = self.project_owner_2
        project = Project.objects.filter(owner__email=user_1["email"]).first()
        projects_init_count = Project.objects.count()
        url = reverse("api_projects:project-detail", kwargs={"pk": project.pk})

        new_name = "new name"
        self._login_user(user_1)
        response_ok = self.client.put(url, {"name": new_name})
        self._login_user(user_2)
        response_bad = self.client.put(url, {"name": new_name})

        self.assertEqual(response_ok.status_code,
                         status.HTTP_200_OK)
        self.assertEqual(response_ok.data["name"], new_name)
        self.assertEqual(response_bad.status_code,
                         status.HTTP_404_NOT_FOUND)
