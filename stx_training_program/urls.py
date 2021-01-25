"""stx_training_program URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from graphene_file_upload.django import FileUploadGraphQLView

from stx_training_program.schema import schema

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-accounts/", include("api_accounts.urls")),
    path("api-projects/", include("api_projects.urls")),
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {
            "document_root": settings.MEDIA_ROOT,
        },
    ),
    path(r"graphql/", csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),
    path(r"graphql-file/", FileUploadGraphQLView.as_view(graphiql=True)),
]
