from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api_projects.views import ProjectViewSet, IssueViewSet, IssueAttachment

app_name = "api_projects"

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"project", ProjectViewSet)
router.register(r"issue", IssueViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("", include(router.urls)),
    path("attachment/<int:pk>/", IssueAttachment.as_view(), "issue_attachment"),
]
