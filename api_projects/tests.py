from typing import Dict
from datetime import datetime

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse_lazy, reverse
from rest_framework import status

from api_projects.models import Project, Issue


User = get_user_model()


class ProjectsTest(APITestCase):

    OBTAIN_TOKEN_URL = reverse_lazy("api_accounts:token_obtain_pair")

    PROJECT_LIST = "api_projects:project-list"
    PROJECT_DETAILS = "api_projects:project-detail"

    def _init_db(self) -> None:
        # NOTE: It's better option to create some test fixtures in future

        self.owners = [
            {"email": "project_owner1@example.com", "password": "password000"},
            {"email": "project_owner2@example.com", "password": "password999"},
        ]
        self.no_project_users = [
            {"email": "no_project_user@example.com", "password": "passwordxxx"},
        ]
        self.members = [
            {"email": "member_owner1@example.com", "password": "password111"},
            {"email": "member_owner2@example.com", "password": "password222"},
            {"email": "member_owner3@example.com", "password": "password333"},
        ]
        self.users = [
            User.objects.create_user(**user)
            for user in self.owners + self.no_project_users
        ]

        members = [User.objects.create_user(
            **member) for member in self.members]

        User.objects.all().update(is_active=True)

        project_1 = Project.objects.create(
            name="Project1 with members", owner=self.users[0]
        )
        project_1.members.add(*members)

        Project.objects.create(
            name="Project1 without members", owner=self.users[0])
        Project.objects.create(name="Project2 empty", owner=self.users[1])

        example_date = datetime(2030, 10, 10, hour=12, minute=30)
        Issue.objects.create(
            title="Issue 1",
            description="Desc...",
            owner=members[0],
            project=project_1,
            due_date=example_date,
        )

    def setUp(self):
        self._init_db()

    def _login_user(self, user: Dict[str, str]) -> None:
        response = self.client.post(self.OBTAIN_TOKEN_URL, user, format="json")
        access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_get_projects(self):
        url = reverse(self.PROJECT_LIST)
        # anonymous user
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged in as owner
        user = self.owners[0]
        self._login_user(user)
        expected_count = Project.objects.filter(
            owner__email=user["email"]).count()

        response = self.client.get(url)
        self.assertEqual(len(response.data), expected_count)

        # logged in as member
        user = self.members[0]
        self._login_user(user)
        expected_count = Project.objects.filter(
            members__email=user["email"]).count()

        response = self.client.get(url)
        self.assertEqual(len(response.data), expected_count)

        # logged in as user without projects
        self._login_user(self.no_project_users[0])
        expected_count = 0
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), expected_count)

    def test_get_project_details(self):
        user_1 = self.owners[0]
        user_2 = self.owners[1]
        project = Project.objects.filter(owner__email=user_1["email"]).first()
        projects_init_count = Project.objects.count()
        url = reverse(self.PROJECT_DETAILS, kwargs={"pk": project.pk})

        self._login_user(user_1)
        response_ok = self.client.get(url)
        self._login_user(user_2)
        response_bad = self.client.get(url)

        self.assertEqual(response_ok.status_code, status.HTTP_200_OK)
        self.assertEqual(response_bad.status_code, status.HTTP_404_NOT_FOUND)

        issues_count = Issue.objects.filter(project=project).count()
        response_issues = response_ok.data["issues"]
        self.assertEqual(len(response_issues), issues_count)

    def test_create_project(self):
        url = reverse(self.PROJECT_LIST)
        new_project = {"name": "New project"}
        response_bad = self.client.post(url, new_project)

        user = self.no_project_users[0]
        self._login_user(user)
        expected_count = Project.objects.filter(
            owner__email=user["email"]).count() + 1
        response_ok = self.client.post(url, new_project)
        current_projects_count = Project.objects.filter(
            owner__email=user["email"]
        ).count()

        self.assertEqual(response_bad.status_code,
                         status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_ok.status_code, status.HTTP_201_CREATED)
        self.assertEqual(current_projects_count, expected_count)

    def test_update_project(self):
        user_1 = self.owners[0]
        user_2 = self.owners[1]
        project = Project.objects.filter(owner__email=user_1["email"]).first()
        projects_init_count = Project.objects.count()
        url = reverse(self.PROJECT_DETAILS, kwargs={"pk": project.pk})

        new_name = "new name"
        self._login_user(user_1)
        response_ok = self.client.put(url, {"name": new_name})
        self._login_user(user_2)
        response_bad = self.client.put(url, {"name": new_name})

        self.assertEqual(response_ok.status_code, status.HTTP_200_OK)
        self.assertEqual(response_ok.data["name"], new_name)
        self.assertEqual(response_bad.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_project(self):
        user = self.owners[0]
        project = Project.objects.filter(owner__email=user["email"]).first()
        projects_init_count = Project.objects.count()
        url = reverse(self.PROJECT_DETAILS, kwargs={"pk": project.pk})

        response_bad = self.client.delete(url)
        projects_count_non_auth_delete = Project.objects.count()

        self._login_user(user)
        response_ok = self.client.delete(url)
        print(response_ok)
        #projects_count_delete = Project.objects.count()

        # self.assertEqual(projects_count_non_auth_delete, projects_init_count)
        # self.assertEqual(response_bad.status_code,
        #                  status.HTTP_401_UNAUTHORIZED)

        # self.assertEqual(projects_count_delete, projects_init_count - 1)
        # self.assertEqual(response_ok.status_code, status.HTTP_204_NO_CONTENT)
