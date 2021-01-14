from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api_projects.views import ProjectViewSet, IssueViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"projects", ProjectViewSet)
router.register(r"issue", IssueViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
