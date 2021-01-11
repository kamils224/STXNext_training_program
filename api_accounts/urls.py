from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from api_accounts.views import UserRegistrationView

app_name = "api_accounts"

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
]

urlpatterns = format_suffix_patterns(urlpatterns)